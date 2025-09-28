from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate

def evaluate_resume(resume: str, job_description: str) -> dict:
    """
    Analyzes a resume against a job description using the standard Gemini API,
    providing a detailed, structured evaluation.
    """
    
    # Reverted to the standard ChatGoogleGenerativeAI model which works with your setup
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.0)

    # --- NEW, DETAILED RESPONSE STRUCTURE ---
    
    # Define schemas for individual metrics
    education_schema = ResponseSchema(name="education_relevance", description="A score out of 10 for education relevance.")
    skills_schema = ResponseSchema(name="matching_skills", description="A score out of 10 for how well the candidate's skills match the job.")
    projects_schema = ResponseSchema(name="project_relevance", description="A score out of 10 for the relevance of the candidate's projects.")
    industry_schema = ResponseSchema(name="industry_standard", description="A score out of 10 for how the resume compares to the industry standard.")
    global_score_schema = ResponseSchema(name="global_score", description="The final weighted average score out of 10.")
    title_schema = ResponseSchema(name="title", description="The job title and company name, formatted as 'Job Title at Company'.")

    # Define schema for the "Areas to Improve" table
    improvements_schema = ResponseSchema(
        name="areas_to_improve",
        description="A list of 3-5 key areas the candidate should focus on. This must be a list of JSON objects."
    )

    response_schemas = [
        education_schema,
        skills_schema,
        projects_schema,
        industry_schema,
        global_score_schema,
        title_schema,
        improvements_schema
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    # --- NEW, DETAILED PROMPT ---
    template = (
        """
        You are an expert technical recruiter and career coach. Your task is to provide a detailed, structured evaluation of a candidate's resume against a specific job description.

        **Resume:**
        {resume}

        **Job Description:**
        {job_description}

        **CRITICAL INSTRUCTIONS:**
        1.  Analyze the resume and job description to evaluate the candidate on the following five metrics:
            - **Education Relevance:** How well does their education align with the job's requirements?
            - **Matching Skills:** How many of the required technical skills and keywords are present in their resume?
            - **Project Relevance:** How relevant are their personal or academic projects to the job's responsibilities?
            - **Industry Standard:** How does the resume's quality (formatting, clarity, impact statements) compare to the industry standard for this role?
        2.  For each metric, provide a score out of 10.
        3.  Calculate a **Global Score** by taking the simple average of the four scores above.
        4.  Based on a gap analysis, identify 3-5 **Key Areas to Improve**. For each area, you MUST provide:
            - **Importance:** How critical is this for the job (High, Medium, Low)?
            - **Your Current Level:** Assess the candidate's current level based on their resume (Beginner, Intermediate, Advanced).
            - **Approx. Time to Prepare:** A realistic estimate for how long it would take to become interview-ready in this area.
        5.  Your entire response MUST be a single, valid JSON object. Do not include any other text, explanations, or markdown formatting outside of the JSON structure.

        {format_instructions}
        """
    )
    
    prompt = ChatPromptTemplate.from_template(template=template)
    chain = prompt | llm | output_parser

    # --- THIS IS THE FIX ---
    # The 'format_instructions' variable must be passed to the chain.
    response = chain.invoke({
        "resume": resume,
        "job_description": job_description,
        "format_instructions": format_instructions
    })
    return response

