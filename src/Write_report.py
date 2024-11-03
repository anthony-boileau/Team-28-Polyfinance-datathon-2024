import streamlit as st 
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import re
import matplotlib.pyplot as plt

def generate_report(ticker, years):
    # Fetch stock data
    stock_data = yf.Ticker(ticker)
    
    # Historical market data based on user-selected years
    period = f"{years}y"
    df = stock_data.history(period=period)
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

    # Fetch company info
    info = stock_data.info
    company_name = info.get('longName', 'Information not available')
    sector = info.get('sector', 'Information not available')
    industry = info.get('industry', 'Information not available')

    # Display company and stock information
    st.subheader(f'{ticker} Company Report')
    st.write('### Company Information')
    st.write(f"Company Name: {company_name}")
    st.write(f"Sector: {sector}")
    st.write(f"Industry: {industry}")

    st.write('### Stock Price History')
    st.line_chart(df.set_index('Date')['Close'])

    st.write('### Key Statistics')
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}")
        st.metric("52-Week High", f"${df['High'].max():.2f}")
    with col2:
        st.metric("Volume", f"{df['Volume'].iloc[-1]:,}")
        st.metric("52-Week Low", f"${df['Low'].min():.2f}")

    st.write('### Technical Indicators')
    st.write(f"20-day SMA: ${df['SMA_20'].iloc[-1]:.2f}")
    st.write(f"RSI (14): {df['RSI'].iloc[-1]:.2f}")
    st.write(f"Latest MACD: {df['MACD'].iloc[-1]:.2f}")
    st.write(f"Latest OBV: {df['OBV'].iloc[-1]:.2f}")

    st.write('### MACD Indicator')
    st.line_chart(df.set_index('Date')[['MACD', 'Signal_Line']])

    st.write('### OBV Indicator')
    st.line_chart(df.set_index('Date')['OBV'])

    # Financial metrics from yfinance
    st.subheader('Financial Performance')
    st.write('### Key Financial Metrics')
    revenue_per_share = info.get('revenuePerShare', 'N/A')
    net_income_per_share = info.get('netIncomePerShare', 'N/A')
    pe_ratio = info.get('forwardPE', 'N/A')
    market_cap = info.get('marketCap', 'N/A')
    enterprise_value = info.get('enterpriseValue', 'N/A')
    free_cash_flow_yield = info.get('freeCashFlowYield', 'N/A')
    debt_to_equity = info.get('debtToEquity', 'N/A')
    current_ratio = info.get('currentRatio', 'N/A')
    roe = info.get('returnOnEquity', 'N/A')

    st.write(f"Revenue Per Share: ${revenue_per_share}")
    st.write(f"Net Income Per Share: ${net_income_per_share}")
    st.write(f"PE Ratio: {pe_ratio}")
    st.write(f"Market Cap: {market_cap}")
    st.write(f"Enterprise Value: {enterprise_value}")
    st.write(f"Free Cash Flow Yield: {free_cash_flow_yield}")
    st.write(f"Debt to Equity: {debt_to_equity}")
    st.write(f"Current Ratio: {current_ratio}")
    st.write(f"ROE: {roe}")

    # Fetch balance sheet
    balance_sheet = stock_data.balance_sheet

    # Print balance sheet for inspection
    st.write('### Balance Sheet')
    st.write(balance_sheet)

    # Prepare debt breakdown
    debt_breakdown = {}
    try:
        short_term_debt = balance_sheet.loc['Short Term Debt'].values[0] if 'Short Term Debt' in balance_sheet.index else 0
        debt_breakdown['Short Term Debt'] = short_term_debt if pd.notna(short_term_debt) else 0
    except KeyError:
        debt_breakdown['Short Term Debt'] = 0

    try:
        long_term_debt = balance_sheet.loc['Long Term Debt'].values[0] if 'Long Term Debt' in balance_sheet.index else 0
        debt_breakdown['Long Term Debt'] = long_term_debt if pd.notna(long_term_debt) else 0
    except KeyError:
        debt_breakdown['Long Term Debt'] = 0

    # Display debt breakdown
    st.write('### Debt Breakdown')
    st.write(debt_breakdown)

    # Create a pie chart for debt breakdown
    labels = debt_breakdown.keys()
    sizes = list(debt_breakdown.values())
    colors = ['#ff9999','#66b3ff']  # Color palette for pie chart

    # Check if both sizes are zero, which would cause an issue
    if all(size == 0 for size in sizes):
        st.write("Insufficient data to display debt breakdown.")
    else:
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        st.write('### Debt Breakdown Pie Chart')
        st.pyplot(fig)  # Display the pie chart in the Streamlit app

    # Compare Revenue and Earnings
    st.subheader('Revenue vs Earnings Comparison')
    
    # Assuming you have the earnings data in a suitable format
    # For example, you could use the income statement:
    income_statement = stock_data.financials
    try:
        revenue = income_statement.loc['Total Revenue'].values[0] if 'Total Revenue' in income_statement.index else 0
        earnings = income_statement.loc['Gross Profit'].values[0] if 'Gross Profit' in income_statement.index else 0
        
        # Create a bar plot to compare Revenue and Earnings
        fig, ax = plt.subplots()
        ax.bar(['Revenue', 'Earnings'], [revenue, earnings], color=['#66b3ff', '#ff9999'])
        ax.set_ylabel('Amount in USD')
        ax.set_title('Comparison of Revenue and Earnings')
        
        st.pyplot(fig)  # Display the bar plot in the Streamlit app
    except KeyError as e:
        st.write(f"Error fetching data: {e}")

if __name__ == '__main__':
    st.write("# Company Report Generator")
    ticker = st.text_input('Enter Stock Ticker:', 'AAPL').upper()
    
    # User input for number of years
    years = st.slider('Select Number of Years:', 1, 5, 1)  # Default is 1 year
    
    # User input validation
    if ticker and not re.match(r'^[A-Z0-9]{1,5}$', ticker):  # Only allow 1-5 uppercase letters or numbers
        st.error("Invalid ticker format. Please enter a valid stock ticker (1-5 uppercase letters and numbers).")
    elif st.button('Generate Report'):
        generate_report(ticker, years)

