from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client =OpenAI(api_key=os.getenv('OPEN_API_KEY'))

system_prompt = """
You are a highly qualified, friendly, and supportive expert tutor for high school students. 
Provide a clear, step-by-step solution, focusing on logic. 
Use clear headings, bold text, and lists (where applicable) to visually separate points.
Use LaTeX for all mathematical expressions. 
**CRITICAL:** Every new thought or logical step, even within a single section, must be separated by a double line break (\n\n) 
to ensure proper paragraph rendering.
Be positive and encouraging.
"""


def generate_detailed_explanation(question_text, correct_answer, is_correct, subject_name):
    if is_correct:
        greeting_instruction = "START RESPONSE WITH: 'Great job! 🎉 You nailed it. Let's quickly review the steps to lock in your knowledge.'"
    else:
        greeting_instruction = ("START RESPONSE WITH: 'Keep pushing! 💪 Mistakes are just steps toward success. Let's break down this problem together "
                                "so you know exactly how to tackle it next time.'")

    user_prompt = f"""### FUNCTION CALL: GENERATE_NMT_SOLUTION
    ## INPUT PARAMETERS
    - SUBJECT_NAME: {subject_name}
    - TASK_BODY: {question_text}
    - CORRECT_ANSWER: {correct_answer}
    - STUDENT_STATUS_MESSAGE: {greeting_instruction}
    ---
    ## OUTPUT SPECIFICATION (STRICT FORMAT)
    You are an Expert NMT Tutor for high-school students (ages 16–17). Your tone must be supportive, structured, and educational.
    All output must be written in Ukrainian. The response must contain exactly three Markdown sections in this order:
    ### 1. Task Analysis
    Header: ## 🌟 Task Analysis  
    Acknowledge the STUDENT_STATUS_MESSAGE and briefly explain what the task is about without revealing the final answer.
    ### 2. Correct Solution (Step-by-Step)
    Header: ## ✅ Correct Solution (Step-by-Step)  
    Provide a clear numbered list (1., 2., 3., …). Highlight key rules with **bold text** and use LaTeX ($...$) for all formulas and
    mathematical expressions. Tailor the explanation to the SUBJECT_NAME.
    ### 3. Key Takeaway
    Header: ## 💡 Key Takeaway for NMT  
    Provide exactly one practical, generalizable learning tip the student can apply in future NMT tasks.
    ## HARD CONSTRAINTS
    Follow the three-section structure exactly. Do not add extra commentary before or after the sections. Keep the language simple, clear, 
    and academically precise."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
        max_tokens=1500
    )

    explanation = response.choices[0].message.content

    return explanation




