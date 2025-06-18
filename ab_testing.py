import streamlit as st
from time import time
import random
import requests

# Initialize session state for group assignment and start time
if 'group' not in st.session_state:
    st.session_state['group'] = random.choice(['A', 'B'])
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time()

# Define the functions for A/B group content
def do_group_a_stuff():
    st.write("Hello there, fellow web traveler!")

def do_group_b_stuff():
    st.write("What's up, friend? You dig the site?")

# Function to log data
def log_data(group, action, start_time):
    end_time = time()
    time_spent = end_time - start_time
    data = {'group': group, 'action': action, 'time_spent': time_spent}
    # Replace 'YOUR_API_ENDPOINT' with the actual endpoint
    response = requests.post('YOUR_API_ENDPOINT', json=data)
    if response.status_code != 200:
        st.error('Failed to log data')

# Function to redirect user to a new URL
def nav_to(url):
    nav_script = f'<meta http-equiv="refresh" content="0; URL=\'{url}\'" />'
    st.markdown(nav_script, unsafe_allow_html=True)

# Display content based on the user's assigned group
if st.session_state['group'] == 'A':
    do_group_a_stuff()
elif st.session_state['group'] == 'B':
    do_group_b_stuff()

# Button to log time spent on the page and perform an action
if st.button('Click me!'):
    log_data(st.session_state['group'], 'button_click', st.session_state['start_time'])

# Button to exit the page and log the interaction
if st.button('Exit Page to Google'):
    log_data(st.session_state['group'], 'exit_page', st.session_state['start_time'])
    nav_to("https://www.google.com")

# Run the app
if __name__ == '__main__':
    st.title('A/B Testing with Streamlit')