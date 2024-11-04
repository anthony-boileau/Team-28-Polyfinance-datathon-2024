import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import re
from transformer import Transformer
from api import API
from dbagent import DBagent
import aiohttp
import asyncio
from datetime import datetime

def call_transform(prompt, fromYear, ticker):
    t = Transformer()
    r = DBagent()
    context = r.get_context(prompt=prompt, fromYear=fromYear, ticker=ticker)
    response = t.transform(context=context, prompt=prompt)
    return response

async def fetch_report_data(ticker, fromYear):
    dba = DBagent()
    dba.embed_company_over_daterange(ticker, fromYear)
    return True

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ticker" not in st.session_state:
        st.session_state.ticker = None
    if "from_year" not in st.session_state:
        st.session_state.from_year = None

def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def display_technical_analysis(df):
    st.write('### Technical Analysis')
    
    # Technical indicators
    col1, col2 = st.columns(2)
    with col1:
        st.metric("20-day SMA", f"${df['SMA_20'].iloc[-1]:.2f}")
        st.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
    with col2:
        st.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")
        st.metric("Latest OBV", f"{df['OBV'].iloc[-1]:,.0f}")

    # MACD Chart
    st.write('### MACD Indicator')
    st.line_chart(df.set_index('Date')[['MACD', 'Signal_Line']])

    # OBV Chart
    st.write('### On-Balance Volume (OBV)')
    st.line_chart(df.set_index('Date')['OBV'])

def display_financial_metrics(info):
    st.write('### Key Financial Metrics')
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Revenue Per Share", f"${info.get('revenuePerShare', 'N/A')}")
        st.metric("Net Income Per Share", f"${info.get('netIncomePerShare', 'N/A')}")
        st.metric("PE Ratio", info.get('forwardPE', 'N/A'))
        st.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,.0f}")
    
    with col2:
        st.metric("Debt to Equity", info.get('debtToEquity', 'N/A'))
        st.metric("Current Ratio", info.get('currentRatio', 'N/A'))
        st.metric("ROE", f"{info.get('returnOnEquity', 'N/A')*100:.1f}%" if info.get('returnOnEquity') else 'N/A')
        st.metric("Free Cash Flow Yield", f"{info.get('freeCashFlowYield', 'N/A')}%")

def display_quarterly_analysis(stock_data):
    st.write("### Quarterly Performance")
    try:
        quarterly_financials = stock_data.quarterly_financials
        
        # Revenue analysis
        if 'Total Revenue' in quarterly_financials.index:
            revenue_quarterly = quarterly_financials.loc['Total Revenue'].sort_index()
            st.write("#### Quarterly Revenue Trend")
            st.line_chart(revenue_quarterly)
            
            # Calculate QoQ growth
            revenue_growth = revenue_quarterly.pct_change() * 100
            st.write("Quarter-over-Quarter Revenue Growth:")
            st.line_chart(revenue_growth)

        # Earnings analysis
        if 'Net Income' in quarterly_financials.index:
            earnings_quarterly = quarterly_financials.loc['Net Income'].sort_index()
            st.write("#### Quarterly Earnings Trend")
            st.line_chart(earnings_quarterly)
            
            # Revenue vs Earnings comparison
            if 'Total Revenue' in quarterly_financials.index:
                comparison_df = pd.DataFrame({
                    'Revenue': quarterly_financials.loc['Total Revenue'],
                    'Net Income': quarterly_financials.loc['Net Income']
                }).sort_index()
                st.write("#### Revenue vs Earnings Comparison")
                st.line_chart(comparison_df)
    
    except Exception as e:
        st.error(f"Error in quarterly analysis: {str(e)}")

