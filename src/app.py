from flask import Flask, render_template, request, redirect, url_for, jsonify, flash,Response,session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime  # Import datetime
from flask_mail import Mail, Message
from flask_socketio import SocketIO
import random
import time
from threading import Thread,Lock
import matplotlib
import csv
matplotlib.use('Agg')  # Fix Matplotlib error
from gevent import monkey

monkey.patch_all()
admin="parvathanenimadhu@gmail.com"

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load ML Model
model = joblib.load("isolation_forest.pkl")
forecast_model = joblib.load("forecast_model.pkl")

# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Anomaly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100), nullable=False)
    power_usage = db.Column(db.Float, nullable=False)
    anomaly = db.Column(db.Boolean, default=False)

class RealTimeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    power_usage = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "power_usage": self.power_usage}

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "makeskilledtest@gmail.com"
app.config["MAIL_PASSWORD"] = "mqqk slyn vvix uxwu"

last_alert_time = 0  
ALERT_COOLDOWN = 300

mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

alert_lock = Lock()  # Create a lock for thread safety

def send_email_alert(power_usage):
    # Fetch logged-in user's email from session
    user_email = session.get("user_email")  # Assuming you store email in session
    
    if not user_email:
        print("❌ No logged-in user found, email not sent.")
        return

    msg = Message("Anomaly Detected!", sender="your-email@gmail.com", recipients=[user_email])
    msg.body = f"Anomaly detected with power usage: {power_usage} kWh"

    try:
        mail.send(msg)
        print(f"✅ Email sent to {user_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")

def send_email_alert_admin(power_usage):
    """Send email alert to admin with cooldown and thread safety."""
    global last_alert_time  

    with alert_lock:  # Ensure only one thread runs this block at a time
        current_time = time.time()
        time_since_last_alert = current_time - last_alert_time

        if time_since_last_alert >= ALERT_COOLDOWN:
            msg = Message("Anomaly Detected!", sender="your-email@gmail.com", recipients=[admin])
            msg.body = f"⚠️ Anomaly detected with power usage: {power_usage} kWh"

            try:
                mail.send(msg)
                last_alert_time = time.time()  # ✅ Update last alert time after success
                print(f"📧 Email sent to admin")
            except Exception as e:
                print(f"❌ Failed to send email: {str(e)}")
        else:
            print(f"⏳ Cooldown active: Email alert not sent. Wait {ALERT_COOLDOWN - time_since_last_alert:.2f} seconds.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🚀 Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

# 🔑 Login Route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            session["user_id"] = user.id
            session["user_email"] = user.email
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("index.html")

@app.route('/anomalie')
@login_required
def anomalie():
    return render_template('anomalie.html')

# 🏠 Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    # Fetch anomalies from the database
    anomalies = Anomaly.query.all()

    # Extract timestamps and power usage for visualization
    timestamps = [a.timestamp for a in anomalies]
    power_usage = [a.power_usage for a in anomalies]

    # Generate a plot if there is data
    plot_url = None
    if timestamps and power_usage:
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, power_usage, marker='o', linestyle='-', color='blue', label="Power Usage")
        plt.xlabel("Time")
        plt.ylabel("Power Usage (kWh)")
        plt.title("Energy Consumption Over Time")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Convert plot to a PNG image
        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

    # Render the dashboard with anomalies and plot
    return render_template("dashboard.html", anomalies=anomalies, plot_url=plot_url)


# 🚨 Detect Anomaly
@app.route("/detect", methods=["POST"])
def detect():
    data = request.json
    power_usage = data.get("power_usage")

    # Convert input to float
    try:
        power_usage = float(power_usage)
    except ValueError:
        return jsonify({"error": "Invalid power usage input"}), 400

    # Fix IsolationForest Warning: Pass DataFrame with column name
    prediction = model.predict(pd.DataFrame([[power_usage]], columns=["power_usage"]))
    anomaly_detected = prediction[0] == -1

    if anomaly_detected:
        send_email_alert(power_usage)

    # Convert timestamp to string format for SQLite
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Store in database
    new_entry = Anomaly(timestamp=timestamp, power_usage=power_usage, anomaly=anomaly_detected)
    db.session.add(new_entry)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "Anomalous" if anomaly_detected else "Normal"})


