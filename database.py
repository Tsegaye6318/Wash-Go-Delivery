import os
import psycopg2
from psycopg2 import sql
import streamlit as st

# Database connection parameters
db_params = {
    'dbname': os.environ.get('PGDATABASE'),
    'user': os.environ.get('PGUSER'),
    'password': os.environ.get('PGPASSWORD'),
    'host': os.environ.get('PGHOST'),
    'port': os.environ.get('PGPORT')
}

def get_db_connection():
    return psycopg2.connect(**db_params)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create sequence for users table if it doesn't exist
        cur.execute('''
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = 'users_id_seq') THEN
                CREATE SEQUENCE users_id_seq START 1;
            END IF;
        END
        $$;
        ''')

        # Create new users table without loyalty points and referral code
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY DEFAULT nextval('users_id_seq'),
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            is_first_time_customer BOOLEAN DEFAULT TRUE
        )
        """)
        
        # Check if users_old table exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users_old')")
        users_old_exists = cur.fetchone()[0]

        if users_old_exists:
            # Check if email and phone columns exist in users_old table
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users_old' AND column_name IN ('email', 'phone')")
            existing_columns = [row[0] for row in cur.fetchall()]

            # Modify the INSERT statement based on existing columns
            if 'email' in existing_columns and 'phone' in existing_columns:
                insert_query = '''
                INSERT INTO users (id, username, password, email, phone, is_admin)
                SELECT id, username, password, 
                    COALESCE(email, username || '@example.com') as email,
                    COALESCE(phone, '1234567890') as phone,
                    is_admin 
                FROM users_old
                ON CONFLICT (id) DO NOTHING
                '''
            else:
                insert_query = '''
                INSERT INTO users (id, username, password, email, phone, is_admin)
                SELECT id, username, password, 
                    username || '@example.com' as email,
                    '1234567890' as phone,
                    is_admin 
                FROM users_old
                ON CONFLICT (id) DO NOTHING
                '''

            cur.execute(insert_query)

            # Now we can safely drop the users_old table
            cur.execute("DROP TABLE IF EXISTS users_old")

        # Update the sequence to the maximum ID
        cur.execute('''
        SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 0) + 1, false);
        ''')
        
        # Create orders table (unchanged)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            pickup_date DATE NOT NULL,
            pickup_time TIME NOT NULL,
            location TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'Pending',
            weight FLOAT,
            item_count INTEGER,
            total_price FLOAT
        )
        """)

        # Drop the referrals table if it exists
        cur.execute("DROP TABLE IF EXISTS referrals")
        
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

def execute_query(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()

def fetch_one(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def fetch_all(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def is_first_time_customer(user_id):
    result = fetch_one("SELECT is_first_time_customer FROM users WHERE id = %s", (user_id,))
    return result[0] if result else False

def set_customer_order_placed(user_id):
    execute_query("UPDATE users SET is_first_time_customer = FALSE WHERE id = %s", (user_id,))
