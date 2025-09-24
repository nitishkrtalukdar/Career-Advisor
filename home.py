# In Home.py

import streamlit as st

st.set_page_config(
    page_title="CareeroAI - Home",
    page_icon="🧠",
    layout="wide",
)

st.title("Welcome to CareeroAI 🧠")
st.write("Your personal AI-powered career assistant. Choose your path below to get started.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.header("Interview Prep")
    st.write("For college students and professionals. Upload your resume and a job description to get a detailed evaluation and practice for your interview.")
    # The correct path includes the 'pages/' prefix
    if st.button("Go to Interview Prep", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Interview_Prep.py")

with col2:
    st.header("Career Path Finder")
    st.write("For high school students who are unsure about their future. Take a survey to discover the top 3 career paths tailored to your skills and interests.")
    # The correct path includes the 'pages/' prefix
    if st.button("Go to Career Finder", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Career_Finder.py")