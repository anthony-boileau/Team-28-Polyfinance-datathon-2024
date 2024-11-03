import streamlit as st
import pandas as pd
import aiohttp
import asyncio
import pandas_ta as ta
from dotenv import load_dotenv
import os

# Load environment variables from .secrets file
load_dotenv(".secrets")
FMP_API_KEY = os.getenv("API_KEY")

# API URLs
YAHOO_FINANCE_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
FMP_COMPANY_INFO_URL = "https://financialmodelingprep.com/api/v3/profile/"

async def fetch_stock_data(ticker, session):
    url = f"{YAHOO_FINANCE_API_URL}{ticker}"
    params = {'interval': '1d', 'range': '1y'}
    async with session.get(url, params=params) as response:
        return await response.json()

async def fetch_company_info(ticker, session):
    if FMP_API_KEY:  # Check if the API key is present
        url = f"{FMP_COMPANY_INFO_URL}{ticker}?apikey={FMP_API_KEY}"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                st.warning(f"Failed to retrieve data from FMP for {ticker}. Status code: {response.status}")
    else:
        st.warning("API key is missing or invalid.")
    return None

async def generate_report(ticker):
    async with aiohttp.ClientSession() as session:
        stock_data_task = fetch_stock_data(ticker, session)
        company_info_task = fetch_company_info(ticker, session)
        
        stock_data, company_info = await asyncio.gather(stock_data_task, company_info_task)

        # Parse stock data
        if stock_data.get('chart', {}).get('result'):
            result = stock_data['chart']['result'][0]
            timestamps = result['timestamp']
            closes = result['indicators']['quote'][0]['close']
            highs = result['indicators']['quote'][0]['high']
            lows = result['indicators']['quote'][0]['low']
            volumes = result['indicators']['quote'][0]['volume']
            
            df = pd.DataFrame({
                'Date': pd.to_datetime(timestamps, unit='s'),
                'Close': closes,
                'High': highs,
                'Low': lows,
                'Volume': volumes
            }).set_index('Date')
            
            df['SMA_20'] = ta.sma(df['Close'], length=20)
            df['RSI'] = ta.rsi(df['Close'], length=14)
        else:
            st.error(f"Error fetching stock data for {ticker}.")
            return

        # Parse company info with error handling
        if company_info and isinstance(company_info, list) and len(company_info) > 0:
            info = company_info[0]
            company_name = info.get('companyName', 'Information not available')
            sector = info.get('sector', 'Information not available')
            industry = info.get('industry', 'Information not available')
        else:
            st.warning(f"Company information for {ticker} could not be retrieved.")
            company_name, sector, industry = "N/A", "N/A", "N/A"

        # Display data in Streamlit
        st.subheader(f'{ticker} Company Report')
        st.write('### Company Information')
        st.write(f"Company Name: {company_name}")
        st.write(f"Sector: {sector}")
        st.write(f"Industry: {industry}")
        
        st.write('### Stock Price History')
        st.line_chart(df['Close'])
        
        st.write('### Key Statistics')
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Price", f"${df['Close'][-1]:.2f}")
            st.metric("52-Week High", f"${df['High'].max():.2f}")
        with col2:
            st.metric("Volume", f"{df['Volume'][-1]:,}")
            st.metric("52-Week Low", f"${df['Low'].min():.2f}")
        
        st.write('### Technical Indicators')
        st.write(f"20-day SMA: ${df['SMA_20'][-1]:.2f}")
        st.write(f"RSI (14): {df['RSI'][-1]:.2f}")

if __name__ == '__main__':
    st.write("""
    # Company Report Generator
    Enter a ticker symbol to generate a report
    """)
    
    ticker = st.text_input('Enter Stock Ticker:', 'AAPL').upper()

    if st.button('Generate Report'):
        asyncio.run(generate_report(ticker))