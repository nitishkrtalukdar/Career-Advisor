from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from typing import ContextManager
from langchain_community.document_loaders import PyPDFLoader
from evaluator_agent import evaluate_resume
from chat_agent import call_chat_agent
import plotly.graph_objects as go
import re
import pandas as pd

st.set_page_config(
    page_title="Interview Prep | CareeroAI",
    page_icon="🧐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- HELPER FUNCTIONS ---

def stream_gemini_response(stream):
    for chunk in stream:
        try:
            yield chunk.text
        except Exception:
            continue

def create_donut_chart(score: float):
    score = max(0, min(10, score))
    fig = go.Figure(data=[go.Pie(
        values=[score, 10 - score],
        hole=0.6,
        textinfo='none',
        marker=dict(colors=["#009688", "#ECEFF1"])
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=50,
        width=50,
    )
    return fig

def clean_and_convert_score(score_string: str) -> float:
    match = re.search(r'(\d+\.?\d*)', str(score_string))
    if match:
        try:
            return float(match.group(1))
        except (ValueError, IndexError):
            return 0.0
    return 0.0

# --- THIS IS THE CORRECTED, MORE ROBUST FUNCTION ---
def display_evaluation(container: ContextManager) -> None:
    with container:
        evaluation = st.session_state.evaluation

        # Display Scores
        st.header("📊 Evaluation Breakdown")
        
        score_metrics = {
            "global_score": "Global Score",
            "education_relevance": "Education Relevance",
            "matching_skills": "Matching Skills",
            "project_relevance": "Project Relevance",
            "industry_standard": "Standard vs. Industry"
        }

        # Display the Global Score
        if "global_score" in evaluation:
            raw_global_score = evaluation.get("global_score", "0")
            numeric_global_score = clean_and_convert_score(raw_global_score)
            
            c1, c2, c3 = st.columns([5, 3, 2])
            with c1: st.markdown(f"## {score_metrics['global_score']}")
            with c2: st.markdown(f"<b style='text-align: right; font-size: 38px;'>{numeric_global_score:.1f}/10</b>", unsafe_allow_html=True)
            with c3: st.plotly_chart(create_donut_chart(numeric_global_score), use_container_width=True)
            st.divider()

        # Display the rest of the scores
        for key, display_name in score_metrics.items():
            if key != "global_score" and key in evaluation:
                # --- THIS IS THE FIX ---
                # Check if the 'details' for this key is a dictionary before processing
                details = evaluation.get(key)
                if isinstance(details, dict):
                    raw_score = details.get('score', "0")
                    numeric_score = clean_and_convert_score(raw_score)
                    
                    c1, c2, c3 = st.columns([5, 3, 2])
                    with c1: st.markdown(f"### {display_name}")
                    with c2: st.markdown(f"<b style='text-align: right; font-size: 30px;'>{numeric_score:.1f}/10</b>", unsafe_allow_html=True)
                    with c3: st.plotly_chart(create_donut_chart(numeric_score), use_container_width=True)

                    with st.expander("Positive Points"):
                        for point in details.get("positive", []):
                            st.write(f"- {point}")
                    
                    with st.expander("Negative Points"):
                        negative_points = details.get("negative", [])
                        if negative_points:
                            for point in negative_points:
                                st.write(f"- {point}")
                        else:
                            st.write("No negative points.")
                else:
                    # If 'details' is just a string, display it as a general note
                    st.markdown(f"### {display_name}")
                    st.info(str(details)) # Using st.info to make it stand out
        st.divider()

        # Display Areas to Improve Table
        st.header("🔑 Key Areas to Improve")
        improvements = evaluation.get("areas_to_improve", [])
        if improvements and isinstance(improvements, list):
            df_improvements = pd.DataFrame(improvements)
            if not df_improvements.empty:
                df_improvements.rename(columns={
                    'Area': 'Area to Focus On',
                    'Importance': 'Importance',
                    'Your Current Level': 'Your Current Level',
                    'Approx. Time to Prepare': 'Time to Prepare'
                }, inplace=True, errors='ignore')
            st.dataframe(df_improvements, use_container_width=True, hide_index=True)
        else:
            st.success("Great job! The AI found no specific areas for immediate improvement.")

# --- The rest of your code remains the same ---

def update_history():
    if st.session_state.job_text != '':
        job_text = st.session_state.job_text
        existing_record = next((record for record in st.session_state.jobs_history if record['job_text'] == job_text), None)
        if existing_record:
            if "messages" in st.session_state: existing_record["messages"] = st.session_state.messages; del st.session_state.messages
            if "evaluation" in st.session_state: existing_record["evaluation"] = st.session_state.evaluation; del st.session_state.evaluation
        else:
            new_record = {'job_text': job_text}
            if "messages" in st.session_state: new_record["messages"] = st.session_state.messages; del st.session_state.messages
            if "evaluation" in st.session_state: new_record["evaluation"] = st.session_state.evaluation; del st.session_state.evaluation
            if len(new_record) > 1: st.session_state.jobs_history.append(new_record)

def run_chat_agent(resume: str, job_description: str):
    system_prompt = f"""
    You are a career advisor for a candidate with the resume delimited by <<<>>> and the job description delimited by ((( ))).
    Resume: <<< {resume} >>>
    Job description: ((( {job_description} )))
    Answer the questions giving the given information only. If you don't know the answer, say that you don't know.
    """
    if "messages" not in st.session_state: st.session_state.messages = []
    message_container = st.container(height=600)
    for message in st.session_state.messages:
        if message.get("role") != "system":
            role = "assistant" if message.get("role") == "model" else message.get("role")
            message_container.chat_message(role).write(message.get("content"))
    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        message_container.chat_message("user").write(prompt)
        messages_to_send = [msg for msg in st.session_state.messages if msg.get("role") != "system"]
        stream = call_chat_agent(messages_to_send, system_prompt)
        response = message_container.chat_message("assistant").write_stream(stream_gemini_response(stream))
        st.session_state.messages.append({"role": "model", "content": response})

def retrieve_job_history(job_history: str) -> None:
    update_history()
    st.session_state.job_text = job_history.get('job_text')
    if 'evaluation' in job_history: st.session_state.evaluation = job_history.get('evaluation')
    if "messages" in job_history:
        loaded_messages = job_history.get('messages')
        st.session_state.messages = [msg for msg in loaded_messages if msg.get("role") != "system"]

if "job_text" not in st.session_state: st.session_state.job_text = ""
if "jobs_history" not in st.session_state: st.session_state.jobs_history = []

with st.sidebar:
    st.header("History")
    for i, job_history in enumerate(st.session_state.jobs_history):
        try:
            job = job_history['evaluation']['title']
        except KeyError:
            job = "New record"
        if st.button(job, type='tertiary', use_container_width=True, key=f'{job}_{i}'):
            retrieve_job_history(job_history)

left_section, right_section = st.columns(2)
with left_section:
    st.title("🧐 Interview Prep for College Students")
    resume = st.file_uploader("Upload your resume", type=["pdf"])
    if resume is not None:
        with open("temp_resume.pdf", "wb") as f: f.write(resume.read())
        loader = PyPDFLoader("temp_resume.pdf")
        pages = loader.load()
        st.session_state.resume_content = "\n".join(page.page_content for page in pages)
        with st.expander("Show Resume Content"):
            st.write(st.session_state.resume_content)
    job_text = st.text_area("Job Description:", st.session_state.job_text, height=350, on_change=update_history)
    st.session_state.job_text = job_text

with right_section:
    tab1, tab2 = st.tabs(["⭐ Evaluation", "💬 Free Chat"])
    with tab1:
        if st.button("Evaluate", type='primary', use_container_width=True, icon='🧐'):
            if "resume_content" not in st.session_state:
                st.warning('Please upload a resume first', icon="⚠️")
            elif st.session_state.job_text == "":
                st.warning('Please provide a job description', icon="⚠️")
            else:
                with st.spinner("Evaluating your resume..."):
                    try:
                        st.session_state.evaluation = evaluate_resume(st.session_state.resume_content, st.session_state.job_text)
                    except Exception as e:
                        st.error("Sorry, there was an error during evaluation.")
                        st.error(f"Details: {e}")
        evaluation_container = st.container(height=600)
        if "evaluation" in st.session_state:
            display_evaluation(evaluation_container)
    with tab2:
        if ("resume_content" in st.session_state) and (st.session_state.job_text != ""):
            run_chat_agent(st.session_state.resume_content, st.session_state.job_text)

