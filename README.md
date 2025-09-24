CareeroAI 🧠
Your personal AI-powered career assistant, designed to guide you at every stage of your professional journey.

CareeroAI is a multi-page web application built with Streamlit and powered by Google's Gemini AI. It offers two distinct modules to cater to different user needs: one for students and professionals preparing for interviews, and another for high school students exploring potential career paths.

✨ Features
CareeroAI is divided into two main sections:

1. Interview Prep (For College Students & Professionals)
This tool helps you bridge the gap between your resume and your dream job.

AI-Powered Resume Evaluation: Upload your resume and paste a job description to get an instant, detailed analysis of how well you match the role.

Detailed Scoring: Receive scores (out of 10) for your skills, experience, and education, along with a weighted global score.

Constructive Feedback: Get a breakdown of your strengths ("Positive Points") and areas for improvement ("Negative Points").

Interactive Chatbot: Practice for your interview by asking questions related to the job description and your resume in a conversational chat.

History Tracking: The app saves your previous evaluations, allowing you to revisit them at any time.

2. Career Path Finder (For High Schoolers)
For students who are unsure about their future, this tool provides personalized guidance.

Comprehensive Survey: Fill out a detailed survey covering your academic strengths, personal interests, work style, and college preferences (including budget and location).

Personalized Career Suggestions: The AI analyzes your profile and suggests the top 3 most suitable career paths for you.

In-Depth Insights: For each career path, get detailed information including:

A clear reasoning for why it's a good fit.

The average starting salary in India.

Top 10 Government and Private Colleges sorted by the latest NIRF rankings.

Detailed College Information: View colleges in clean, tabular format with details on Fees Range, Location, Entrances Required, and Average Package.

🛠️ Tech Stack
Backend: Python

Frontend: Streamlit

AI/LLM: Google Gemini Pro via the google-generativeai library

Core Logic: LangChain

Data Handling: Pandas

🚀 Getting Started
Follow these instructions to set up and run the project on your local machine.

Prerequisites
Python 3.12 or higher

A Google AI API key

Installation & Setup
Clone the repository (or download the source code):

git clone [https://github.com/your-username/CareeroAI.git](https://github.com/your-username/CareeroAI.git)
cd CareeroAI

Create and activate a virtual environment:

# For Windows
py -3.12 -m venv .venv
.\.venv\Scripts\Activate

Install the required dependencies:

pip install -r requirements.txt

Create your environment file:

Create a new file named .env in the root of your project directory.

Add your Google AI API key to this file:

GOOGLE_API_KEY="PASTE_YOUR_API_KEY_HERE"

How to Run the Application
Once the setup is complete, run the following command in your terminal:

streamlit run Home.py

The application will open in a new tab in your web browser.

📂 Project Structure
The project uses Streamlit's multi-page app feature:

Home.py: The main landing page of the application.

pages/: This directory contains all the other pages of the app.

1_Interview_Prep.py: The code for the resume evaluator and chatbot.

2_Career_Path_Finder.py: The code for the high school student survey and career recommender.

career_agent.py, chat_agent.py, evaluator_agent.py: These files contain the backend logic for interacting with the Gemini AI.

🤝 Contributing
Contributions are welcome! If you have ideas for new features or improvements, feel free to open an issue or submit a pull request.

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.