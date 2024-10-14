import streamlit as st
import database
import pandas as pd
import plotly.express as px
import time
from datetime import datetime, timedelta
import utils
import requests
import json
import os
import stripe

# Set up Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def get_address_suggestions(input_text):
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    base_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": input_text,
        "key": api_key,
        "types": "address"
    }
    response = requests.get(base_url, params=params)
    suggestions = json.loads(response.text)['predictions']
    return [suggestion['description'] for suggestion in suggestions]

def user_dashboard():
    st.title(f"Welcome to Wash & Go Delivery, {st.session_state.user['username']}! 👋")
    st.write("Here's a summary of your recent laundry activity:")
    
    if st.session_state.user['is_first_time_customer']:
        st.info("As a first-time customer, you're eligible for a 20% discount on your first order!")
    
    recent_orders = database.fetch_all(
        "SELECT * FROM orders WHERE user_id = %s ORDER BY pickup_date DESC LIMIT 5",
        (st.session_state.user['id'],)
    )
    
    if recent_orders:
        st.subheader("Recent Orders")
        for order in recent_orders:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"Order #{order[0]} - {order[2]}")
                with col2:
                    st.write(f"Status: {order[5]}")
                with col3:
                    st.write(f"Total: ${order[8]:.2f}")
    else:
        st.info("You don't have any recent orders.")
    
    st.markdown("---")
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Schedule a New Pickup', key='schedule_pickup_button', use_container_width=True):
            from main import navigate_to
            navigate_to('Schedule Pickup')
    with col2:
        if st.button('View Order History', key='view_history_button', use_container_width=True):
            from main import navigate_to
            navigate_to('Order History')

    st.markdown("---")
    st.subheader("Need Help?")
    st.write("Contact our customer support:")
    st.write("📞 Phone: (301) 555-1234")
    st.write("📧 Email: support@washandgodelivery.com")
    st.write("🕒 Hours: Mon-Sat: 7AM-9PM, Sun: 9AM-7PM")

def schedule_pickup():
    st.title("Schedule a Pickup with Wash & Go Delivery 📅")
    
    col1, col2 = st.columns(2)
    with col1:
        pickup_date = st.date_input("Pickup Date", min_value=datetime.now().date())
    with col2:
        pickup_time = st.time_input("Pickup Time")
    
    location_input = st.text_input("Pickup Location", key="location_input")
    suggestions = get_address_suggestions(location_input)
    location = st.selectbox("Select or confirm address", options=[""] + suggestions, key="location_select")
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Estimated Weight (in kg)", min_value=0.0, step=0.5)
    with col2:
        item_count = st.number_input("Number of Items", min_value=0, step=1)
    
    total_price = utils.calculate_price_by_weight(weight, st.session_state.user['is_first_time_customer'])
    st.write(f"Estimated Price: ${total_price:.2f}")
    if st.session_state.user['is_first_time_customer']:
        st.write("20% first-time customer discount applied!")
    
    st.markdown("---")
    st.subheader("Order Summary")
    st.write(f"Pickup Date: {pickup_date}")
    st.write(f"Pickup Time: {pickup_time}")
    st.write(f"Location: {location}")
    st.write(f"Estimated Weight: {weight} kg")
    st.write(f"Number of Items: {item_count}")
    st.write(f"Total Price: ${total_price:.2f}")
    
    if st.button("Proceed to Payment", key='proceed_to_payment_button', use_container_width=True):
        if not (pickup_date and pickup_time and location):
            st.error("Please fill in all the fields.")
        else:
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(total_price * 100),  # Stripe expects amount in cents
                            'product_data': {
                                'name': 'Laundry Service',
                                'description': f'Pickup on {pickup_date} at {pickup_time}',
                            },
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f"{os.environ.get('REPLIT_URL', 'http://localhost:5000')}/?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=f"{os.environ.get('REPLIT_URL', 'http://localhost:5000')}/",
                )
                
                st.session_state.pending_order = {
                    'user_id': st.session_state.user['id'],
                    'pickup_date': pickup_date,
                    'pickup_time': pickup_time,
                    'location': location,
                    'weight': weight,
                    'item_count': item_count,
                    'total_price': total_price,
                    'checkout_session_id': checkout_session.id
                }
                
                st.markdown(f'<script>window.location.href = "{checkout_session.url}";</script>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"An error occurred while processing your payment: {str(e)}")

def order_history():
    st.title("Wash & Go Delivery Order History 📋")
    orders = database.fetch_all(
        "SELECT * FROM orders WHERE user_id = %s ORDER BY pickup_date DESC",
        (st.session_state.user['id'],)
    )
    
    if orders:
        df_orders = pd.DataFrame(orders, columns=['id', 'user_id', 'pickup_date', 'pickup_time', 'location', 'status', 'weight', 'item_count', 'total_price'])
        
        # Display orders in an expandable format
        for _, order in df_orders.iterrows():
            with st.expander(f"Order #{order['id']} - {order['pickup_date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Status: {order['status']}")
                    st.write(f"Pickup Time: {order['pickup_time']}")
                    st.write(f"Location: {order['location']}")
                with col2:
                    st.write(f"Weight: {order['weight']} kg")
                    st.write(f"Item Count: {order['item_count']}")
                    st.write(f"Total Price: ${order['total_price']:.2f}")
        
        # Visualizations
        st.subheader("Order Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Orders by status
            status_counts = df_orders['status'].value_counts()
            fig_status = px.pie(values=status_counts.values, names=status_counts.index, title="Orders by Status")
            st.plotly_chart(fig_status)
        
        with col2:
            # Total spent over time
            df_orders['pickup_date'] = pd.to_datetime(df_orders['pickup_date'])
            spending_over_time = df_orders.groupby('pickup_date')['total_price'].sum().reset_index()
            fig_spending = px.line(spending_over_time, x='pickup_date', y='total_price', title="Total Spent Over Time")
            st.plotly_chart(fig_spending)
    else:
        st.info("You don't have any orders with Wash & Go Delivery yet.")

def handle_successful_payment():
    if 'session_id' in st.query_params:
        session_id = st.query_params['session_id']
        if 'pending_order' in st.session_state and st.session_state.pending_order['checkout_session_id'] == session_id:
            order = st.session_state.pending_order
            try:
                database.execute_query(
                    "INSERT INTO orders (user_id, pickup_date, pickup_time, location, weight, item_count, total_price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (order['user_id'], order['pickup_date'], order['pickup_time'], order['location'], order['weight'], order['item_count'], order['total_price'], 'Paid')
                )
                if st.session_state.user['is_first_time_customer']:
                    database.set_customer_order_placed(st.session_state.user['id'])
                    st.session_state.user['is_first_time_customer'] = False
                st.success("Payment successful! Your pickup has been scheduled.")
                del st.session_state.pending_order
            except Exception as e:
                st.error(f"An error occurred while finalizing your order: {str(e)}")
        else:
            st.warning("Invalid or expired payment session.")