def generate_report(ticker, years):
    fromYear = datetime.now().year-years+1
    
    # Create a placeholder for the status message
    status_placeholder = st.empty()
    status_placeholder.markdown('<span style="color: red;">Loading data, please wait...</span>', unsafe_allow_html=True)

    # Store ticker and fromYear in session state for chat
    st.session_state.ticker = ticker
    st.session_state.from_year = fromYear

    ready = asyncio.run(fetch_report_data(ticker, fromYear))

    if ready:
        status_placeholder.markdown('<span style="color: green;">Data loaded! You can now ask questions below.</span>', unsafe_allow_html=True)

        # Fetch stock data
        stock_data = yf.Ticker(ticker)
        
        # Get historical data
        df = stock_data.history(period=f"{years}y")
        df.reset_index(inplace=True)

        # Calculate technical indicators
        df['SMA_20'] = ta.sma(df['Close'], length=20)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'])
        df['MACD'] = macd['MACD_12_26_9']
        df['Signal_Line'] = macd['MACDs_12_26_9']

        # Calculate OBV
        obv = [0]
        for i in range(1, len(df)):
            if df['Close'][i] > df['Close'][i-1]:
                obv.append(obv[-1] + df['Volume'][i])
            elif df['Close'][i] < df['Close'][i-1]:
                obv.append(obv[-1] - df['Volume'][i])
            else:
                obv.append(obv[-1])
        df['OBV'] = obv

        # Get company info
        info = stock_data.info
        company_name = info.get('longName', 'Information not available')
        
        # Display company overview
        st.write(f"## {company_name} ({ticker}) Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
            st.metric("52-Week High", f"${df['High'].max():.2f}")
        with col2:
            st.metric("Trading Volume", f"{df['Volume'].iloc[-1]:,}")
            st.metric("52-Week Low", f"${df['Low'].min():.2f}")

        # Stock price chart
        st.write('### Stock Price History')
        st.line_chart(df.set_index('Date')['Close'])

        # Display technical analysis
        display_technical_analysis(df)
        
        # Display financial metrics
        display_financial_metrics(info)
        
        # Display quarterly analysis
        display_quarterly_analysis(stock_data)

        # Generated sections using call_transform
        st.write("## AI-Generated Analysis")
        
        with st.expander("Leadership Changes"):
            response = call_transform(f"Summarize leadership changes in the last {years} years.", fromYear, ticker)
            st.write(response)
            
        with st.expander("Executive Composition"):
            response = call_transform("List the current executive team and their positions.", fromYear, ticker)
            st.write(response)
            
        with st.expander("Board Committees"):
            response = call_transform("Describe the current board committee structure.", fromYear, ticker)
            st.write(response)

        # Chat interface
        st.write("## Ask Questions About the Company")
        st.write("Use the chat below to ask specific questions about the company's performance, leadership, strategy, or any other aspect.")
        
        display_chat_history()

        if prompt := st.chat_input("What would you like to know about the company?"):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                response = call_transform(prompt, fromYear, ticker)
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    st.set_page_config(page_title="Company Analysis & Chat", layout="wide")
    
    st.title("Interactive Company Analysis with AI Chat")
    st.write("Enter a stock ticker and time period to analyze a company. Once the data is loaded, you can ask questions about any aspect of the company.")
    
    initialize_chat_history()

    # Sidebar for inputs
    with st.sidebar:
        st.header("Analysis Parameters")
        ticker = st.text_input('Enter Stock Ticker:', 'AAPL').upper()
        years = st.selectbox('Analysis Timeframe (Years):', options=[1, 2, 5], index=0)
        
        if st.button('Generate Analysis', use_container_width=True):
            if not re.match(r'^[A-Z0-9]{1,5}$', ticker):
                st.error("Invalid ticker format. Please enter a valid stock ticker (1-5 uppercase letters/numbers).")
            else:
                generate_report(ticker, years)
        
        st.divider()
        st.write("### About")
        st.write("""
        This tool combines financial analysis with AI-powered insights. You can:
        - View technical and fundamental analysis
        - Track performance metrics
        - Chat with AI about any aspect of the company
        - Get insights about leadership and strategy
        """)

    # If there's already a ticker loaded, show the chat interface
    if st.session_state.ticker:
        if prompt := st.chat_input("Ask a question about the company..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                response = call_transform(prompt, st.session_state.from_year, st.session_state.ticker)
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    api = API()
    transformer = Transformer()
    dba = DBagent()
    main()