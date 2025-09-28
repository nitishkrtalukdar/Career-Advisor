
# In pages/1_Career_Finder.py

import streamlit as st
import pandas as pd
from career_agent import get_career_suggestions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Career Path Finder | CareeroAI",
    page_icon="🧭",
    layout="wide",
)

st.title("🧭 Career Path Finder for High Schoolers")
st.write("For high school students trying to find their way. Fill out the survey below to get started!")

# --- Survey Form ---
with st.form("career_survey"):
    st.subheader("Academic Information")
    subjects = st.multiselect(
        "What are your strongest subjects?",
        ["Physics", "Mathematics", "Chemistry", "Biology", "Computer Science", "History", "Economics", "Literature", "Art"]
    )
    score = st.slider("What were your approximate Class 12th scores (in %)?", 0, 100, 75)

    st.subheader("Personal Interests")
    interests = st.multiselect(
        "What are your hobbies and interests?",
        ["Reading", "Gaming", "Sports", "Coding/Programming", "Art/Drawing", "Music", "Debating", "Volunteering", "Traveling"]
    )
    work_style = st.radio(
        "How do you prefer to work?",
        ("I prefer working alone", "I enjoy collaborating in teams", "A mix of both"),
        horizontal=True
    )

    st.subheader("College Preferences")
    budget = st.selectbox(
        "What is your approximate annual budget for college fees?",
        ("Less than ₹2 Lakhs", "₹2 Lakhs - ₹5 Lakhs", "₹5 Lakhs - ₹10 Lakhs", "More than ₹10 Lakhs")
    )
    relocate = st.radio("Are you willing to relocate to a different city for college?", ("Yes", "No"), horizontal=True)
    
    states_and_uts = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", 
        "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
        "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", 
        "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", 
        "Lakshadweep", "Puducherry"
    ]
    home_state = st.selectbox("What is your home state?", states_and_uts)
    
    cities = st.multiselect(
        "Do you have any preferred cities? (Optional)",
        ["Delhi", "Mumbai", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Ahmedabad"]
    )

    # Submit button for the form
    submitted = st.form_submit_button("Find My Career Path")

# --- Process and Display Results ---
if submitted:
    # Clear previous results when a new survey is submitted
    if 'career_results' in st.session_state:
        del st.session_state['career_results']
    if 'selected_career' in st.session_state:
        del st.session_state['selected_career']

    if not subjects or not interests:
        st.warning("Please select at least one subject and one interest.")
    else:
        # Collate survey data
        survey_data = {
            "subjects": ", ".join(subjects),
            "score": score,
            "interests": ", ".join(interests),
            "work_style": work_style,
            "budget": budget,
            "relocate": relocate,
            "home_state": home_state,
            "cities": ", ".join(cities) if cities else "Any"
        }
        
        # Show the spinner and call the AI agent
        with st.spinner("Analyzing your profile and finding the best career paths for you..."):
            try:
                result = get_career_suggestions(survey_data)
                st.session_state.career_results = result['careers']
            except Exception as e:
                st.error("Sorry, something went wrong. Please try again!")
                st.error(f"Error details: {e}")

# Display results if they exist in the session state
if "career_results" in st.session_state:
    st.success("Here are your top 3 career path suggestions!")
    
    career_titles = [career['career_name'] for career in st.session_state.career_results]
    
    if 'selected_career' not in st.session_state:
        st.session_state.selected_career = None

    cols = st.columns(len(career_titles))
    for i, title in enumerate(career_titles):
        if cols[i].button(title, use_container_width=True, key=f"career_btn_{i}"):
            st.session_state.selected_career = st.session_state.career_results[i]

    # Display details of the selected career
    if st.session_state.selected_career:
        st.divider()
        career = st.session_state.selected_career
        st.header(f"Insights for: {career['career_name']}")

        st.subheader("💡 Reasoning")
        st.write(career['reasoning'])

        st.subheader("💰 Average Starting Salary")
        st.write(career['average_salary'])

        # Display Government Colleges Table
        st.subheader("🎓 Top Government Colleges")
        govt_colleges = career['top_colleges'].get('government', [])
        if govt_colleges:
            df_govt = pd.DataFrame(govt_colleges)
            st.dataframe(df_govt, use_container_width=True, hide_index=True)
        else:
            st.write("No specific government colleges found matching the criteria.")
        
        # Display Private Colleges Table
        st.subheader("🎓 Top Private Colleges")
        private_colleges = career['top_colleges'].get('private', [])
        if private_colleges:
            df_private = pd.DataFrame(private_colleges)
            st.dataframe(df_private, use_container_width=True, hide_index=True)
        else:
            st.write("No specific private colleges found matching the criteria.")