# 📊 Visualize Data
@app.route("/plot")
@login_required
def plot():
    data = Anomaly.query.all()
    timestamps = [a.timestamp for a in data]
    power_usage = [a.power_usage for a in data]
    
    plt.figure(figsize=(10,5))
    plt.plot(timestamps, power_usage, label="Power Usage")
    plt.xlabel("Time")
    plt.ylabel("Power Usage (kWh)")
    plt.title("Energy Consumption Over Time")
    plt.legend()
    
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    return render_template("dashboard.html", plot_url=plot_url)

# 🚪 Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/anomalies", methods=["GET", "POST"])
@login_required
def anomalies():
    query = Anomaly.query
    
    if request.method == "POST":
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if start_date and end_date:
            query = query.filter(Anomaly.timestamp.between(start_date, end_date))

    anomalies_data = query.all()
    return render_template("anomalies.html", anomalies=anomalies_data)

@app.route("/export_anomalies")
@login_required
def export_anomalies():
    anomalies = Anomaly.query.all()

    def generate():
        yield "Timestamp,Power Usage,Anomaly\n"
        for anomaly in anomalies:
            yield f"{anomaly.timestamp},{anomaly.power_usage},{'Yes' if anomaly.anomaly else 'No'}\n"

    return Response(generate(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=anomalies.csv"})

@app.route("/forecast", methods=["GET"])
@login_required
def forecast_page():
    return render_template("forecast.html")

@app.route("/get_forecast", methods=["GET"])
@login_required
def get_forecast():
    steps = 24  # Predict next 24 hours
    forecast_values = forecast_model.forecast(steps=steps)
    
    future_timestamps = pd.date_range(pd.Timestamp.now(), periods=steps, freq="H")
    
    forecast_data = [{"timestamp": str(future_timestamps[i]), "predicted_usage": round(forecast_values[i], 2)}
                     for i in range(steps)]
    
    return jsonify(forecast_data)

@app.route("/real-time-monitoring")
@login_required
def real_time_monitoring():
    return render_template("real_time_monitoring.html")

@app.route("/historical_data")
def historical_data():
    data = RealTimeData.query.order_by(RealTimeData.timestamp.desc()).limit(50).all()
    return jsonify([entry.to_dict() for entry in data])

@app.route("/historical_data_page")
def historical_data_page():
    return render_template("historical_data.html")


def generate_real_time_data():
    """Simulates real-time power usage updates, detects anomalies, and sends alerts."""
    with app.app_context():  # Ensure Flask session is accessible
        while True:
            power_usage = round(random.uniform(300, 700), 2)
            timestamp = datetime.now()

            # Emit real-time data
            socketio.emit("real_time_data", {"power_usage": power_usage})

            # Save real-time data to database
            new_data = RealTimeData(timestamp=timestamp, power_usage=power_usage)
            db.session.add(new_data)
            db.session.commit()

            # ML Model Prediction
            prediction = model.predict(pd.DataFrame([[power_usage]], columns=["power_usage"]))
            anomaly_detected = prediction[0] == -1
            
            if anomaly_detected:
                send_email_alert_admin(power_usage)  # Now works correctly

            # Convert timestamp to string format for SQLite
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Store anomaly in database
            new_entry = Anomaly(timestamp=timestamp, power_usage=power_usage, anomaly=anomaly_detected)
            db.session.add(new_entry)
            db.session.commit()

            time.sleep(5)  # Update every 5 seconds

# Start the thread in Flask's app context
thread = Thread(target=lambda: generate_real_time_data())
thread.daemon = True
thread.start()


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()  # Ensure all tables are created

    # app.run(debug=True, host="0.0.0.0", port=5001)
    socketio.run(app, host="0.0.0.0", port=5001)
    # socketio.run(app, cors_allowed_origins="*", async_mode="threading", logger=True, engineio_logger=True)

