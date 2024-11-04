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

        # Chat interface
        st.write("## Ask Questions About your Data")
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

        # AI-Generated Analysis
        st.write("## AI-Generated Analysis")

        # Financial Analysis Section
        st.write("### Financial Analysis")
        
        with st.expander("Company Metrics & Fundamentals"):
            response = call_transform(
                f"Analyze the company's key financial metrics including revenue growth, profit margins, and cash flow trends. Compare current ratios against historical averages and highlight any significant deviations or trends. Include specific figures and percentage changes where available.",
                fromYear,
                ticker
            )
            st.write(response)
        
        with st.expander("Historical Performance"):
            response = call_transform(
                f"Provide a detailed analysis of the company's performance over the past {years} years, focusing on year-over-year growth rates, operational efficiency metrics, and capital allocation decisions. Include specific milestone achievements and setbacks.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Industry Comparisons"):
            response = call_transform(
                "Compare the company's financial performance metrics against its primary industry competitors, focusing on market share, revenue growth rates, and profitability margins. Identify areas where the company leads or lags its peers.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("KPI Monitoring"):
            response = call_transform(
                "Analyze the company's performance against its stated key performance indicators, including both financial and operational metrics. Detail any significant changes in KPI achievement rates and explain potential underlying factors.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Market Positioning"):
            response = call_transform(
                "Evaluate the company's current market position, including market share trends, competitive advantages, and strategic positioning within its industry. Include analysis of brand strength and customer relationship metrics where available.",
                fromYear,
                ticker
            )
            st.write(response)

        # Leadership & Governance Section
        st.write("### Leadership & Governance")
        
        with st.expander("Board Composition"):
            response = call_transform(
                "Analyze the current board composition, including member backgrounds, expertise distribution, and independence status. Detail any recent changes and evaluate the board's diversity across various dimensions.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Executive Leadership Profiles"):
            response = call_transform(
                "Provide comprehensive profiles of key executive team members, including their experience, achievements since joining, and significant decisions or initiatives they've led. Include any notable changes in leadership structure or responsibilities.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Committee Structure"):
            response = call_transform(
                "Detail the current board committee structure, including each committee's composition, primary responsibilities, and key decisions or recommendations made in the past year. Evaluate the effectiveness of the committee framework.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Compensation Analysis"):
            response = call_transform(
                "Analyze executive compensation structures, including base salary, performance bonuses, equity awards, and other benefits. Compare compensation levels against industry benchmarks and evaluate alignment with company performance.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("DE&I Metrics"):
            response = call_transform(
                "Evaluate the company's diversity, equity, and inclusion metrics across all organizational levels, including board, executive team, and workforce composition. Track progress against stated DE&I goals and industry benchmarks.",
                fromYear,
                ticker
            )
            st.write(response)

        # Risk Assessment Section
        st.write("### Risk Assessment")
        
        with st.expander("Risk Factor Identification"):
            response = call_transform(
                "Identify and categorize all material risks disclosed by the company, including operational, financial, regulatory, and strategic risks. Provide specific examples and context for each major risk category.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Risk Pattern Evolution"):
            response = call_transform(
                f"Analyze how the company's risk profile has evolved over the past {years} years, noting new emerging risks, risks that have been mitigated, and changes in risk prioritization. Include specific examples of risk materialization where applicable.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Mitigation Strategies"):
            response = call_transform(
                "Evaluate the company's risk mitigation strategies and their effectiveness, including specific policies, procedures, and controls implemented to address key risks. Assess the comprehensiveness of the risk management framework.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Impact Analysis"):
            response = call_transform(
                "Analyze the potential financial and operational impacts of identified risks, including quantitative assessments where available and qualitative evaluations of potential consequences. Include historical examples of risk impacts when relevant.",
                fromYear,
                ticker
            )
            st.write(response)
            
        with st.expander("Peer Risk Comparison"):
            response = call_transform(
                "Compare the company's risk profile and mitigation strategies against industry peers, highlighting areas where the company's approach differs significantly from industry standards. Include analysis of unique risks specific to the company.",
                fromYear,
                ticker
            )
            st.write(response)



if __name__ == '__main__':
    api = API()
    transformer = Transformer()
    dba = DBagent()
    main()