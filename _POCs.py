"""POCs Ensino Einstein"""

# Import from 3rd party libraries
import streamlit as st
import streamlit.components.v1 as components
import streamlit_analytics


# Configure Streamlit page and state
st.set_page_config(page_title="POCs Ensino")

if "plano" not in st.session_state:
    st.session_state.plano = ""
if "text_error" not in st.session_state:
    st.session_state.text_error = ""
if "n_requests" not in st.session_state:
    st.session_state.n_requests = 0

# Force responsive layout for columns also on mobile
st.write(
    """<style>
    [data-testid="column"] {
        width: calc(50% - 1rem);
        flex: 1 1 calc(50% - 1rem);
        min-width: calc(50% - 1rem);
    }
    </style>""",
    unsafe_allow_html=True,
)

# Render Streamlit page
streamlit_analytics.start_tracking()
st.title("POCs Ensino")
st.markdown(
    "POCs Ensino"
)

streamlit_analytics.stop_tracking()
