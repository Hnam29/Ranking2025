import streamlit as st 
from streamlit_option_menu import option_menu 
from webpages.ranking import main_ranking
from webpages.web import main_web
from webpages.app import main_app
from webpages.feedback import main_feedback

st.set_page_config(page_title="Multiple Dashboards", page_icon="📈",layout="wide",initial_sidebar_state='collapsed')

st.logo("/webpages/Logo.png")

page = option_menu(None, ["Ranking", "Web",  "App", 'Feedback'], 
    icons=['list-ol', 'browser-chrome', "google-play", 'chat-left-text'], 
    menu_icon="cast", default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffffff"},
        "icon": {"color": "#fcc603", "font-size": "25px"}, 
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#69bd68"},
    }
)

st.markdown("---")

if page == 'Ranking':
    main_ranking()

elif page == 'Web':
    main_web()

elif page == 'App':
    main_app()

elif page == 'Feedback':
    main_feedback()
