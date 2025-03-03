# 🔍 Anomaly Detection System for Electric Energy Consumption

## 📌 Project Overview
This project is an **AI-powered anomaly detection system** that monitors electric energy consumption in smart farms. It uses **Flask, Python, and Machine Learning** to detect unusual power usage and send alerts in real-time.

The system can:
✅ Collect and store real-time power usage data  
✅ Detect anomalies using an **ML model (Isolation Forest)**  
✅ Send **email alerts** to the admin for detected anomalies  
✅ Visualize **historical data** with charts  
✅ Provide **real-time monitoring** using **WebSocket**  

---

## 🚀 Features
✔ **Real-time Power Monitoring** (via WebSocket)  
✔ **ML-Based Anomaly Detection** (Isolation Forest)  
✔ **Email Alerts for Anomalies** (with cooldown)  
✔ **Historical Data Visualization** (Chart.js)  
✔ **Export Anomalies as CSV**  
✔ **Secure Login & Admin Panel**  

---

## ⚙️ Installation & Setup

### **🔹 1. Clone the Repository**
```sh
git clone https://github.com/your-repo/anomaly-detection.git
cd anomaly-detection
```

### **🔹 2. Install Dependencies**
```sh
pip install -r requirements.txt
```

### **🔹 3. Set Up Environment Variables (`.env`)**
Create a **`.env`** file and add:
```sh
SECRET_KEY=your_secret_key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
ADMIN_EMAIL=admin@example.com
```

### **🔹 4. Set Up Database**
```sh
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### **🔹 5. Train the ML Model**
```sh
python train_model.py
python train_forecast.py
```

### **🔹 6. Run the Flask Application**
```sh
python app.py
```
The server will start at **`http://127.0.0.1:5000`** 🚀

---

## 📌 Usage Guide
### **🔹 1. Register & Login**
- Visit `http://127.0.0.1:5000/register`
- Log in at `http://127.0.0.1:5000/login`
- You will be redirected to the dashboard

### **🔹 2. Real-time Monitoring**
- Navigate to **`http://127.0.0.1:5000/real-time-monitoring`**
- View **live power usage updates** & anomaly alerts.

### **🔹 3. View Anomalies**
- Go to `http://127.0.0.1:5000/anomalies`
- Filter data by **date range**
- **Download anomalies as CSV**

### **🔹 4. Forecast Future Energy Consumption**
- Visit **`http://127.0.0.1:5000/forecast`** to see **24-hour energy predictions**.

---

## 🔗 API Endpoints

| **Endpoint**             | **Method** | **Description** |
|--------------------------|------------|----------------|
| `/register`             | `POST`     | Register a new user |
| `/login`                | `POST`     | Authenticate user |
| `/real-time-monitoring` | `GET`      | Live power usage updates |
| `/historical_data`      | `GET`      | Fetch past 50 readings |
| `/detect`               | `POST`     | Detect anomalies from input |
| `/anomalies`            | `GET`      | View detected anomalies |
| `/forecast`             | `GET`      | Predict energy consumption for next 24 hours |
| `/export_anomalies`     | `GET`      | Download anomalies as CSV |

---

## 🛠️ Technology Stack

**Backend**:  
- Python Flask  
- Flask-SQLAlchemy  
- Flask-SocketIO (for real-time data)  
- Flask-Mail (for email alerts)  

**Frontend**:  
- HTML5, CSS3 (Tailwind CSS)  
- JavaScript (Chart.js for data visualization)  

**Machine Learning**:  
- **Scikit-Learn** (Isolation Forest)  
- Pandas, NumPy  

**Database**:  
- SQLite (Can be replaced with PostgreSQL/MySQL)  

---

## 🔥 Future Enhancements
🚀 Add **SMS Alerts** using Twilio  
🚀 Deploy on **AWS/GCP**  
🚀 Add **User Roles (Admin, User, Guest)**  
🚀 Improve **AI Model with Deep Learning (LSTMs)**  
🚀 Implement **Energy Consumption Optimization Recommendations**  

---

## 🙌 Contributors
👤 **Madhu Parvathaneni** - [GitHub Profile](https://github.com/maddydevgits)  

---
🚀 **Now, you're ready to run and test your anomaly detection system!**  
Would you like to **deploy this project on a cloud server (AWS/Heroku)?** 🌐🚀

