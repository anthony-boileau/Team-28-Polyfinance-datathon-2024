
import streamlit as st
from datetime import datetime
import asyncio
from transformer import Transformer
from api import API
from dbagent import DBagent

st.set_page_config(page_title="AI Chat Assistant", page_icon="💬")

st.markdown("# AI Chat Assistant 💬")
st.sidebar.header("AI Chat")

# Check if ticker and years are in session state
if "ticker" not in st.session_state or "years" not in st.session_state:
    st.error("Please select a ticker and time period on the home page first!")
    st.stop()

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

def display_chat_history():
    if "messages" in st.session_state:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def main():
    # Initialize chat history
    initialize_chat_history()
    
    # Display current analysis parameters
    st.write(f"Chatting about **{st.session_state.ticker}** for the past **{st.session_state.years}** year(s)")
    
    # Calculate the from year
    fromYear = datetime.now().year - st.session_state.years + 1
    
    # Create a placeholder for the status message
    status_placeholder = st.empty()
    status_placeholder.info('Loading data, please wait...')
    
    # Fetch company data
    ready = True
    
    if ready:
        status_placeholder.success('Data loaded! You can now ask questions below.')
        
        st.write("## Ask Questions About your Data")
        st.write("Use the chat below to ask specific questions about the company's performance, leadership, strategy, or any other aspect.")
        
        display_chat_history()
        
        if prompt := st.chat_input("What would you like to know about the company?"):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("assistant"):
                response = call_transform(prompt, fromYear, st.session_state.ticker)
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:
        st.error("Failed to load company data. Please try again.")

if __name__ == "__main__":
    # Initialize required classes
    api = API()
    transformer = Transformer()
    dba = DBagent()
    main()