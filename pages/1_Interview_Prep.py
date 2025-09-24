from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from typing import ContextManager
from langchain_community.document_loaders import PyPDFLoader
from evaluator_agent import evaluate_resume
from chat_agent import call_chat_agent
import plotly.graph_objects as go

st.set_page_config(
    page_title="Interview Prep | CareeroAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ADD THIS NEW HELPER FUNCTION
def stream_gemini_response(stream):
    for chunk in stream:
        try:
            yield chunk.text
        except Exception:
            # Handle potential errors if a chunk has no text
            continue

def update_history():
    if st.session_state.job_text != '':
        job_text = st.session_state.job_text
        existing_record = next((record for record in st.session_state.jobs_history if record['job_text'] == job_text), None)
        
        if existing_record:
            # Update existing record
            if "messages" in st.session_state:
                existing_record["messages"] = st.session_state.messages
                del st.session_state.messages
            if "evaluation" in st.session_state:
                existing_record["evaluation"] = st.session_state.evaluation
                del st.session_state.evaluation
        else:
            # Create new record
            new_record = {
                'job_text': job_text
            }
            if "messages" in st.session_state:
                new_record["messages"] = st.session_state.messages
                del st.session_state.messages
            if "evaluation" in st.session_state:
                new_record["evaluation"] = st.session_state.evaluation
                del st.session_state.evaluation
            if len(new_record) > 1:
                st.session_state.jobs_history.append(new_record)

def create_donut_chart(score: int | float):
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

def display_evaluation(container: ContextManager) -> None:
    with container:
        col1, col2, col3 = st.columns([5, 3, 2])
        with col1:
            st.markdown(f"## Global Score")
        with col2:
            st.markdown(f"<b style='text-align: right; font-size: 38px;'>{float(st.session_state.evaluation["global_score"])}/10</b>", unsafe_allow_html=True)
        with col3:
            chart = create_donut_chart(float(st.session_state.evaluation["global_score"]))
            st.plotly_chart(chart, use_container_width=True, key="Global Score")
        st.divider()
        for name, details in st.session_state.evaluation.items():
            if name not in ['global_score', 'title']:
                col1, col2, col3 = st.columns([5, 3, 2])
                with col1:
                    st.markdown(f"### {name.capitalize()}")
                with col2:
                    st.markdown(f"<b style='text-align: right; font-size: 30px;'>{details['score']}/10</b>", unsafe_allow_html=True)
                with col3:
                    chart = create_donut_chart(details["score"])
                    st.plotly_chart(chart, use_container_width=True, key=name)
                
                with st.expander("Positive Points"):
                    for point in details["positive"]:
                        st.write(f"- {point}")
                
                with st.expander("Negative Points"):
                    if details["negative"]:
                        for point in details["negative"]:
                            st.write(f"- {point}")
                    else:
                        st.write("No negative points.")


# Replace the old run_chat_agent function with this one
# In main.py, replace your existing function with this one

# In main.py, replace the entire function with this version

# In main.py, ensure your run_chat_agent function looks like this

def run_chat_agent(resume: str, job_description: str):
    system_prompt = f"""
    You are a career advisor for a candidate with the resume delimited by <<<>>> and the job description delimited by ((( ))).
    Resume:
    <<<
    {resume}
    >>>
    Job description:
    (((
    {job_description}
    )))
    Answer the questions giving the given information only. If the candidate asks a question that you don't have an answer to, say that you don't know the answer.
    """
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

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
        
        # This line is correct and essential
        st.session_state.messages.append({"role": "model", "content": response})

def retrieve_job_history(job_history: str) -> None:
    update_history()
    st.session_state.job_text = job_history.get('job_text')
    if 'evaluation' in job_history:
        st.session_state.evaluation = job_history.get('evaluation')
    if "messages" in job_history:
        loaded_messages = job_history.get('messages')
        st.session_state.messages =  [msg for msg in loaded_messages if msg.get("role") != "system"]

if "job_text" not in st.session_state:
    st.session_state.job_text = ""

if "jobs_history" not in st.session_state:
    st.session_state.jobs_history = []

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
        # Save the uploaded resume temporarily
        with open("temp_resume.pdf", "wb") as f:
            f.write(resume.read())
        
        # Use PyPDFLoader to read the uploaded resume
        loader = PyPDFLoader("temp_resume.pdf")
        pages = loader.load()

        st.session_state.resume_content = "\n".join(page.page_content for page in pages)
        # Display the resume content (optional)
        with st.expander("Show Resume Content"):
            st.write(st.session_state.resume_content)

    # Editable text box with job details
    job_text = st.text_area(
        "Job Description:",
        st.session_state.job_text,
        height=350,
        on_change=update_history,
    )

    # Update the session state with edited text
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
                progress_bar = st.progress(45, "Evaluating...")
                st.session_state.evaluation = evaluate_resume(st.session_state.resume_content, st.session_state.job_text)
                progress_bar.empty()
        
        evaluation_container = st.container(height=600)

        if "evaluation" in st.session_state:
            display_evaluation(evaluation_container)

    with tab2:
        if ("resume_content" in st.session_state) and (st.session_state.job_text != ""):
            run_chat_agent(st.session_state.resume_content, st.session_state.job_text)