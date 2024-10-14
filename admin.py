import streamlit as st
import database
import pandas as pd
import plotly.express as px
import time
from datetime import datetime, timedelta

def admin_dashboard():
    st.title("Wash & Go Delivery Admin Dashboard 🚀")
    
    st.write("This dashboard updates automatically every 5 seconds.")
    
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # Display all orders
            st.header("All Orders")
            orders = database.fetch_all("SELECT * FROM orders")
            df_orders = pd.DataFrame(orders, columns=['id', 'user_id', 'pickup_date', 'pickup_time', 'location', 'status', 'weight', 'item_count', 'total_price'])
            
            # Add filters
            st.subheader("Filters")
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.multiselect("Status", df_orders['status'].unique())
            with col2:
                date_range = st.date_input("Date Range", [df_orders['pickup_date'].min(), df_orders['pickup_date'].max()])
            with col3:
                price_range = st.slider("Price Range", float(df_orders['total_price'].min()), float(df_orders['total_price'].max()), (float(df_orders['total_price'].min()), float(df_orders['total_price'].max())))
            
            # Apply filters
            filtered_df = df_orders[
                (df_orders['status'].isin(status_filter) if status_filter else True) &
                (df_orders['pickup_date'].between(date_range[0], date_range[1])) &
                (df_orders['total_price'].between(price_range[0], price_range[1]))
            ]
            
            st.dataframe(filtered_df.style.highlight_max(axis=0))
            
            # Update order status
            st.subheader("Update Order Status")
            col1, col2, col3 = st.columns(3)
            with col1:
                order_id = st.number_input("Order ID", min_value=1, step=1)
            with col2:
                new_status = st.selectbox("New Status", ["Pending", "Picked Up", "In Progress", "Ready for Delivery", "Delivered", "Cancelled"])
            with col3:
                if st.button("Update Status"):
                    database.execute_query("UPDATE orders SET status = %s WHERE id = %s", (new_status, order_id))
                    st.success(f"Order {order_id} status updated to {new_status}")
            
            # Visualizations
            st.header("Wash & Go Delivery Order Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Orders by status
                status_counts = df_orders['status'].value_counts()
                fig_status = px.pie(values=status_counts.values, names=status_counts.index, title="Orders by Status")
                st.plotly_chart(fig_status)
            
            with col2:
                # Daily order count
                df_orders['pickup_date'] = pd.to_datetime(df_orders['pickup_date'])
                daily_orders = df_orders.groupby('pickup_date').size().reset_index(name='count')
                fig_daily = px.line(daily_orders, x='pickup_date', y='count', title="Daily Order Count")
                st.plotly_chart(fig_daily)
            
            # Revenue analysis
            st.subheader("Wash & Go Delivery Revenue Analysis")
            df_orders['pickup_date'] = pd.to_datetime(df_orders['pickup_date'])
            revenue_by_date = df_orders.groupby('pickup_date')['total_price'].sum().reset_index()
            fig_revenue = px.bar(revenue_by_date, x='pickup_date', y='total_price', title="Daily Revenue")
            st.plotly_chart(fig_revenue)
            
            # Top customers
            st.subheader("Top Wash & Go Delivery Customers")
            top_customers = df_orders.groupby('user_id')['total_price'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_top_customers = px.bar(top_customers, x='user_id', y='total_price', title="Top 10 Customers by Revenue")
            st.plotly_chart(fig_top_customers)
            
            # First-time customer analysis
            st.subheader("Wash & Go Delivery First-Time Customer Analysis")
            first_time_customers = database.fetch_all("SELECT * FROM users WHERE is_first_time_customer = TRUE")
            st.write(f"Number of first-time customers: {len(first_time_customers)}")
            
            first_time_orders = database.fetch_all("""
                SELECT o.* FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE u.is_first_time_customer = TRUE
            """)
            df_first_time_orders = pd.DataFrame(first_time_orders, columns=['id', 'user_id', 'pickup_date', 'pickup_time', 'location', 'status', 'weight', 'item_count', 'total_price'])
            
            if not df_first_time_orders.empty:
                st.write("First-Time Customer Orders:")
                st.dataframe(df_first_time_orders)
                
                # Calculate total discount given to first-time customers
                total_discount = df_first_time_orders['total_price'].sum() * 0.25  # 20% discount is equivalent to 25% of the discounted price
                st.write(f"Total discount given to first-time customers: ${total_discount:.2f}")
            else:
                st.write("No orders from first-time customers yet.")
            
            # Real-time order tracking
            st.subheader("Wash & Go Delivery Real-Time Order Tracking")
            for _, order in filtered_df.iterrows():
                with st.expander(f"Order #{order['id']} - {order['pickup_date']}"):
                    st.write(f"Status: {order['status']}")
                    st.write(f"Total Price: ${order['total_price']:.2f}")
                    st.write(f"Pickup Time: {order['pickup_time']}")
                    st.write(f"Location: {order['location']}")
                    
                    # Add a progress bar for order status
                    progress = get_order_progress(order['status'])
                    st.progress(progress)
                    
                    # Add estimated delivery time
                    estimated_delivery = get_estimated_delivery(order['pickup_date'], order['status'])
                    st.write(f"Estimated Delivery: {estimated_delivery}")
                    
                    # Add a map showing the order location (placeholder)
                    st.write("Order Location:")
                    st.map()  # This will show a default map. In a real app, we'd use the actual coordinates.
        
        time.sleep(5)
        st.rerun()

def get_order_progress(status):
    status_progress = {
        "Pending": 0,
        "Picked Up": 25,
        "In Progress": 50,
        "Ready for Delivery": 75,
        "Delivered": 100
    }
    return status_progress.get(status, 0)

def get_estimated_delivery(pickup_date, status):
    pickup_date = datetime.strptime(str(pickup_date), "%Y-%m-%d")
    if status == "Delivered":
        return "Order has been delivered"
    elif status == "Ready for Delivery":
        return "Today"
    else:
        estimated_date = pickup_date + timedelta(days=2)
        return estimated_date.strftime("%Y-%m-%d")
