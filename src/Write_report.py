import streamlit as st
import pandas as pd
import aiohttp
import asyncio
import pandas_ta as ta
from dotenv import load_dotenv
import os

# Load environment variables from secrets.txt file
load_dotenv(".secrets")

# Retrieve API key from environment
FMP_API_KEY = os.getenv("API_KEY")

# API URLs
YAHOO_FINANCE_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
FMP_COMPANY_INFO_URL = "https://financialmodelingprep.com/api/v3/profile/"
FMP_KEY_METRICS_URL = "https://financialmodelingprep.com/api/v3/key-metrics/"
FMP_KEY_GROWTH_METRICS_URL = "https://financialmodelingprep.com/api/v3/financial-growth/"

async def fetch_stock_data(ticker, session):
    url = f"{YAHOO_FINANCE_API_URL}{ticker}"
    params = {'interval': '1d', 'range': '1y'}
    async with session.get(url, params=params) as response:
        return await response.json()

async def fetch_company_info(ticker, session):
    url = f"{FMP_COMPANY_INFO_URL}{ticker}?apikey={FMP_API_KEY}"
    async with session.get(url) as response:
        return await response.json()

async def fetch_key_metrics(ticker, session):
    url = f"{FMP_KEY_METRICS_URL}{ticker}?period=annual&apikey={FMP_API_KEY}"
    async with session.get(url) as response:
        return await response.json()
    
async def fetch_financial_growth(ticker, session):
    url = f"{FMP_KEY_GROWTH_METRICS_URL}{ticker}?period=annual&apikey={FMP_API_KEY}"
    async with session.get(url) as response:
        return await response.json()

async def generate_report(ticker):
    async with aiohttp.ClientSession() as session:
        stock_data_task = fetch_stock_data(ticker, session)
        company_info_task = fetch_company_info(ticker, session)
        key_metrics_task = fetch_key_metrics(ticker, session)
        financial_growth_task = fetch_financial_growth(ticker, session)

        # Fetch stock data, company info, and key metrics concurrently
        # Fetch data concurrently
        stock_data, company_info, key_metrics, financial_growth = await asyncio.gather(
            stock_data_task, company_info_task, key_metrics_task, financial_growth_task
            )

        # Parse stock data
        if stock_data.get('chart', {}).get('result'):
            result = stock_data['chart']['result'][0]
            timestamps = result['timestamp']
            closes = result['indicators']['quote'][0]['close']
            highs = result['indicators']['quote'][0]['high']
            lows = result['indicators']['quote'][0]['low']
            volumes = result['indicators']['quote'][0]['volume']
            
            # Create DataFrame
            df = pd.DataFrame({
                'Date': pd.to_datetime(timestamps, unit='s'),
                'Close': closes,
                'High': highs,
                'Low': lows,
                'Volume': volumes
            }).set_index('Date')
            
            # Calculate technical indicators
            df['SMA_20'] = ta.sma(df['Close'], length=20)
            df['RSI'] = ta.rsi(df['Close'], length=14)

            # Calculate MACD and Signal Line
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
            obv_trend = "Increasing" if df['OBV'].iloc[-1] > df['OBV'].iloc[-2] else "Decreasing"

        else:
            st.error(f"Error fetching stock data for {ticker}.")
            return

        # Parse company info
        if company_info and isinstance(company_info, list) and len(company_info) > 0:
            info = company_info[0]
            company_name = info.get('companyName', 'Information not available')
            sector = info.get('sector', 'Information not available')
            industry = info.get('industry', 'Information not available')
        else:
            st.warning(f"Company information for {ticker} could not be retrieved.")
            company_name, sector, industry = "N/A", "N/A", "N/A"

        # Display company and stock information
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
        st.write(f"Latest MACD: {df['MACD'][-1]:.2f}")
        st.write(f"Latest OBV: {df['OBV'].iloc[-1]:.2f} ({obv_trend})")

        st.write('### MACD Indicator')
        st.line_chart(df[['MACD', 'Signal_Line']])

        st.write('### OBV Indicator')
        st.line_chart(df['OBV'])

        # Display Financial Performance
        if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0:
            latest_metrics = key_metrics[0]
            st.subheader('Financial Performance')
            st.write('### Key Financial Metrics')
            st.write(f"Revenue Per Share: ${latest_metrics.get('revenuePerShare', 'N/A')}")
            st.write(f"Net Income Per Share: ${latest_metrics.get('netIncomePerShare', 'N/A')}")
            st.write(f"PE Ratio: {latest_metrics.get('peRatio', 'N/A')}")
            st.write(f"Market Cap: ${latest_metrics.get('marketCap', 'N/A')}")
            st.write(f"Enterprise Value: ${latest_metrics.get('enterpriseValue', 'N/A')}")
            st.write(f"Free Cash Flow Yield: {latest_metrics.get('freeCashFlowYield', 'N/A')}")
            st.write(f"Debt to Equity: {latest_metrics.get('debtToEquity', 'N/A')}")
            st.write(f"Current Ratio: {latest_metrics.get('currentRatio', 'N/A')}")
            st.write(f"ROE: {latest_metrics.get('roe', 'N/A')}")
        else:
            st.warning("Key financial metrics could not be retrieved.")

        # Parse financial growth data
        if financial_growth and isinstance(financial_growth, list) and len(financial_growth) > 0:
            growth_data = financial_growth[0]
            st.subheader('Financial Growth Overview')

            # Display key growth metrics with explanation
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Revenue Growth", f"{growth_data['revenueGrowth'] * 100:.2f}%", "YoY")
                st.metric("Net Income Growth", f"{growth_data['netIncomeGrowth'] * 100:.2f}%", "YoY")
                st.metric("Operating Cash Flow Growth", f"{growth_data['operatingCashFlowGrowth'] * 100:.2f}%", "YoY")
            with col2:
                st.metric("Free Cash Flow Growth", f"{growth_data['freeCashFlowGrowth'] * 100:.2f}%", "YoY")
                st.metric("Dividends per Share Growth", f"{growth_data['dividendsperShareGrowth'] * 100:.2f}%", "YoY")
                st.metric("Equity Growth", f"{growth_data['tenYShareholdersEquityGrowthPerShare'] * 100:.2f}%", "10Y Avg")

        else:
            st.warning("Financial growth data for this company is not available.")


if __name__ == '__main__':
    st.write("# Company Report Generator")
    ticker = st.text_input('Enter Stock Ticker:', 'AAPL').upper()
    if st.button('Generate Report'):
        asyncio.run(generate_report(ticker))
        
