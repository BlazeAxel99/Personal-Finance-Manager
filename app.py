# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from bcrypt import hashpw, gensalt, checkpw

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'budget' not in st.session_state:
    st.session_state['budget'] = 0
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []
if 'investments' not in st.session_state:
    st.session_state['investments'] = []
if 'categories' not in st.session_state:
    st.session_state['categories'] = ['Food', 'Transportation', 'Entertainment']
if 'current_savings' not in st.session_state:
    st.session_state['current_savings'] = 0
if 'income_sources' not in st.session_state:
    st.session_state['income_sources'] = []

# File to store user data
USER_DATA_FILE = 'user_data.pkl'

# Load user data
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {}

# Save user data
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'wb') as file:
        pickle.dump(user_data, file)

# Hash password
def hash_password(password):
    return hashpw(password.encode(), gensalt())

# Verify password
def verify_password(password, hashed):
    return checkpw(password.encode(), hashed)

# User registration
def register_user(username, password):
    user_data = load_user_data()
    if username in user_data:
        return False  # Username already exists
    user_data[username] = {
        'password': hash_password(password),
        'budget': 0,
        'expenses': [],
        'investments': [],
        'categories': ['Food', 'Transportation', 'Entertainment'],
        'income_sources': [],
        'current_savings': 0,
    }
    save_user_data(user_data)
    return True

# Load saved data for the logged-in user
def load_user_session(username):
    user_data = load_user_data()
    user = user_data.get(username, {})
    st.session_state['budget'] = user.get('budget', 0)
    st.session_state['expenses'] = user.get('expenses', [])
    st.session_state['investments'] = user.get('investments', [])
    st.session_state['categories'] = user.get('categories', ['Food', 'Transportation', 'Entertainment'])
    st.session_state['income_sources'] = user.get('income_sources', [])
    st.session_state['current_savings'] = user.get('current_savings', 0)

# Save data for the logged-in user
def save_user_session(username):
    user_data = load_user_data()
    if username in user_data:
        user_data[username] = {
            'password': user_data[username]['password'],
            'budget': st.session_state['budget'],
            'expenses': st.session_state['expenses'],
            'investments': st.session_state['investments'],
            'categories': st.session_state['categories'],
            'income_sources': st.session_state['income_sources'],
            'current_savings': st.session_state['current_savings'],
        }
        save_user_data(user_data)

# Streamlit app
st.title('💰 Personal Finance Manager')

# Login and Registration Page
if not st.session_state['logged_in']:
    st.header('Welcome! Please Login or Register')

    option = st.radio('Select an option', ['Login', 'Register'])

    if option == 'Login':
        input_username = st.text_input('Username', key='login_username')
        input_password = st.text_input('Password', type='password', key='login_password')
        if st.button('Login'):
            user_data = load_user_data()
            if input_username in user_data and verify_password(input_password, user_data[input_username]['password']):
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = input_username
                load_user_session(input_username)
                st.success(f"Welcome back, {input_username}!")
            else:
                st.error('Invalid username or password')

    elif option == 'Register':
        new_username = st.text_input('Choose a username', key='register_username')
        new_password = st.text_input('Choose a password', type='password', key='register_password')
        if st.button('Register'):
            if register_user(new_username, new_password):
                st.success('User registered successfully! Please login.')
            else:
                st.error('Username already exists. Please choose a different one.')

# Main app functionality
else:
    st.header(f'Welcome, {st.session_state["current_user"]}!')

    # Create tabs for navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        '💼 Budget', '🛒 Expenses', '📈 Investments', '📊 Analytics', '💵 Income', '📥 Download Data'
    ])

    # Budget tab
    with tab1:
        st.subheader('Set Your Budget')
        budget = st.number_input('Enter your monthly budget:', min_value=0, key='budget_input')
        st.session_state['budget'] = budget
        st.success(f'Your budget is set to {st.session_state["budget"]}')

        # Goal setting
        st.subheader('Set Your Savings Goal')
        goal_description = st.text_input('Goal Description:')
        goal_amount = st.number_input('Goal Amount:', min_value=0, key='goal_amount')
        st.progress(st.session_state['current_savings'] / max(1, goal_amount))

    # Expenses tab
    with tab2:
        st.subheader('Track Your Expenses')
        expense_category = st.selectbox('Select Expense Category:', st.session_state['categories'])
        expense_amount = st.number_input('Expense Amount:', min_value=0)
        if st.button('Add Expense'):
            st.session_state['expenses'].append({'category': expense_category, 'amount': expense_amount})
            st.success('Expense added successfully!')

        st.write('**Your Expenses:**')
        for i, expense in enumerate(st.session_state['expenses']):
            st.write(f'{i+1}. {expense["category"]}: {expense["amount"]}')

    # Investments tab
    with tab3:
        st.subheader('Track Your Investments')
        investment_type = st.selectbox('Investment Type:', ['Stocks', 'Bonds', 'Mutual Funds'])
        investment_amount = st.number_input('Investment Amount:', min_value=0)
        if st.button('Add Investment'):
            st.session_state['investments'].append({'type': investment_type, 'amount': investment_amount})
            st.success('Investment added successfully!')

        st.write('**Your Investments:**')
        for i, investment in enumerate(st.session_state['investments']):
            st.write(f'{i+1}. {investment["type"]}: {investment["amount"]}')

    # Analytics tab
    with tab4:
        st.subheader('Analyze Your Finances')
        if st.session_state['expenses']:
            expense_df = pd.DataFrame(st.session_state['expenses'])
            expense_fig = px.pie(expense_df, names='category', values='amount', title='Expense Distribution')
            st.plotly_chart(expense_fig)

        if st.session_state['investments']:
            investment_df = pd.DataFrame(st.session_state['investments'])
            investment_fig = px.pie(investment_df, names='type', values='amount', title='Investment Distribution')
            st.plotly_chart(investment_fig)

    # Income tab
    with tab5:
        st.subheader('Track Your Income')
        income_source = st.text_input('Income Source:')
        income_amount = st.number_input('Income Amount:', min_value=0)
        if st.button('Add Income'):
            st.session_state['income_sources'].append({'source': income_source, 'amount': income_amount})
            st.success('Income source added successfully!')

        st.write('**Your Income Sources:**')
        for i, income in enumerate(st.session_state['income_sources']):
            st.write(f'{i+1}. {income["source"]}: {income["amount"]}')

    # Download Data tab
    with tab6:
        st.subheader('Download Your Financial Data')

        budget_df = pd.DataFrame({'Budget': [st.session_state['budget']]})
        expenses_df = pd.DataFrame(st.session_state['expenses'])
        investments_df = pd.DataFrame(st.session_state['investments'])
        income_sources_df = pd.DataFrame(st.session_state['income_sources'])

        @st.cache
        def convert_df(df):
            return df.to_csv(index=False)

        budget_csv = convert_df(budget_df)
        expenses_csv = convert_df(expenses_df)
        investments_csv = convert_df(investments_df)
        income_sources_csv = convert_df(income_sources_df)

        st.download_button('Download Budget Data', budget_csv, file_name='budget.csv')
        st.download_button('Download Expenses Data', expenses_csv, file_name='expenses.csv')
        st.download_button('Download Investments Data', investments_csv, file_name='investments.csv')
        st.download_button('Download Income Sources Data', income_sources_csv, file_name='income_sources.csv')

    # Logout button
    if st.button('Logout'):
        save_user_session(st.session_state['current_user'])
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.success('You have been logged out.')