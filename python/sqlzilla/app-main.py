import streamlit as st
from code_editor import code_editor
import requests
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlzilla import SQLZilla

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
if 'code_text' not in st.session_state:
    st.session_state.code_text = ''

def db_connection_str():
    user = st.session_state.user
    pwd = st.session_state.pwd
    host = st.session_state.hostname
    prt = st.session_state.port
    ns = st.session_state.namespace
    return f"iris://{user}:{pwd}@{host}:{prt}/{ns}"

def assistant_interaction(sqlzilla, prompt):
    response = sqlzilla.prompt(prompt)
    response = clean_response(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    return response

def clean_response(response):
    if response.startswith("```sql"):
        response = response[6:-3]
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

database_schema = None
if (st.session_state.namespace and st.session_state.openai_api_key):
    sqlzilla = SQLZilla(db_connection_str(), st.session_state.openai_api_key)
    # Initial prompts for namespace and database schema
    try:
        query = """
        SELECT SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
        """
        rows = sqlzilla.execute_query(query)
        options = [row[0] for row in rows or []]
        database_schema = st.selectbox(
            'Enter Database Schema', 
            options,
            index=None,
            placeholder="Select database schema...",
        )
    except:
        database_schema = st.text_input('Enter Database Schema')
        st.warning('Was not possible to retrieve database schemas. Please provide it manually.')

if (st.session_state.namespace and database_schema and st.session_state.openai_api_key):
    context = sqlzilla.schema_context_management(database_schema)

    # Layout for the page
    col1, col2 = st.columns(2)

    with col1:
        editor_btn = [ {
            "name": "Execute", "feather": "Play",
            "primary": True,"hasText": True, "alwaysOn": True,
            "showWithIcon": True,"commands": ["submit"],
            "style": {
                "bottom": "0.44rem",
                "right": "0.4rem"
            }
        },]
        editor_dict = code_editor(st.session_state.code_text, lang="sql", height=[10, 100], shortcuts="vscode", options={"placeholder":"Add your SQL here to test...", "showLineNumbers":True}, buttons=editor_btn)

        if editor_dict['type'] == "submit":
            st.session_state.code_text = editor_dict['text']
            data = sqlzilla.execute_query(st.session_state.code_text)
            # Display query result as dataframe
            if (data is not None):
                st.session_state.query_result = pd.DataFrame(data)
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

            response = assistant_interaction(sqlzilla, prompt)

            # Check if the response contains SQL code and update the editor
            if "SELECT" in response.upper():
                st.session_state.query = response
                st.session_state.code_text = response
                editor_dict['text'] = response
                data = sqlzilla.execute_query(st.session_state.code_text)
                st.session_state.query_result = pd.DataFrame(data)
                st.rerun()
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
else:
    st.warning('Please select a database schema to proceed.')
