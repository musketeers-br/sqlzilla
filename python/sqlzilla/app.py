import streamlit as st
from code_editor import code_editor
import requests
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize session state
if 'hostname' not in st.session_state:
    st.session_state.hostname = 'sqlzilla-iris-1'
if 'user' not in st.session_state:
    st.session_state.user = '_system'
if 'pwd' not in st.session_state:
    st.session_state.pwd = 'SYS'
if 'port' not in st.session_state:
    st.session_state.port = '1972'
if 'namespace' not in st.session_state:
    st.session_state.namespace = "IRISAPP"
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY', '')
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "I'm SQLZilla, your friendly AI SQL helper.\n Ask me anything, from basic queries to complex optimizations."}]
if 'query_result' not in st.session_state:
    st.session_state.query_result = None

def db_connection():
    user = st.session_state.user
    pwd = st.session_state.pwd
    host = st.session_state.hostname
    prt = st.session_state.port
    ns = st.session_state.namespace
    iris_conn_str = f"iris://{user}:{pwd}@{host}:{prt}/{ns}"
    engine = create_engine(iris_conn_str)
    return engine.connect().connection

# Function to run query using SQLAlchemy and return result as DataFrame
def run_query():
    try:
        engine = db_connection()
        with engine.connect() as connection:
            result = pd.read_sql_query(st.session_state.query, connection)
            st.session_state.query_result = result
            st.success("Query executed successfully!")
    except Exception as e:
        st.error(f"Error running query: {str(e)}")


# Function to simulate assistant interaction
def assistant_interaction(prompt):
    # This is a placeholder. In a real scenario, you'd call an AI service here.
    response = f"Assistant: I've analyzed your prompt '{prompt}'. Here's a suggested SQL query:\n\nSELECT * FROM Table WHERE condition = 'value';"
    st.session_state.chat_history.append(("User", prompt))
    st.session_state.chat_history.append(("Assistant", response))
    return response

left_co, cent_co, last_co = st.columns(3)
with cent_co:
    try:
        st.image("small_logo.png", use_column_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar a imagem: {str(e)}")
        st.write("SQLZilla")

# Authentication configuration
if not st.session_state.openai_api_key:
    st.warning("Please provide your API key to proceed.")
    st.session_state.openai_api_key = st.text_input("API Key", type="password")
else:
    if st.button("Config"):
        host = st.text_input("Hostname", value=st.session_state.hostname)
        username = st.text_input("Username", value=st.session_state.user)
        password = st.text_input("Password", value=st.session_state.pwd, type="password")
        namespace = st.text_input("Namespace", value=st.session_state.namespace)
        port = st.text_input("Port", value=st.session_state.port)
        api_key = st.text_input("API Key", value=st.session_state.openai_api_key, type="password")
        if st.button("Save"):
            st.session_state.hostname = host
            st.session_state.port = port
            st.session_state.pwd = password
            st.session_state.user = username
            st.session_state.namespace = namespace
            st.session_state.openai_api_key = api_key
            st.success("Configuration updated!")

# Initial prompts for namespace and database schema
database_schema = st.text_input('Enter Database Schema')

if st.session_state.namespace and database_schema:
    # Layout for the page
    col1, col2 = st.columns(2)

    with col1:
        code_editor("-- your query", lang="sql", height=[10, 100], shortcuts="vscode")
        
        # Buttons to run, save, and clear the query in a single row
        run_button, clear_button = st.columns([1, 1])
        with run_button:
            if st.button('Execute'):
                run_query()
        with clear_button:
            if st.button('Clear'):
                st.session_state.query = ""
        
        # Display query result as dataframe
        if st.session_state.query_result is not None:
            st.dataframe(st.session_state.query_result)
        

    with col2:
        # Display chat history
        for message in st.session_state.chat_history:
            st.chat_message(message["role"]).markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("How can I assist you?"):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})

            response = assistant_interaction(prompt)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
else:
    st.warning('Please select a namespace and enter a database schema to proceed.')