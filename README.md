## 🚀 Built with Passion by
# **V Sree Kirthana**

# 📋 User Registration System
**Secure. Validated. Persistent.**

A full-stack user registration web application built with Node.js and Express on the backend, connected to a live MySQL database — with real-time client-side validation and secure parameterized queries.

---

## 📂 Project Structure

* **`server.js`**: The main entry point; manages the Express server, API routes, MySQL connection pool, and server-side validation logic.
* **`public/`**: The frontend layer; contains the HTML registration form, CSS styles, and client-side JavaScript for real-time input validation.
* **`.env`**: Stores sensitive database credentials securely (host, user, password, database name) — never committed to version control.
* **`package.json`**: Project metadata and dependency definitions.

---
## 📂 Folder Structure

```text
cognifyz-task-2/
├── public/                 # Frontend (HTML, CSS, JS)
├── .env                    # Environment variables (DB credentials)
├── .gitignore              # Ignores node_modules and .env
├── package.json            # Project dependencies
├── package-lock.json       # Locked dependency tree
└── server.js               # Express backend + MySQL integration
```
---

## 🛠 Tech Stack

* **Runtime:** Node.js
* **Framework:** Express.js
* **Database:** MySQL (via mysql2)
* **Security:** dotenv (credential management), Parameterized queries (SQL injection prevention)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript

---

## ⚙️ Features

* ✅ Client-side real-time form validation
* ✅ Server-side validation (username, email, age, password rules)
* ✅ Secure MySQL database integration via connection pooling
* ✅ Environment variable management with dotenv
* ✅ SQL injection prevention via parameterized queries
* ✅ RESTful POST `/submit` route for user registration

---

## 🚀 Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/sreekirthana123/cognifyz-task-2.git
cd cognifyz-task-2

# 2. Install dependencies
npm install

# 3. Set up your .env file
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=task5_test_db
PORT=3000

# 4. Run the server
node server.js
```

Then open `http://localhost:3000` in your browser.

---

## 📬 Connect & Share Feedback

I'd love to hear your thoughts! Whether it's a feature suggestion, a bug report, or general feedback — your input helps make this project better.

* *Connect with me:* [My LinkedIn Profile](https://www.linkedin.com/in/v-sree-kirthana-565b4a367?utm_source=share_via&utm_content=profile&utm_medium=member_android)
* *Share Feedback:* [Create a GitHub Issue](https://github.com/sreekirthana123/cognifyz-task-2/issues/new)

---

## 📜 License

© 2026 V. Sree Kirthana. All rights reserved.  
This project was developed as part of the Cognifyz Technologies Internship Program.  
Unauthorized reproduction or distribution is not permitted without explicit consent from the author.

---

*Built by V Sree Kirthana*
