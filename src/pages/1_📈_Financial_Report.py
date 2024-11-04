
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="Financial Report", page_icon="📈")

st.markdown("# Financial Report Generator 📈")
st.sidebar.header("Financial Report")

# Check if ticker and years are in session state
if "ticker" not in st.session_state or "years" not in st.session_state:
    st.error("Please select a ticker and time period on the home page first!")
    st.stop()

def calculate_technical_indicators(df):
    """Calculate technical indicators for the dataframe"""
    if len(df) == 0:
        return df
    
    # Calculate indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['Signal_Line'] = macd['MACDs_12_26_9']
    
    # Calculate OBV
    df['OBV'] = (df['Close'] - df['Close'].shift(1)).apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)) * df['Volume']
    df['OBV'] = df['OBV'].cumsum()
    
    return df

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

def main():
    # Display current analysis parameters
    st.write(f"Analyzing **{st.session_state.ticker}** for the past **{st.session_state.years}** year(s)")
    
    try:
        # Create a placeholder for the status message
        status_placeholder = st.empty()
        status_placeholder.info('Loading data, please wait...')

        # Fetch stock data
        stock_data = yf.Ticker(st.session_state.ticker)
        
        # Get historical data
        df = stock_data.history(period=f"{st.session_state.years}y")
        df.reset_index(inplace=True)
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Clear loading message
        status_placeholder.empty()
        
        # Display all analyses
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
            st.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
        with col2:
            price_change = df['Close'].iloc[-1] - df['Close'].iloc[0]
            price_change_pct = (price_change / df['Close'].iloc[0]) * 100
            st.metric("Price Change", f"${price_change:.2f}", f"{price_change_pct:.1f}%")
        
        # Stock price chart
        st.write("### Stock Price History")
        st.line_chart(df.set_index('Date')['Close'])
        
        display_technical_analysis(df)
        display_financial_metrics(stock_data.info)
        display_quarterly_analysis(stock_data)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Please check if the ticker symbol is correct and try again.")

if __name__ == "__main__":
    main()