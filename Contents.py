import streamlit as st

st.set_page_config(
    page_title="AI Teacher Support",
    page_icon="👋",
)

st.write("# Welcome to IMS Teacher Support AI Page! 👋")

st.sidebar.success("Select an activity above.")

st.markdown(
    """
    These activities are intended for educational use.
    They use GPT 3.5 Turbo as the AI.
    If you encounter any bugs, errors, or invalid responses, please report them to edtech@indianmountain.org.

    **Lesson Planner** allows you to specify a format, subject, a topic, and present additional constraints to the AI.
    It will return a project, lesson, worksheet, athletics practice, etc.  You can ask the AI to refine its response to 
    best fit your needs.

"""
)