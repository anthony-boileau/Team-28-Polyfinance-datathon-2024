import streamlit as st
import re
from datetime import datetime

st.set_page_config(
    page_title="10k Intelligence",
    page_icon="📊",
)

# Initialize session state for storing ticker and year selection
if "ticker" not in st.session_state:
    st.session_state.ticker = "AAPL"
if "years" not in st.session_state:
    st.session_state.years = 1

st.write("# Welcome to 10k Intelligence! 📊")

# Move the input fields to the sidebar
with st.sidebar:
    st.write("## Configure Analysis")
    ticker = st.text_input('Enter Stock Ticker:', st.session_state.ticker).upper()
    years = st.selectbox('Select Number of Years:', options=[1, 2, 5], index=0)
    
    # Update session state when inputs change
    if ticker != st.session_state.ticker or years != st.session_state.years:
        st.session_state.ticker = ticker
        st.session_state.years = years
    
    st.success("Select a feature above.")

# Validate ticker format
if ticker and not re.match(r'^[A-Z0-9]{1,5}$', ticker):
    st.error("Invalid ticker format. Please enter a valid stock ticker (1-5 uppercase letters and numbers).")

# Main page content
st.markdown(
    f"""
    Currently analyzing: **{st.session_state.ticker}** for the past **{st.session_state.years}** year(s).
    
    This tool helps you analyze companies through:
    
    1. **📈 Financial Reports**: Comprehensive financial analysis including:
        - Technical indicators
        - Financial metrics
        - Quarterly performance
        - AI-generated insights
    
    2. **💬 AI Chat Assistant**: Interactive Q&A about company:
        - Performance
        - Leadership
        - Strategy
        - Historical events
    
    **👈 Select a feature from the sidebar** to get started!

    ### How to use
    1. Enter a stock ticker in the sidebar (currently: {st.session_state.ticker})
    2. Choose the time period (currently: {st.session_state.years} year(s))
    3. Analyze reports or chat with the AI assistant
    
    ### Data Sources
    - Market data from Yahoo Finance
    - Company reports and filings
    - News and public information
    """
)