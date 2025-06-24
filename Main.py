import streamlit as st
from streamlit_option_menu import option_menu

# IMMEDIATE DEBUG - Check if imports work
st.error("🚨 DEBUG: Main.py started, imports beginning...")

try:
    from webpages.ranking import main_ranking
    st.error("🚨 DEBUG: ranking import successful")
except Exception as e:
    st.error(f"🚨 DEBUG: ranking import FAILED: {str(e)}")
    main_ranking = None

try:
    from webpages.web import main_web
    st.error("🚨 DEBUG: web import successful")
except Exception as e:
    st.error(f"🚨 DEBUG: web import FAILED: {str(e)}")
    main_web = None

try:
    from webpages.app import main_app
    st.error("🚨 DEBUG: app import successful")
except Exception as e:
    st.error(f"🚨 DEBUG: app import FAILED: {str(e)}")
    main_app = None

try:
    from webpages.feedback import main_feedback
    st.error("🚨 DEBUG: feedback import successful")
except Exception as e:
    st.error(f"🚨 DEBUG: feedback import FAILED: {str(e)}")
    main_feedback = None

st.error("🚨 DEBUG: All imports completed")

st.set_page_config(page_title="Multiple Dashboards", page_icon="📈",layout="wide",initial_sidebar_state='collapsed')

# st.sidebar.markdown("""<h2 style="color:#dbb323; text-align: center">Welcome to Ranking 2025</h2>""", unsafe_allow_html=True)
st.logo("/Users/vuhainam/Documents/PROJECT_DA/EdtechAgency/Ranking/2025/webpages/Logo.png")

# page = option_menu(
#         menu_title=None, #required (default:None)
#         options=['Home','Documentation','Examples'], #required
#         icons=['house','book','envelope'], #optional -> find on Bootstrap
#         menu_icon='cast', #optional
#         default_index=0, #optional
#         orientation='horizontal',
#         styles={
#             'container':{'padding':'5px!important','background-color':'pink'},
#             'icon':{'color':'orange','font-size':'25px'},
#             'nav-link': {
#                 'font-size':'25px',
#                 'text-align':'center',
#                 'margin': '40px 40px 0px',
#                 '--hover-color': '#eee',
#             },
#             'nav-link-selected': {'background-color':'green'},
#         },
#     )

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

st.error(f"🚨 DEBUG: Page selected: {page}")

if page == 'Ranking':
    st.error("🚨 DEBUG: About to call main_ranking()")
    if main_ranking is not None:
        try:
            main_ranking()
            st.error("🚨 DEBUG: main_ranking() completed successfully")
        except Exception as e:
            st.error(f"🚨 DEBUG: main_ranking() FAILED: {str(e)}")
    else:
        st.error("🚨 DEBUG: main_ranking is None, cannot call")

elif page == 'Web':
    st.error("🚨 DEBUG: About to call main_web()")
    if main_web is not None:
        main_web()
    else:
        st.error("🚨 DEBUG: main_web is None, cannot call")

elif page == 'App':
    st.error("🚨 DEBUG: About to call main_app()")
    if main_app is not None:
        main_app()
    else:
        st.error("🚨 DEBUG: main_app is None, cannot call")

elif page == 'Feedback':
    st.error("🚨 DEBUG: About to call main_feedback()")
    if main_feedback is not None:
        main_feedback()
    else:
        st.error("🚨 DEBUG: main_feedback is None, cannot call")