import socket
import streamlit as st
import mysql.connector
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="My Fullstack App", layout="centered")

# 2. Database Connection (Using Secrets for security)
# 1. Cache the heavy lifting of logging in
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

# 2. Call THIS function in the rest of your app
def get_db_connection():
    conn = _init_db_connection()

    # 3. The ping happens here, outside the cache!
    # It will wake up Aiven every single time you ask for the database.
    try:
        conn.ping(reconnect=True, attempts=3, delay=2)
    except mysql.connector.Error:
        # If it fully died, forcefully clear Streamlit's cache and retry
        st.cache_resource.clear()
        conn = _init_db_connection()
        conn.ping(reconnect=True)

    return conn

# 3. UI: Simple Header
st.title("Welcome to my App")


@st.cache_data(ttl=60)
def get_all_users():
    conn = get_db_connection()
    query = "SELECT id, username, email, age, created_at FROM users"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


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


# UI: Dashboard (READ)
st.subheader("Registered Users")
if st.button("Refresh User List"):
    st.rerun()

users_df = get_all_users()
st.dataframe(users_df)


