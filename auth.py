import streamlit as st
import database
import hashlib
import re

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_page():
    st.title("Login to Wash & Go Delivery")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        print("Login button clicked")  # Debug print
        user = database.fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        print(f"User query result: {user}")  # Debug print
        if user and user[2] == hash_password(password):
            print("Login successful")  # Debug print
            st.session_state.user = {
                'id': user[0],
                'username': user[1],
                'email': user[3],
                'phone': user[4],
                'is_admin': user[5],
                'is_first_time_customer': user[6] if len(user) > 6 else True  # Default to True if field doesn't exist
            }
            st.session_state.page = "User Dashboard"  # Set the page to User Dashboard after successful login
            st.success("Logged in successfully!")
            st.rerun()
        else:
            print("Login failed")  # Debug print
            st.error("Invalid username or password")

def register_page():
    st.title("Register for Wash & Go Delivery")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
        elif database.fetch_one("SELECT * FROM users WHERE username = %s", (username,)):
            st.error("Username already exists")
        elif not validate_email(email):
            st.error("Invalid email address")
        elif not validate_phone(phone):
            st.error("Invalid phone number")
        else:
            hashed_password = hash_password(password)
            database.execute_query('INSERT INTO users (username, password, email, phone) VALUES (%s, %s, %s, %s)', (username, hashed_password, email, phone))
            user_id = database.fetch_one('SELECT id FROM users WHERE username = %s', (username,))[0]
            
            st.session_state.user = {
                'id': user_id,
                'username': username,
                'email': email,
                'phone': phone,
                'is_admin': False,
                'is_first_time_customer': True
            }
            st.success("Registration successful! Redirecting to dashboard...")
            st.rerun()

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_phone(phone):
    phone_regex = r'^\+?1?\d{9,15}$'
    return re.match(phone_regex, phone) is not None

def logout():
    # Clear the user session state
    st.session_state.user = None
    # Reset the page to Home
    st.session_state.page = "Home"
    st.success("Logged out successfully!")
    # Use rerun to refresh the page and apply the changes
    st.rerun()
