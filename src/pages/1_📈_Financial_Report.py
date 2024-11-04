import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import asyncio
from transformer import Transformer
from api import API
from dbagent import DBagent

st.set_page_config(page_title="Financial Report", page_icon="📈")

st.markdown("# Financial Report Generator 📈")
st.sidebar.header("Financial Report")

# Initialize required classes
api = API()
transformer = Transformer()
dba = DBagent()

# Check if ticker and years are in session state
if "ticker" not in st.session_state or "years" not in st.session_state:
    st.error("Please select a ticker and time period on the home page first!")
    st.stop()

def call_transform(prompt, fromYear, ticker):
    t = Transformer()
    r = DBagent()
    context = r.get_context(prompt=prompt, fromYear=fromYear, ticker=ticker)
    response = t.transform(context=context, prompt=prompt)
    return response

async def fetch_report_data(ticker, fromYear):
    dba = DBagent()
    await dba.embed_company_over_daterange(ticker, fromYear)
    return True

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

def display_market_data(df):
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

def main():
    # Display current analysis parameters
    st.write(f"Analyzing **{st.session_state.ticker}** for the past **{st.session_state.years}** year(s)")
    
    try:
        # Create a placeholder for the status message
        status_placeholder = st.empty()
        status_placeholder.info('Loading data, please wait...')
        
        # Calculate fromYear
        fromYear = datetime.now().year - st.session_state.years + 1
        
        # Fetch company data for AI analysis
        ready = True #asyncio.run(fetch_report_data(st.session_state.ticker, fromYear))
        
        if not ready:
            st.error("Failed to load company data for AI analysis.")
            return

        # Fetch stock data
        stock_data = yf.Ticker(st.session_state.ticker)
        
        # Get historical data
        df = stock_data.history(period=f"{st.session_state.years}y")
        df.reset_index(inplace=True)
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Clear loading message
        status_placeholder.empty()
        
        # Create tabs for different sections
        tab_market, tab_financials, tab_ai = st.tabs([
            "Market Data", 
            "Financial Analysis", 
            "AI Insights"
        ])
        
        with tab_market:
            display_market_data(df)
            display_technical_analysis(df)
        
        with tab_financials:
            display_financial_metrics(stock_data.info)
            display_quarterly_analysis(stock_data)
        
        with tab_ai:
            st.write("## AI Analysis")
            
            # Financial Analysis Section
            st.write("### 💰 Financial Analysis")
            
            with st.expander("Company Metrics & Fundamentals", expanded=True):
                response = call_transform(
                    f"Analyze {st.session_state.ticker}'s key financial metrics, including revenue growth, profit margins, and cash flow trends since {fromYear}. Focus on fundamental strengths and weaknesses in their financial position.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)
            
            with st.expander("Historical Performance & Industry Standing"):
                response = call_transform(
                    f"Compare {st.session_state.ticker}'s historical performance against industry benchmarks since {fromYear}, including market share trends, competitive positioning, and key performance indicators relative to peers.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)
            
            with st.expander("Market Position & Growth Strategy"):
                response = call_transform(
                    f"Evaluate {st.session_state.ticker}'s market positioning, revenue streams, and growth strategy effectiveness since {fromYear}. Include analysis of market share, product portfolio, and strategic initiatives.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)

            # Leadership & Governance Section
            st.write("### 👥 Leadership & Governance")
            
            with st.expander("Executive Leadership Analysis"):
                response = call_transform(
                    f"Analyze {st.session_state.ticker}'s executive leadership team composition, experience, and effectiveness since {fromYear}. Include key leadership changes and their impact on company direction.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)
            
            with st.expander("Board & Governance Structure"):
                response = call_transform(
                    f"Evaluate {st.session_state.ticker}'s board composition, committee structure, and governance practices since {fromYear}. Include analysis of independence, diversity, and effectiveness of oversight.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)
            
            with st.expander("Corporate Culture & ESG Practices"):
                response = call_transform(
                    f"Assess {st.session_state.ticker}'s corporate culture, ESG initiatives, and compensation practices since {fromYear}. Include analysis of DE&I metrics, sustainability efforts, and alignment with company values.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)

            # Risk Assessment Section
            st.write("### ⚠️ Risk Assessment")
            
            with st.expander("Key Risk Factors"):
                response = call_transform(
                    f"Identify and analyze {st.session_state.ticker}'s primary risk factors since {fromYear}, including operational, financial, and strategic risks. Compare with industry peer risk profiles.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)
            
            with st.expander("Risk Mitigation Strategies"):
                response = call_transform(
                    f"Evaluate {st.session_state.ticker}'s risk mitigation strategies and their effectiveness since {fromYear}. Include analysis of risk management frameworks and adaptation to emerging threats.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)
            
            with st.expander("Future Risk Outlook"):
                response = call_transform(
                    f"Analyze emerging risks and future challenges facing {st.session_state.ticker}, including market trends, regulatory changes, and industry-specific factors that could impact performance.",
                    fromYear, st.session_state.ticker
                )
                st.markdown(response)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Please check if the ticker symbol is correct and try again.")

if __name__ == "__main__":
    main()