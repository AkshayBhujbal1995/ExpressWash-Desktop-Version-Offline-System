# 🧺 Express Wash - Smart Laundry Offline Billing System 

> **A professional, multi-interface laundry business management solution designed for local development and demonstration.**

[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.1-red.svg)](https://streamlit.io/)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-yellow.svg)](https://docs.python.org/3/library/tkinter.html)

## 🎯 Project Overview

**Express Wash** is a comprehensive laundry billing and business management system designed to modernize small laundry businesses. This project demonstrates full-stack development capabilities with **three different UI implementations**, all configured to run on your local machine:

1.  **🌐 React Web Application** - A modern, responsive web app with 3D animations.
2.  **🖥️ Tkinter Desktop Application** - A professional desktop GUI.
3.  **📱 Streamlit Web Application** - A data science-focused web interface.

## ✨ Key Features

### 🛠️ **Complete CRUD Operations**
- ✅ **Create** new customer orders.
- ✅ **Read** order history with advanced filtering.
- ✅ **Update** existing orders with real-time calculation.
- ✅ **Delete** orders with confirmation.
- ✅ **Search & Filter** by customer name, date, and amount.

### 📊 **Business Analytics**
- 📈 Revenue trends and charts.
- 👥 Customer analysis.
- 🧺 Service breakdown.
- 📅 Daily/monthly reports.
- 💰 Financial insights.

### 🎨 **Modern UI/UX**
- 🌟 **3D Animations** (React version).
- 🎭 **Glass Morphism** design.
- 📱 **Responsive** layouts for web versions.
- 🎨 **Professional** styling.
- ⚡ **Smooth** animations and transitions.

### 💾 **Data Management**
- 🗄️ **MySQL Database** integration for persistent storage.
- 📄 **CSV & Excel Export** functionality.
- 🔄 **Real-time** data synchronization across the application.

## 🏗️ Project Structure

The project is organized into distinct folders for each UI implementation.

```
Express Wash/
├── 🌐 React Web App (Modern UI + 3D)
│   ├── src/
│   ├── public/
│   └── package.json       # Dependencies
│
├── 🖥️ Tkinter Desktop App (Professional GUI)
│   ├── tkinter_app.py     # Main desktop application
│   └── requirements.txt   # Python dependencies
│
├── 📱 Streamlit Web App (Data Science UI)
│   ├── app.py            # Main Streamlit application
│   └── requirements.txt  # Python dependencies
│
└── 📚 Documentation
    └── README.md         # This file
```

## 🚀 Getting Started (Localhost Setup)

Follow these steps to get all three versions of the application running on your computer.

### Prerequisites
- **Python 3.8+** installed.
- **Node.js 16+** installed (for the React version).
- **MySQL Server 8.0+** installed and **running** (e.g., via XAMPP, WAMP, or a direct installation).

### Step 1: Database Setup (Crucial First Step)
1.  **Start your MySQL Server.**
2.  Open a MySQL client (like MySQL Workbench or a command line) and run the following command to create the database:
    ```sql
    CREATE DATABASE IF NOT EXISTS express_wash;
    ```
3.  **Update Database Passwords:** Open the following files and update the `password` in the `DB_CONFIG` dictionary to match your MySQL root password:
    - `Tkinter Desktop App/tkinter_app.py`
    - `Streamlit Web App/app.py`
    - (If applicable, check the connection settings in your React app's backend code).

### Step 2: Running the Applications

Open a new terminal for each application you want to run.

#### 🌐 **React Web Application (Recommended)**
```bash
# Navigate to the React app folder
cd "React Web App"

# Install dependencies
npm install

# Start the development server
npm start

# Open http://localhost:3000 in your browser
```

#### 🖥️ **Tkinter Desktop Application**
```bash
# Navigate to the Tkinter app folder
cd "Tkinter Desktop App"

# Install Python dependencies
pip install -r requirements.txt

# Run the desktop application
python tkinter_app.py
```

#### 📱 **Streamlit Web Application**
```bash
# Navigate to the Streamlit app folder
cd "Streamlit Web App"

# Install Python dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py

# Open the URL provided in the terminal (usually http://localhost:8501)
```

## 🛠️ Technology Stack

### Frontend Technologies
- **React 18** - Modern web framework
- **Framer Motion** & **Three.js** - Animations and 3D graphics
- **Tailwind CSS** - Utility-first CSS
- **Tkinter** - Native Python GUI framework
- **Streamlit** - Data science web framework

### Backend Technologies
- **Python 3.8+** - Core programming language
- **MySQL 8.0** - Relational database
- **Pandas** & **Plotly** - Data manipulation and charting
- **Express.js** - Node.js backend (if used with the React version)

## 📊 Database Schema

The `orders` table will be created automatically by the Python applications on their first run.

```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(20),
    order_date DATE NOT NULL,
    regular_clothes_kg DECIMAL(5,2) DEFAULT 0,
    blankets_kg DECIMAL(5,2) DEFAULT 0,
    white_clothes_pieces INT DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Business Impact

- ⚡ **Accelerates** order processing and billing.
- 📊 **Provides** real-time business insights on your local dashboard.
- 💰 **Ensures** accurate and consistent billing calculations.
- 📈 **Enables** data-driven decision-making for a small business.

## 👨‍💻 Author

**Akshay Bhujbal**
- **LinkedIn:** [akshay-1995-bhujbal](https://www.linkedin.com/in/akshay-1995-bhujbal/)
- **GitHub:** [AkshayBhujbal1995](https://github.com/AkshayBhujbal1995)
- **Portfolio:** [Akshay Bhujbal Portfolio](https://akshaybhujbal1995.github.io/Portfolio-Website/)

## 📞 Support

For questions or issues running the project locally, please email akshay.bhujbal16@gmail.com.

---

<div align="center">

**Made with ❤️ for the laundry business community**

</div>
