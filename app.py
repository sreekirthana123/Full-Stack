import re
import socket
import streamlit as st
import mysql.connector
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="My Fullstack App", layout="centered")

# 2. Database Connection
@st.cache_resource(ttl=300)
def _init_db_connection():
    ipv4_host = socket.gethostbyname(st.secrets["DB_HOST"])
    return mysql.connector.connect(
        host=ipv4_host,
        port=int(st.secrets["DB_PORT"]),
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )

def get_db_connection():
    conn = _init_db_connection()
    try:
        conn.ping(reconnect=True, attempts=3, delay=2)
    except mysql.connector.Error:
        st.cache_resource.clear()
        conn = _init_db_connection()
        conn.ping(reconnect=True)
    return conn

# 3. Data Functions
@st.cache_data(ttl=60)
def get_all_users():
    conn = get_db_connection()
    query = "SELECT id, username, email, age, created_at FROM users"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def insert_user(username: str, email: str, age: int, password: str) -> None:
    conn = get_db_connection()
    sql = "INSERT INTO users (username, email, age, password) VALUES (%s, %s, %s, %s)"
    values = (username, email, age, password)
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()

def check_password_strength(password):
    if len(password) < 8:
        return "Weak", "🔴"
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    score = sum([has_upper, has_lower, has_digit, has_special])
    if score <= 2:
        return "Weak", "🔴"
    elif score == 3:
        return "Medium", "🟡"
    else:
        return "Strong", "🟢"

# 4. UI
st.title("Welcome to my App")
st.subheader("Register New User")

# Fields in correct order
username = st.text_input("Username", key="username_input")
email = st.text_input("Email", key="email_input")

# Password after email with strength indicator
password = st.text_input("Password", type="password", key="password_input")
if password:
    strength, emoji = check_password_strength(password)
    if strength == "Weak":
        st.error(f"{emoji} Weak — add uppercase, numbers, and symbols")
    elif strength == "Medium":
        st.warning(f"{emoji} Medium — almost there!")
    else:
        st.success(f"{emoji} Strong password!")

age = st.number_input("Age", min_value=18, max_value=99, step=1, key="age_input")

if st.button("Submit"):
    username = st.session_state.get("username_input", "")
    email = st.session_state.get("email_input", "")
    password = st.session_state.get("password_input", "")
    age = st.session_state.get("age_input", 18)

    if not username or len(username) < 3:
        st.error("Username must be at least 3 characters long.")
    elif "@" not in email:
        st.error("Please enter a valid email address.")
    elif not password or len(password) < 8:
        st.error("Password must be at least 8 characters long.")
    else:
        try:
            insert_user(username=username, email=email, age=int(age), password=password)
            get_all_users.clear()
            st.success(f"User {username} registered successfully!")
            # Clear all fields after successful submission
            for key in ["username_input", "email_input", "password_input", "age_input"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        except Exception as e:
            st.error(f"Registration failed: {e}")

# 5. Dashboard
st.subheader("Registered Users")
if st.button("Refresh User List"):
    st.rerun()

users_df = get_all_users()
st.dataframe(users_df)