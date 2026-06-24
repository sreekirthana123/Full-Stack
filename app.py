import socket
import streamlit as st
import mysql.connector
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="My Fullstack App", layout="centered")

# 2. Database Connection (Using Secrets for security)
@st.cache_resource
def get_db_connection():
    # Force Streamlit to resolve the Aiven hostname to an IPv4 address to avoid Error 99
    ipv4_host = socket.gethostbyname(st.secrets["DB_HOST"])

    return mysql.connector.connect(
        host=ipv4_host,
        port=int(st.secrets["DB_PORT"]),  # Wrapping in int() just to be perfectly safe!
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )

# 3. UI: Simple Header
st.title("Welcome to my App")


def insert_user(username: str, email: str, age: int, password: str) -> None:
    conn = get_db_connection()
    sql = "INSERT INTO users (username, email, age, password) VALUES (?, ?, ?, ?)"
    # mysql.connector supports %s placeholders; keep params ordered.
    # Convert to correct placeholder style if needed.
    # NOTE: MySQL uses %s; use a compatible query format.
    sql = "INSERT INTO users (username, email, age, password) VALUES (%s, %s, %s, %s)"
    values = (username, email, age, password)
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()


# --- UI: CREATE (Registration) ---
st.subheader("Register New User")
with st.form("registration_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    age = st.number_input("Age", min_value=18, max_value=99, step=1)
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Submit")

if submit:
    if not username or len(username) < 3:
        st.error("Username must be at least 3 characters long.")
    elif "@" not in email:
        st.error("Please enter a valid email address.")
    elif password is None or len(password) < 8:
        st.error("Password must be at least 8 characters long.")
    else:
        try:
            insert_user(username=username, email=email, age=int(age), password=password)
            # Clear cached dashboard data
            get_all_users.clear()
            st.success(f"User {username} registered successfully!")
        except Exception as e:
            st.error(f"Registration failed: {e}")


# Function to get all users
@st.cache_data(ttl=60)
def get_all_users():
    conn = get_db_connection()
    query = "SELECT id, username, email, age, created_at FROM users"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# UI: Dashboard (READ)
st.subheader("Registered Users")
if st.button("Refresh User List"):
    st.rerun()

users_df = get_all_users()
st.dataframe(users_df)


