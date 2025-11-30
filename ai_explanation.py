import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPEN_API_KEY'))

EXPLANATION_SYSTEM_PROMPT = """
You are a highly qualified, friendly, and supportive expert tutor for high school students. 
Provide a clear, step-by-step solution, focusing on logic. 
Use clear headings, bold text, and lists (where applicable) to visually separate points.
Use LaTeX for all mathematical expressions. 
Use English language for explanation.
**CRITICAL:** Every new thought or logical step, even within a single section, must be separated by a double line break (\n\n) 
to ensure proper paragraph rendering.

IMPORTANT GREETING RULES:
- If the student answered CORRECTLY: Start your response with encouraging words like "Great job! 🎉 You nailed it. Let's quickly review the steps to lock in your knowledge."
- If the student answered INCORRECTLY: Start your response with supportive words like "Keep pushing! 💪 Mistakes are just steps toward success. Let's break down this problem together so you know exactly how to tackle it next time."

After the greeting, provide the full detailed explanation.
Be positive and encouraging throughout.
"""

CHAT_SYSTEM_PROMPT = """
You are a friendly and supportive AI assistant dedicated to helping high school students master their learning materials (Math, History, Language Arts, etc.).
Your primary goal is to ensure the student achieves genuine understanding.

CONTEXT: You have just provided a detailed explanation of a problem. The student may now ask follow-up questions about this explanation or related topics.

Your responses must adhere to the following rules:
1.  **Educational Focus:** Be patient and guide the student toward the solution rather than just providing the answer.
2.  **Clarity & Tone:** Maintain an encouraging and friendly tone. Use language that is easy for a high school student to grasp.
3.  **Language:** Respond in English language.
4.  **Formatting:** Use LaTeX formatting for all mathematical or scientific formulas where applicable.
5.  **Encouragement:** End your replies by encouraging the student to ask more follow-up questions for deeper understanding.
6.  **Memory:** Remember the problem you just explained and use that context in your answers.
"""


def generate_detailed_explanation(question_text, correct_answer, is_correct,
                                  subject_name):
    """
    Generates a detailed explanation for a question with greeting integrated inside.

    This function:
    - Creates a prompt based on whether student answered correctly
    - Sends request to OpenAI
    - Returns explanation with greeting at the beginning
    """

    # Build the prompt for OpenAI
    # The AI will automatically add the appropriate greeting based on is_correct
    user_prompt = f"""### TASK: GENERATE DETAILED EXPLANATION

## INPUT PARAMETERS
- SUBJECT: {subject_name}
- PROBLEM: {question_text}
- CORRECT ANSWER: {correct_answer}
- STUDENT WAS CORRECT: {"YES" if is_correct else "NO"}

## YOUR TASK
1. Start with appropriate greeting (encouraging if correct, supportive if incorrect)
2. Provide detailed step-by-step explanation
3. Make sure the student understands the concept

Remember: This explanation will be the first message in a chat, so make it comprehensive and welcoming!
"""

    try:
        # Send request to OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cost-effective model
            messages=[
                {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            # Balanced creativity (0 = deterministic, 1 = creative)
            max_tokens=1500  # Maximum length of response
        )

        # Extract the explanation text from response
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Error generating explanation: {e}")
        return "Sorry, an error occurred while generating the explanation. Please try again later."


def initialize_chat_history(question_text, ai_explanation):
    """
    Initializes chat history with system prompt and first explanation.

    This is crucial: it makes the AI explanation the FIRST message in the chat,
    so the AI remembers everything about the problem in subsequent questions.

    The chat history structure:
    1. System prompt (AI's instructions)
    2. Student's question (what was asked)
    3. AI's explanation (the detailed answer)
    """

    return [
        # Message 1: System instructions (not shown to user)
        {
            "role": "system",
            "content": CHAT_SYSTEM_PROMPT
        },
        # Message 2: Student's original question
        {
            "role": "user",
            "content": question_text
        },
        # Message 3: AI's detailed explanation (first response)
        {
            "role": "assistant",
            "content": ai_explanation
        }
    ]


def generate_chat_response(chat_history):
    """
    Generates AI response to a user message in the chat.

    This function:
    - Takes the full chat history (including previous explanation)
    - Sends it to OpenAI
    - Returns the AI's response
    """

    try:
        # Send full history to OpenAI
        # The AI uses all previous messages as context
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history,  # Full conversation history
            temperature=0.7,
            # Slightly more creative for conversational responses
            max_tokens=500
            # Shorter responses for chat (not initial explanation)
        )

        # Extract and return the response text
        return response.choices[0].message.content

    except Exception as e:

        print(f"❌ Error generating chat response: {e}")
        return "Sorry, an error occurred. Please try again later."


if __name__ == '__main__':
    print("--- 🧪 Запуск тестового режиму AI-логіки ---")

    # 1. Визначення тестових даних
    test_question = "Яким буде результат множення 5x + 3 на 2x - 1?"
    test_correct_answer = "10x^2 + x - 3"
    test_is_correct = True  # Припустимо, студент відповів правильно
    test_subject = "Math"

    # 2. Тестування генерації детального пояснення
    print("\n--- 1. Генерація пояснення ---")
    explanation = generate_detailed_explanation(
        question_text=test_question,
        correct_answer=test_correct_answer,
        is_correct=test_is_correct,
        subject_name=test_subject
    )
    print("Отримане пояснення (перші 100 символів):")
    print(explanation[:100] + "...")

    # 3. Тестування ініціалізації історії чату
    print("\n--- 2. Ініціалізація історії чату ---")
    history = initialize_chat_history(
        question_text=test_question,
        ai_explanation=explanation
    )
    print(
        f"Історія чату ініціалізована. Кількість повідомлень: {len(history)} (Включаючи системний промпт).")

    # 4. Тестування генерації відповіді чату
    print("\n--- 3. Генерація відповіді чату (на запит користувача) ---")
    user_chat_message = "Поясніть, будь ласка, що таке квадратний тричлен."
    history.append({"role": "user", "content": user_chat_message})

    chat_response = generate_chat_response(history)

    print(f"Запит користувача: {user_chat_message}")
    print(f"Відповідь AI (перші 100 символів): {chat_response[:100]}...")

    print("\n--- ✅ Тестування завершено ---")