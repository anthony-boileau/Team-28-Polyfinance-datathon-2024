import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import re
from transformer import Transformer

def section(prompt):
    lc_transformer = Transformer()
    response = lc_transformer.transform(prompt)
    return response


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

    # Display debt breakdown as a bar chart
    st.write('### Debt Breakdown')
    debt_df = pd.DataFrame.from_dict(debt_breakdown, orient='index', columns=['Amount'])
    st.bar_chart(debt_df)

    # Compare Revenue and Earnings
    st.subheader('Revenue vs Earnings Comparison (Most Recent Annual Figures)')
    
    income_statement = stock_data.financials
    try:
        revenue = income_statement.loc['Total Revenue'].values[0] if 'Total Revenue' in income_statement.index else 0
        earnings = income_statement.loc['Gross Profit'].values[0] if 'Gross Profit' in income_statement.index else 0
        
        # Create a bar chart for Revenue vs Earnings
        comparison_df = pd.DataFrame({'Amount': [revenue, earnings]}, index=['Revenue', 'Earnings'])
        st.bar_chart(comparison_df)
    except KeyError as e:
        st.write(f"Error fetching data: {e}")

    # Quarterly Revenue vs. Earnings Comparison
    st.write("### Quarterly Revenue vs. Earnings Over Time")
    try:
        quarterly_financials = stock_data.quarterly_financials
        revenue_quarterly = quarterly_financials.loc['Total Revenue']
        earnings_quarterly = quarterly_financials.loc['Net Income']

        # Sort by date to ensure chronological ordering
        revenue_quarterly = revenue_quarterly.sort_index(ascending=True)
        earnings_quarterly = earnings_quarterly.sort_index(ascending=True)

        # Combine revenue and earnings into a single DataFrame
        quarterly_df = pd.DataFrame({'Revenue': revenue_quarterly, 'Earnings': earnings_quarterly})
        st.line_chart(quarterly_df)
    except KeyError as e:
        st.write(f"Error fetching quarterly data: {e}")

    st.write(f"### Leadership Change over the past {years} year(s)")
    st.write(section(f"State the leadership change in the last {years} and if there were none, answer in one line."))

    st.write("### Company composition")
    st.write(section("State each executive's name followed by leadership position in parentheses, and if they are in any other board positions. If not, do not write anything."))

    st.write("### Commitees")
    st.write(section("State each leadership position in parentheses, followed by salary."))

if __name__ == '__main__':
    st.write("# Company Report Generator")
    ticker = st.text_input('Enter Stock Ticker:', 'AAPL').upper()
    years = st.selectbox('Select Number of Years:', options=[1, 2, 5], index=0)

    if ticker and not re.match(r'^[A-Z0-9]{1,5}$', ticker):
        st.error("Invalid ticker format. Please enter a valid stock ticker (1-5 uppercase letters and numbers).")
    elif st.button('Generate Report'):
        generate_report(ticker, years)