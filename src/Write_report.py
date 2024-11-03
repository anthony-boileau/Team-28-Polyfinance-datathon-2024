import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

if __name__ == '__main__':
    st.write("""
    # Company Report Generator
    Enter a ticker symbol to generate a report
    """)
    
    # Create ticker input
    ticker = st.text_input('Enter Stock Ticker:', 'AAPL').upper()
    
    if st.button('Generate Report'):
        # Get data from yfinance
        try:
            # Download stock data
            stock = yf.Ticker(ticker)
            df = stock.history(period='1y')
            
            # Display company info
            st.subheader(f'{ticker} Company Report')
            
            # Company info
            info = stock.info
            st.write('### Company Information')
            st.write(f"Company Name: {info.get('longName', 'N/A')}")
            st.write(f"Sector: {info.get('sector', 'N/A')}")
            st.write(f"Industry: {info.get('industry', 'N/A')}")
            
            # Stock price chart
            st.write('### Stock Price History')
            st.line_chart(df['Close'])
            
            # Basic statistics
            st.write('### Key Statistics')
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Current Price", f"${df['Close'][-1]:.2f}")
                st.metric("52-Week High", f"${df['High'].max():.2f}")
            
            with col2:
                st.metric("Volume", f"{df['Volume'][-1]:,}")
                st.metric("52-Week Low", f"${df['Low'].min():.2f}")
            
            # Calculate some technical indicators
            df['SMA_20'] = ta.sma(df['Close'], length=20)
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # Display technical indicators
            st.write('### Technical Indicators')
            st.write(f"20-day SMA: ${df['SMA_20'][-1]:.2f}")
            st.write(f"RSI (14): {df['RSI'][-1]:.2f}")
            
        except Exception as e:
            st.error(f'Error fetching data for {ticker}. Please check the ticker symbol.')
            st.write(f'Error details: {str(e)}')