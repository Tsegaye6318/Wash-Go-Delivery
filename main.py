import streamlit as st
import database
import auth
import admin
import user
import utils

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

def home_page():
    st.title("Welcome to Wash & Go Delivery")
    st.write("Your one-stop solution for hassle-free laundry services!")
    st.image("assets/logo.svg", width=300)

    # Services section
    st.header("Our Services")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Wash and Fold")
        st.write("Let us take care of your everyday laundry needs.")
        st.write("Price: $2.50 per pound")
    with col2:
        st.subheader("Dry Cleaning")
        st.write("Professional care for your delicate garments.")
        st.write("Price: Starting at $8 per item")

    # Service Areas section
    st.subheader('Service Areas')
    st.write('We currently operate in the following locations in the DMV area:')

    with st.container():
        col1, col2, col3 = st.columns(3)
        locations = [
            'Bethesda, MD', 'Rockville, MD', 'Silver Spring, MD', 'Washington, D.C.', 'Gaithersburg, MD', 'Colesville, MD',
            'Laurel, MD', 'Hyattsville, MD', 'Chevy Chase, MD', 'Wheaton, MD', 'Takoma Park, MD',
            'Greenbelt, MD', 'Riverdale Park, MD', 'Falls Church, VA', 'Alexandria, VA', 'Arlington, VA',
            'Vienna, VA', 'Beltsville, MD', 'College Park, MD', 'Bladensburg, MD', 'Lanham, MD',
            'Bowie, MD', 'Mount Rainier, MD'
        ]
        locations_per_column = len(locations) // 3 + (len(locations) % 3 > 0)
        
        with col1:
            for loc in locations[:locations_per_column]:
                st.write(f'• {loc}')
        with col2:
            for loc in locations[locations_per_column:2*locations_per_column]:
                st.write(f'• {loc}')
        with col3:
            for loc in locations[2*locations_per_column:]:
                st.write(f'• {loc}')

    # Express service
    st.subheader("Express Service")
    st.write("Need it fast? Our express service ensures same-day delivery!")
    st.write("Additional $10 fee for express service")

    # Special promotion
    st.info("🎉 Special Promotion: 20% off your first order when you sign up today!")

    # Features
    st.header("Why Choose Wash & Go Delivery?")
    features = [
        "✅ Convenient pickup and delivery",
        "✅ Eco-friendly cleaning options",
        "✅ Real-time order tracking",
        "✅ Flexible scheduling",
        "✅ Satisfaction guaranteed"
    ]
    for feature in features:
        st.write(feature)

    # Contact Information
    st.header("Contact Us")
    st.write("We're here to help! Get in touch with us:")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📞 Phone: (202) 202-2083")
        st.write("📧 Email: WashGoDelivery@gmail.com")
    with col2:
        st.write("🏠 Address: 525 Thayer Ave, Silver Spring, MD 20910")
        st.write("⏰ Hours: Mon-Sat: 7AM-9PM, Sun: 9AM-7PM")

    st.write("Please login or register to get started.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", key="home_login_button", use_container_width=True):
            navigate_to("Login")
    with col2:
        if st.button("Register", key="home_register_button", use_container_width=True):
            navigate_to("Register")

def main():
    st.set_page_config(page_title="Wash & Go Delivery", page_icon="🧺", layout="wide")
    
    # Add custom CSS for responsive design and consistent button styles
    st.markdown("""
        <style>
        .stApp {
            background-color: #f0f8ff;
        }
        .main-title {
            color: #4CAF50;
            font-size: clamp(1.5rem, 5vw, 2.5rem);
            text-align: center;
            margin-bottom: 20px;
        }
        .sidebar .sidebar-content {
            background-color: #e6f3ff;
        }
        /* Responsive design */
        @media (max-width: 768px) {
            .stButton > button {
                width: 100%;
                margin-bottom: 10px;
            }
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stDateInput > div > div > input,
            .stTimeInput > div > div > input,
            .stNumberInput > div > div > input {
                width: 100%;
            }
            .stDataFrame {
                font-size: 0.8em;
            }
            .stPlotlyChart {
                height: 300px !important;
            }
        }
        /* Mobile-specific styles */
        @media (max-width: 480px) {
            .stSidebar {
                width: 100%;
                position: relative;
            }
            .stSidebar > div:first-child {
                height: auto !important;
                min-height: 0px !important;
            }
            .stImage {
                max-width: 200px;
                margin: 0 auto;
                display: block;
            }
            .stContainer {
                padding: 1rem 0.5rem;
            }
            .stHeader {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
            .stColumn {
                padding: 0.25rem;
            }
        }
        /* Updated consistent button styles */
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stButton > button:hover {
            background-color: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .stButton > button:active {
            background-color: #3d8b40;
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #2C3E50;
        }
        .stInfo {
            background-color: #E8F5E9;
            padding: 1rem;
            border-radius: 4px;
            border-left: 5px solid #4CAF50;
            margin-bottom: 1rem;
        }
        /* Consistent sidebar button styles */
        .stSidebar .stButton > button {
            background-color: #4CAF50;
            color: white;
            width: 100%;
            margin-bottom: 0.5rem;
        }
        .stSidebar .stButton > button:hover {
            background-color: #45a049;
        }
        .stSidebar .stButton > button:active {
            background-color: #3d8b40;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.image("assets/logo.svg", width=200)
    st.sidebar.title("Navigation")
    
    if st.session_state.user is None:
        pages = ["Home", "Login", "Register"]
    elif st.session_state.user.get('is_admin', False):
        pages = ["Admin Dashboard", "Logout"]
    else:
        pages = ["User Dashboard", "Schedule Pickup", "Order History", "Logout"]
    
    for page in pages:
        if st.sidebar.button(page, key=f'nav_{page.lower().replace(" ", "_")}'):
            navigate_to(page)
    
    # Main content
    st.markdown("<h1 class='main-title'>Wash & Go Delivery</h1>", unsafe_allow_html=True)
    
    try:
        # Handle successful payment redirect
        if 'session_id' in st.query_params:
            user.handle_successful_payment()
        
        if st.session_state.page == "Home":
            home_page()
        elif st.session_state.page == "Login":
            auth.login_page()
        elif st.session_state.page == "Register":
            auth.register_page()
        elif st.session_state.page == "Admin Dashboard":
            admin.admin_dashboard()
        elif st.session_state.page == "User Dashboard":
            user.user_dashboard()
        elif st.session_state.page == "Schedule Pickup":
            user.schedule_pickup()
        elif st.session_state.page == "Order History":
            user.order_history()
        elif st.session_state.page == "Logout":
            auth.logout()
        else:
            st.error(f"Page '{st.session_state.page}' not found.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    database.init_db()
    main()
