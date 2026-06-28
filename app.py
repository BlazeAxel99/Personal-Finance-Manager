# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
import os
import shutil
from bcrypt import hashpw, gensalt, checkpw

# Set page config for wide layout and custom title
st.set_page_config(
    page_title="Personal Finance Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject premium custom CSS for 2026 glassmorphism aesthetic
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Global Fonts & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Hide default Streamlit decoration */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Glassmorphic Cards */
    .card {
        background: rgba(30, 41, 59, 0.45);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .card:hover {
        border-color: rgba(0, 242, 254, 0.3);
        transform: translateY(-2px);
    }
    
    .card-title {
        color: #94A3B8;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .card-value {
        color: #F8FAFC;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .card-value.highlight {
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .card-value.danger {
        background: linear-gradient(90deg, #FF5E62 0%, #FF9966 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .card-value.success {
        background: linear-gradient(90deg, #00FF87 0%, #60EFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .card-subtitle {
        color: #64748B;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* Centered Login & Register Cards */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 60px 0;
    }
    
    .login-card {
        max-width: 450px;
        width: 100%;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    }
    
    /* Tab bar styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1E293B;
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 500;
        border: none;
        padding: 0 20px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC;
        background-color: rgba(255, 255, 255, 0.03);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0F172A !important;
        color: #00F2FE !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        color: #0F172A !important;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.25);
        width: 100%;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #4FACFE 0%, #00F2FE 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 242, 254, 0.4);
        color: #0F172A !important;
    }
    
    .stButton>button:active {
        transform: translateY(0px);
    }
    
    /* Secondary/Logout buttons */
    div[data-testid="stFormSubmitButton"] button, 
    .logout-btn button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stFormSubmitButton"] button:hover,
    .logout-btn button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #F8FAFC !important;
        transform: translateY(-1px);
    }
    
    /* Style form containers */
    [data-testid="stForm"] {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background-color: rgba(30, 41, 59, 0.3) !important;
        border-radius: 16px !important;
        padding: 24px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'budget' not in st.session_state:
    st.session_state['budget'] = 0.0
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []
if 'investments' not in st.session_state:
    st.session_state['investments'] = []
if 'categories' not in st.session_state:
    st.session_state['categories'] = ['Food', 'Transportation', 'Entertainment', 'Housing', 'Utilities', 'Healthcare', 'Insurance', 'Savings', 'Others']
if 'current_savings' not in st.session_state:
    st.session_state['current_savings'] = 0.0
if 'income_sources' not in st.session_state:
    st.session_state['income_sources'] = []
if 'savings_goal_desc' not in st.session_state:
    st.session_state['savings_goal_desc'] = ""
if 'savings_goal_amount' not in st.session_state:
    st.session_state['savings_goal_amount'] = 0.0

# Files for data storage
USER_DATA_FILE = 'user_data.pkl'
BACKUP_FILE = 'user_data.pkl.bak'

# Load user data with robust recovery chain
def load_user_data():
    # Attempt 1: Load main data file
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'rb') as file:
                return pickle.load(file)
        except Exception as e:
            st.warning(f"Unable to read main data file. Attempting recovery from backup... (Error: {e})")
            
    # Attempt 2: Load from backup file
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, 'rb') as file:
                data = pickle.load(file)
                # Restore the main file from the backup
                shutil.copy2(BACKUP_FILE, USER_DATA_FILE)
                st.success("Successfully recovered user database from backup file!")
                return data
        except Exception as e:
            st.error(f"Recovery failed. Backup file is also unreadable. (Error: {e})")
            
    # Attempt 3: Return empty state
    return {}

# Save user data atomically
def save_user_data(user_data):
    # 1. Create a rolling backup of the current valid file if it exists
    if os.path.exists(USER_DATA_FILE):
        try:
            shutil.copy2(USER_DATA_FILE, BACKUP_FILE)
        except Exception:
            pass # Continue even if backup creation fails

    # 2. Write atomically using a temporary file
    username = st.session_state.get('current_user', 'temp')
    temp_file = f"user_data_{username}.pkl.tmp"
    try:
        with open(temp_file, 'wb') as file:
            pickle.dump(user_data, file)
        # Atomic replace
        os.replace(temp_file, USER_DATA_FILE)
    except Exception as e:
        st.error(f"Error saving data: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

# Hash password
def hash_password(password):
    return hashpw(password.encode(), gensalt())

# Verify password
def verify_password(password, hashed):
    try:
        return checkpw(password.encode(), hashed)
    except Exception:
        return False

# User registration
def register_user(username, password):
    user_data = load_user_data()
    if username in user_data:
        return False  # Username already exists
    user_data[username] = {
        'password': hash_password(password),
        'budget': 0.0,
        'expenses': [],
        'investments': [],
        'categories': ['Food', 'Transportation', 'Entertainment', 'Housing', 'Utilities', 'Healthcare', 'Insurance', 'Savings', 'Others'],
        'income_sources': [],
        'current_savings': 0.0,
        'savings_goal_desc': "",
        'savings_goal_amount': 0.0,
    }
    save_user_data(user_data)
    return True

# Load saved data for the logged-in user
def load_user_session(username):
    user_data = load_user_data()
    user = user_data.get(username, {})
    st.session_state['budget'] = float(user.get('budget', 0.0))
    st.session_state['expenses'] = user.get('expenses', [])
    st.session_state['investments'] = user.get('investments', [])
    st.session_state['categories'] = user.get('categories', ['Food', 'Transportation', 'Entertainment', 'Housing', 'Utilities', 'Healthcare', 'Insurance', 'Savings', 'Others'])
    st.session_state['income_sources'] = user.get('income_sources', [])
    st.session_state['current_savings'] = float(user.get('current_savings', 0.0))
    st.session_state['savings_goal_desc'] = user.get('savings_goal_desc', "")
    st.session_state['savings_goal_amount'] = float(user.get('savings_goal_amount', 0.0))

# Save data for the logged-in user (atomic)
def save_user_session(username):
    if not username:
        return
    user_data = load_user_data()
    if username in user_data:
        user_data[username] = {
            'password': user_data[username]['password'],
            'budget': float(st.session_state['budget']),
            'expenses': st.session_state['expenses'],
            'investments': st.session_state['investments'],
            'categories': st.session_state['categories'],
            'income_sources': st.session_state['income_sources'],
            'current_savings': float(st.session_state['current_savings']),
            'savings_goal_desc': st.session_state['savings_goal_desc'],
            'savings_goal_amount': float(st.session_state['savings_goal_amount']),
        }
        save_user_data(user_data)

# Helper to trigger auto-save
def auto_save():
    if st.session_state['logged_in'] and st.session_state['current_user']:
        save_user_session(st.session_state['current_user'])

# App Title & Header
st.markdown("<h1 style='text-align: center; margin-bottom: 30px; font-weight: 700;'>💰 Personal Finance Manager</h1>", unsafe_allow_html=True)

# Login and Registration Page
if not st.session_state['logged_in']:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 24px; font-weight: 600;'>Welcome</h2>", unsafe_allow_html=True)
        
        option = st.radio('Select an option', ['Login', 'Register'], label_visibility="collapsed")
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        if option == 'Login':
            input_username = st.text_input('Username', key='login_username', placeholder="Enter your username")
            input_password = st.text_input('Password', type='password', key='login_password', placeholder="Enter your password")
            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            if st.button('Sign In'):
                user_data = load_user_data()
                if input_username in user_data and verify_password(input_password, user_data[input_username]['password']):
                    st.session_state['logged_in'] = True
                    st.session_state['current_user'] = input_username
                    load_user_session(input_username)
                    st.success(f"Welcome back, {input_username}!")
                    st.rerun()
                else:
                    st.error('Invalid username or password')

        elif option == 'Register':
            new_username = st.text_input('Choose a username', key='register_username', placeholder="Min 3 characters")
            new_password = st.text_input('Choose a password', type='password', key='register_password', placeholder="Min 6 characters")
            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            if st.button('Create Account'):
                if len(new_username) < 3 or len(new_password) < 6:
                    st.error('Username must be at least 3 chars, password at least 6 chars.')
                elif register_user(new_username, new_password):
                    st.success('User registered successfully! Please login.')
                else:
                    st.error('Username already exists. Please choose a different one.')
        
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Main app functionality
else:
    # Top User Welcome and Logout Bar
    welcome_col, logout_col = st.columns([8, 2])
    with welcome_col:
        st.markdown(f"<h3 style='margin-top: 10px; font-weight: 500; color: #94A3B8;'>Hello, <span style='color: #00F2FE; font-weight: 600;'>{st.session_state['current_user']}</span>!</h3>", unsafe_allow_html=True)
    with logout_col:
        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button('Log Out'):
            auto_save()
            st.session_state['logged_in'] = False
            st.session_state['current_user'] = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # Calculation of Metrics
    # ----------------------------------------------------
    total_income = sum(float(item.get('amount', 0)) for item in st.session_state['income_sources'])
    total_expenses = sum(float(item.get('amount', 0)) for item in st.session_state['expenses'])
    total_investments = sum(float(item.get('amount', 0)) for item in st.session_state['investments'])
    net_worth = total_income - total_expenses + total_investments
    remaining_budget = st.session_state['budget'] - total_expenses
    
    # Update current_savings dynamically in session state
    st.session_state['current_savings'] = total_income - total_expenses
    
    # Budget status styling (shifts to red/coral gradient if over budget)
    budget_class = "highlight"
    if remaining_budget < 0:
        budget_class = "danger"
    elif remaining_budget < (st.session_state['budget'] * 0.15): # less than 15% remaining
        budget_class = "danger"

    # ----------------------------------------------------
    # Premium Dashboard Metrics Cards (Top of page)
    # ----------------------------------------------------
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Net Worth</div>
            <div class="card-value highlight">${net_worth:,.2f}</div>
            <div class="card-subtitle">Income - Expenses + Investments</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Total Income</div>
            <div class="card-value success">${total_income:,.2f}</div>
            <div class="card-subtitle">Total cash inflows</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_col3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Total Expenses</div>
            <div class="card-value danger">${total_expenses:,.2f}</div>
            <div class="card-subtitle">Total cash outflows</div>
        </div>
        """, unsafe_allow_html=True)
        
    with metric_col4:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Remaining Budget</div>
            <div class="card-value {budget_class}">${remaining_budget:,.2f}</div>
            <div class="card-subtitle">Budget: ${st.session_state['budget']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Budget Overrun Alert Banner
    if remaining_budget < 0:
        st.error(f"⚠️ **Budget Overrun Alert:** You have exceeded your monthly budget by **${abs(remaining_budget):,.2f}**!")
    elif st.session_state['budget'] > 0 and remaining_budget < (st.session_state['budget'] * 0.15):
        st.warning(f"⚠️ **Budget Warning:** You have less than 15% (**${remaining_budget:,.2f}**) of your budget remaining!")

    # Create tabs for navigation
    tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        '🏠 Dashboard', '💼 Budget & Goals', '🛒 Expenses', '📈 Investments', '📊 Analytics', '💵 Income', '📥 Download Data'
    ])

    # Custom color palette for charts
    custom_colors = ['#00F2FE', '#9d4edd', '#ff7096', '#3a86c8', '#4FACFE', '#ffb703', '#fb8500', '#023e8a', '#e63946']

    # Dashboard Tab (Quick overview and insights)
    with tab0:
        st.subheader("Financial Overview")
        dash_col1, dash_col2 = st.columns([3, 2])
        
        with dash_col1:
            # Net Flow chart over time or category breakdown
            if st.session_state['expenses'] or st.session_state['income_sources']:
                flow_data = pd.DataFrame([
                    {"Type": "Income", "Amount": total_income},
                    {"Type": "Expenses", "Amount": total_expenses},
                    {"Type": "Investments", "Amount": total_investments}
                ])
                fig_flow = px.bar(
                    flow_data, 
                    x="Type", 
                    y="Amount", 
                    color="Type",
                    color_discrete_map={"Income": "#00FF87", "Expenses": "#FF5E62", "Investments": "#00F2FE"},
                    title="Cash Flow Summary"
                )
                fig_flow.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=40, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_flow, use_container_width=True)
            else:
                st.info("Add income and expenses to see your cash flow summary.")

        with dash_col2:
            # Savings Goal Progress Card
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>Savings Goal Progress</div>", unsafe_allow_html=True)
            
            goal_desc = st.session_state.get('savings_goal_desc', 'No goal set')
            goal_amt = float(st.session_state.get('savings_goal_amount', 0.0))
            current_sav = st.session_state['current_savings']
            
            st.markdown(f"<h5>Goal: <b>{goal_desc}</b></h5>", unsafe_allow_html=True)
            st.markdown(f"<h3>${current_sav:,.2f} / ${goal_amt:,.2f}</h3>", unsafe_allow_html=True)
            
            if goal_amt > 0:
                progress_percent = min(1.0, max(0.0, current_sav / goal_amt))
                st.progress(progress_percent)
                st.markdown(f"<span style='color:#94A3B8; font-size:12px;'>{progress_percent*100:.1f}% Completed</span>", unsafe_allow_html=True)
            else:
                st.progress(0.0)
                st.markdown("<span style='color:#64748B; font-size:12px;'>Set a savings goal in the 'Budget & Goals' tab</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Quick Financial Insights
            st.subheader("AI Financial Insights")
            insights = []
            if total_income > 0:
                expense_ratio = total_expenses / total_income
                if expense_ratio > 0.8:
                    insights.append("⚠️ **High spending:** You are spending over 80% of your income. Consider reviewing non-essential expenses.")
                elif expense_ratio < 0.5:
                    insights.append("🌟 **Excellent saving rate:** You are saving more than 50% of your income! Consider increasing your investments.")
            
            if total_investments > 0 and total_income > 0:
                invest_ratio = total_investments / total_income
                if invest_ratio >= 0.2:
                    insights.append("📈 **Great investment habit:** You invest 20% or more of your income. Keep building your wealth!")
                    
            if not insights:
                insights.append("💡 Add more financial details (income, expenses, investments) to receive personalized insights.")
                
            for insight in insights:
                st.info(insight)

    # Budget tab
    with tab1:
        st.subheader('Set Your Budget & Goals')
        budget_col1, budget_col2 = st.columns(2)
        
        with budget_col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### Monthly Budget")
            new_budget = st.number_input(
                'Enter your monthly budget ($):', 
                min_value=0.0, 
                value=float(st.session_state['budget']), 
                step=100.0, 
                key='budget_input'
            )
            if new_budget != st.session_state['budget']:
                st.session_state['budget'] = new_budget
                auto_save()
                st.success(f'Your budget is updated to **${st.session_state["budget"]:,.2f}**')
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with budget_col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### Savings Goal")
            new_goal_desc = st.text_input('Goal Description:', value=st.session_state['savings_goal_desc'])
            new_goal_amount = st.number_input(
                'Goal Amount ($):', 
                min_value=0.0, 
                value=float(st.session_state['savings_goal_amount']), 
                step=100.0, 
                key='goal_amount_input'
            )
            
            if (new_goal_desc != st.session_state['savings_goal_desc'] or 
                new_goal_amount != st.session_state['savings_goal_amount']):
                st.session_state['savings_goal_desc'] = new_goal_desc
                st.session_state['savings_goal_amount'] = new_goal_amount
                auto_save()
                st.success('Savings goal updated successfully!')
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Expenses tab (st.data_editor with dynamic rows and validations)
    with tab2:
        st.subheader('Track Your Expenses')
        st.markdown("Manage your expenses in the interactive table below. Add new rows or select and delete them as needed.")
        
        # Build DataFrame from session state
        expenses_df = pd.DataFrame(st.session_state['expenses'])
        if expenses_df.empty:
            expenses_df = pd.DataFrame(columns=['category', 'amount'])
        else:
            # Ensure columns exist and have correct types
            if 'category' not in expenses_df.columns:
                expenses_df['category'] = 'Others'
            if 'amount' not in expenses_df.columns:
                expenses_df['amount'] = 0.0
            expenses_df['amount'] = expenses_df['amount'].astype(float)

        # Configure columns for st.data_editor
        expense_col_config = {
            "category": st.column_config.SelectboxColumn(
                "Category",
                options=st.session_state['categories'],
                required=True,
                width="medium"
            ),
            "amount": st.column_config.NumberColumn(
                "Amount ($)",
                min_value=0.0,
                format="$%.2f",
                required=True,
                width="medium"
            )
        }

        # Render the interactive data editor with dynamic rows enabled
        edited_expenses_df = st.data_editor(
            expenses_df,
            column_config=expense_col_config,
            num_rows="dynamic",
            use_container_width=True,
            key="expenses_editor"
        )

        # Convert back and save if changed
        new_expenses = edited_expenses_df.to_dict(orient='records')
        # Filter out incomplete rows (e.g. None values)
        new_expenses = [row for row in new_expenses if row.get('category') is not None and row.get('amount') is not None]
        
        if new_expenses != st.session_state['expenses']:
            st.session_state['expenses'] = new_expenses
            auto_save()
            st.rerun()

    # Investments tab (st.data_editor with dynamic rows and validations)
    with tab3:
        st.subheader('Track Your Investments')
        st.markdown("Manage your investment portfolio in the interactive table below. Add new rows or select and delete them as needed.")

        # Build DataFrame from session state
        investments_df = pd.DataFrame(st.session_state['investments'])
        if investments_df.empty:
            investments_df = pd.DataFrame(columns=['type', 'amount'])
        else:
            if 'type' not in investments_df.columns:
                investments_df['type'] = 'Stocks'
            if 'amount' not in investments_df.columns:
                investments_df['amount'] = 0.0
            investments_df['amount'] = investments_df['amount'].astype(float)

        # Configure columns
        investment_col_config = {
            "type": st.column_config.SelectboxColumn(
                "Investment Type",
                options=['Stocks', 'Bonds', 'Mutual Funds', 'Crypto', 'Real Estate', 'Gold', 'Others'],
                required=True,
                width="medium"
            ),
            "amount": st.column_config.NumberColumn(
                "Amount ($)",
                min_value=0.0,
                format="$%.2f",
                required=True,
                width="medium"
            )
        }

        # Render data editor
        edited_investments_df = st.data_editor(
            investments_df,
            column_config=investment_col_config,
            num_rows="dynamic",
            use_container_width=True,
            key="investments_editor"
        )

        # Sync back to session state
        new_investments = edited_investments_df.to_dict(orient='records')
        new_investments = [row for row in new_investments if row.get('type') is not None and row.get('amount') is not None]
        
        if new_investments != st.session_state['investments']:
            st.session_state['investments'] = new_investments
            auto_save()
            st.rerun()

    # Analytics tab
    with tab4:
        st.subheader('Analyze Your Finances')
        
        an_col1, an_col2 = st.columns(2)
        
        with an_col1:
            if st.session_state['expenses']:
                exp_df = pd.DataFrame(st.session_state['expenses'])
                expense_fig = px.pie(
                    exp_df, 
                    names='category', 
                    values='amount', 
                    title='Expense Distribution',
                    color_discrete_sequence=custom_colors
                )
                expense_fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=50, b=20, l=20, r=20)
                )
                st.plotly_chart(expense_fig, use_container_width=True)
            else:
                st.info("No expenses tracked yet. Go to 'Expenses' tab to add some.")

        with an_col2:
            if st.session_state['investments']:
                inv_df = pd.DataFrame(st.session_state['investments'])
                investment_fig = px.pie(
                    inv_df, 
                    names='type', 
                    values='amount', 
                    title='Investment Distribution',
                    color_discrete_sequence=custom_colors
                )
                investment_fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=50, b=20, l=20, r=20)
                )
                st.plotly_chart(investment_fig, use_container_width=True)
            else:
                st.info("No investments tracked yet. Go to 'Investments' tab to add some.")

    # Income tab (st.data_editor with dynamic rows and validations)
    with tab5:
        st.subheader('Track Your Income')
        st.markdown("Manage your income sources in the interactive table below. Add new rows or select and delete them as needed.")

        # Build DataFrame
        income_df = pd.DataFrame(st.session_state['income_sources'])
        if income_df.empty:
            income_df = pd.DataFrame(columns=['source', 'amount'])
        else:
            if 'source' not in income_df.columns:
                income_df['source'] = 'Salary'
            if 'amount' not in income_df.columns:
                income_df['amount'] = 0.0
            income_df['amount'] = income_df['amount'].astype(float)

        # Configure columns
        income_col_config = {
            "source": st.column_config.TextColumn(
                "Income Source",
                required=True,
                width="medium"
            ),
            "amount": st.column_config.NumberColumn(
                "Amount ($)",
                min_value=0.0,
                format="$%.2f",
                required=True,
                width="medium"
            )
        }

        # Render data editor
        edited_income_df = st.data_editor(
            income_df,
            column_config=income_col_config,
            num_rows="dynamic",
            use_container_width=True,
            key="income_editor"
        )

        # Sync back to session state
        new_income = edited_income_df.to_dict(orient='records')
        new_income = [row for row in new_income if row.get('source') is not None and row.get('amount') is not None]
        
        if new_income != st.session_state['income_sources']:
            st.session_state['income_sources'] = new_income
            auto_save()
            st.rerun()

    # Download Data tab
    with tab6:
        st.subheader('Download Your Financial Data')
        
        budget_df = pd.DataFrame({'Budget': [st.session_state['budget']], 'Savings Goal': [st.session_state['savings_goal_amount']], 'Goal Description': [st.session_state['savings_goal_desc']]})
        expenses_df = pd.DataFrame(st.session_state['expenses'])
        investments_df = pd.DataFrame(st.session_state['investments'])
        income_sources_df = pd.DataFrame(st.session_state['income_sources'])

        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False)

        budget_csv = convert_df(budget_df)
        expenses_csv = convert_df(expenses_df)
        investments_csv = convert_df(investments_df)
        income_sources_csv = convert_df(income_sources_df)

        down_col1, down_col2 = st.columns(2)
        with down_col1:
            st.download_button('Download Budget & Goal Data', budget_csv, file_name='budget_and_goals.csv', use_container_width=True)
            st.download_button('Download Expenses Data', expenses_csv, file_name='expenses.csv', use_container_width=True)
        with down_col2:
            st.download_button('Download Investments Data', investments_csv, file_name='investments.csv', use_container_width=True)
            st.download_button('Download Income Sources Data', income_sources_csv, file_name='income_sources.csv', use_container_width=True)