import streamlit as st
from code_editor import code_editor
import requests
import json

# Initialize session state
if 'auth' not in st.session_state:
    st.session_state.auth = ('_SYSTEM', 'SYS')
if 'host' not in st.session_state:
    st.session_state.host = 'localhost'
if 'port' not in st.session_state:
    st.session_state.port = '56754'
if 'namespaces' not in st.session_state:
    st.session_state.namespaces = ['%SYS','IRISAPP']
if 'selected_namespace' not in st.session_state:
    st.session_state.selected_namespace = ''
if 'query' not in st.session_state:
    st.session_state.query = ''
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to fetch namespaces
def fetch_namespaces():
    url = f"https://{st.session_state.host}:{st.session_state.port}/api/atelier/"
    try:
        response = requests.get(url, auth=st.session_state.auth)
        response.raise_for_status()
        data = response.json()
        st.session_state.namespaces = data.get('namespaces', [])
    except requests.RequestException as e:
        st.error(f"Error fetching namespaces: {str(e)}")

# Function to run query
def run_query():
    url = f"https://{st.session_state.host}:{st.session_state.port}/api/atelier/v1/{st.session_state.selected_namespace}/action/query"
    payload = {"query": st.session_state.query}
    try:
        response = requests.post(url, json=payload, auth=st.session_state.auth)
        response.raise_for_status()
        st.success("Query executed successfully!")
        st.json(response.json())
    except requests.RequestException as e:
        st.error(f"Error running query: {str(e)}")

# Function to save query
def save_query():
    url = f"https://{st.session_state.host}:{st.session_state.port}/sqlzilla/query"
    payload = {"query": st.session_state.query}
    try:
        response = requests.post(url, json=payload, auth=st.session_state.auth)
        response.raise_for_status()
        st.success("Query saved successfully!")
    except requests.RequestException as e:
        st.error(f"Error saving query: {str(e)}")

# Function to simulate assistant interaction
def assistant_interaction(prompt):
    # This is a placeholder. In a real scenario, you'd call an AI service here.
    response = f"Assistant: I've analyzed your prompt '{prompt}'. Here's a suggested SQL query:\n\nSELECT * FROM Table WHERE condition = 'value';"
    st.session_state.chat_history.append(("User", prompt))
    st.session_state.chat_history.append(("Assistant", response))
    return response

# Streamlit UI
st.title("SQLZilla")

# Fetch namespaces initially
#fetch_namespaces()

# Initial prompts for namespace and database schema
namespace = st.selectbox('Select Namespace', st.session_state.namespaces)
database_schema = st.text_input('Enter Database Schema')

# Authentication configuration
if st.button("Change Authentication"):
    username = st.text_input("Username", value=st.session_state.auth[0])
    password = st.text_input("Password", value=st.session_state.auth[1], type="password")
    host = st.text_input("Host", value=st.session_state.host)
    port = st.text_input("Port", value=st.session_state.port)
    if st.button("Save Configuration"):
        st.session_state.auth = (username, password)
        st.session_state.host = host
        st.session_state.port = port
        st.success("Configuration updated!")


# if namespace and database_schema:
    # Layout for the page
col1, col2 = st.columns(2)

with col1:
    code_editor("-- your query", lang="sql", height=[10, 100], shortcuts="vscode")
    
    # Buttons to run, save, and clear the query in a single row
    run_button, save_button, clear_button = st.columns([1, 1, 1])
    with run_button:
        if st.button('Execute'):
            run_query()
    with save_button:
        if st.button('Save'):
            save_query()
    with clear_button:
        if st.button('Clear'):
            st.session_state.query = ""
    # Display query result as dataframe
    if st.session_state.query_result:
        try:
            df = pd.json_normalize(st.session_state.query_result['result'])
            st.dataframe(df)
        except KeyError:
            st.error("Unexpected result format")

with col2:
    prompt = st.chat_input("Say something")
    if prompt:
        response = assistant_interaction(prompt)
        st.write(response)

    # Display chat history
    for sender, message in st.session_state.chat_history:
        if sender == "User":
            st.text_area("User", value=message, height=75, key=f"user_{message}")
        else:
            st.text_area("Assistant", value=message, height=75, key=f"assistant_{message}")
