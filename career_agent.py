# In career_agent.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

def get_career_suggestions(survey_data: dict):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.5)

    json_format = """
    {{
      "careers": [
        {{
          "career_name": "Name of the career path",
          "average_salary": "Average starting salary in INR, e.g., '₹6-8 Lakhs per annum'",
          "top_colleges": {{
            "government": [
              {{ "College Name": "...", "Fees Range": "...", "Location": "...", "Entrances Required": "...", "Difficulty Level": "...", "Average Package": "..." }},
              {{ "College Name": "...", "Fees Range": "...", "Location": "...", "Entrances Required": "...", "Difficulty Level": "...", "Average Package": "..." }},
              "... 8 more colleges ..."
            ],
            "private": [
              {{ "College Name": "...", "Fees Range": "...", "Location": "...", "Entrances Required": "...", "Difficulty Level": "...", "Average Package": "..." }},
              {{ "College Name": "...", "Fees Range": "...", "Location": "...", "Entrances Required": "...", "Difficulty Level": "...", "Average Package": "..." }},
              "... 8 more colleges ..."
            ]
          }},
          "reasoning": "A brief paragraph explaining why this career is a good fit for the student."
        }}
      ]
    }}
    """

    # UPDATED PROMPT to be extremely forceful and explicit
    prompt_template = """
    You are an expert career counselor AI. Your task is to provide three career path suggestions based on the student's profile.

    **Student Profile:**
    - Strongest Subjects: {subjects}
    - Class 12th Score: {score}%
    - Interests & Hobbies: {interests}
    - Work Style Preference: {work_style}
    - College Fee Budget: {budget} per year
    - Willingness to Relocate: {relocate}
    - Home State: {home_state}
    - Preferred Cities: {cities}

    **PRIMARY DIRECTIVE:**
    Your single most important task is to generate comprehensive college lists. For EACH of the 3 career paths suggested, you MUST generate two lists of colleges: one for "government" and one for "private".

    **NON-NEGOTIABLE RULE:**
    **EACH of these lists (government and private) MUST CONTAIN EXACTLY 10 colleges.**
    - Your response will be considered a failure if you provide fewer than 10 colleges in any list.
    - The colleges in each list of 10 must be sorted by the latest available NIRF rankings.
    - If 'Willingness to Relocate' is 'No', prioritize colleges within the student's 'Home State'.

    Your entire response MUST be a single, valid JSON object that follows this exact format, with no other text or commentary.
    {format_instructions}
    """

    parser = JsonOutputParser()
    prompt = ChatPromptTemplate.from_template(
        template=prompt_template,
        partial_variables={"format_instructions": json_format}
    )
    chain = prompt | llm | parser

    max_retries = 3
    for i in range(max_retries):
        try:
            print(f"Attempt {i+1} of {max_retries} to call the AI...")
            response = chain.invoke(survey_data)
            return response
        except OutputParserException as e:
            print(f"Attempt {i+1} failed: The AI did not return valid JSON. Retrying... Error: {e}")
            if i == max_retries - 1:
                raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            if i == max_retries - 1:
                raise e
    
    return None