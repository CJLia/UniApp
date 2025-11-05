# 🎓 University Enrolment System (UniApp)

> **A Tkinter-based University Management Application** that allows students and administrators to manage enrolments, marks, grades, and academic reports — all in one interactive system.

---

## 🧾 Overview

The **University Enrolment System** simulates an academic environment with a graphical interface for both **Students** and **Admins**.

- 🧑‍🎓 **Students** can register, enrol or drop subjects, and view their marks and grades.
- 🧑‍🏫 **Admins** can manage subjects, set marks, and generate analytical reports like Pass/Fail and Grade Distribution.

This project demonstrates **Object-Oriented Programming (OOP)**, **Model–View–Controller (MVC)** architecture, and **data persistence** using Python.

---

## 🧑‍💻 Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend (GUI)** | Python `tkinter`, `ttk` widgets |
| **Backend Logic** | Python OOP — Controllers, Services, and Models |
| **Data Storage** | Custom `DataStore` using Python `pickle` |
| **Reporting** | `ReportingService` (Pass/Fail + Grade Grouping) |
| **Security** | Password hashing with `SHA-256` + custom salt |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/CJLia/UniApp.git
cd UniApp


2️⃣ Run the Application

python3 src/app/gui_app.py

3️⃣ Default Admin Login

ID: admin001
Password: Admin123

4️⃣ Data File Location

All persistent data (users, subjects, enrolments) is stored in:

data/university_data.dat


🌟 Core Features
👨‍🎓 Student Features

- Register and log in securely
- View all available subjects
- Enrol or drop subjects dynamically
- Change password (with strong validation)
- View marks and auto-generated grades

🧑‍🏫 Admin Features

- Add and remove subjects
- View all registered students
- Set student marks (grades auto-calculated)
- Generate Pass/Fail Report and Grade Report
- Clear all student data (with confirmation warnings)

🧩 Example Workflow

- Admin adds new subject → Manage Subjects → Add Subject
- Student logs in → Available Subjects → Enrol
- Admin sets marks → Auto grade assigned via GradePolicy
- Admin generates reports → View Pass/Fail or Grade Report

📈 Future Enhancements

🔹 Switch to SQLite for structured data persistence
🔹 Export reports to CSV or PDF format
🔹 Add dark/light theme toggle
🔹 Integrate REST API endpoints for future web interface

⚡ Reset Application (Start Fresh)

If you need to clear all stored data:

rm data/university_data.dat
python3 src/app/gui_app.py