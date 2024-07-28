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
    st.session_state.namespaces = []
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


code_editor("-- your query", lang="sql", height=[10, 100], shortcuts="vscode")

st.text_area("Prompt", value="", height=200)