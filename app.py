from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from ai_explanation import (generate_detailed_explanation,
                                 generate_chat_response,
                                 initialize_chat_history)
from models import db
import redis
from flask_session import Session
import os
from db_manager import get_questions, get_one_question, get_text_correct_answer

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
db_file_name = os.path.join(data_dir, 'questions.db')

load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = redis.StrictRedis(host='localhost', port=6379, db=0)
Session(app)

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/math/home')
# This is the entry point for the test.
# It just shows a welcome message and a 'Start' button.
def home():
    return render_template('start_math_test.html')


@app.route('/math/start')
# This is the initialization route. It randomly selects 20 question
# IDs from the database and saves this unique list into the user's
# session. It then redirects the user to Question 1.
def math_start():
    questions_num = 3
    questions_ids_list = get_questions(questions_num)
    session['questions_ids_list'] = questions_ids_list
    session['user_answers'] = {}
    return redirect(url_for('show_math_question', index=0))

@app.route('/math/questions/<int:index>')
# "This displays the question. It uses the index (0, 1, 2, etc.)
# to fetch the correct question ID from the session, retrieves
# the content from the database, and renders the form."
def show_math_question(index):
    questions_ids_list = session.get('questions_ids_list')
    total_questions = len(questions_ids_list)

    question_id = questions_ids_list[index]

    question_to_show = get_one_question(question_id)

    session.pop('current_question_id', None)
    session.pop('current_explanation_text', None)
    session.pop('chat_history', None)

    return render_template('show_question.html',
                           question=question_to_show,
                           total_questions=total_questions,
                           current_index=index
                           )

@app.route('/math/answer/<int:index>', methods=['POST'])
# This is where the user's selection is sent. We simply store the
# question ID and the user's answer into the session data.
# We DO NOT check for correctness here. Then, we redirect to the
# next question.
def handle_math_answer(index):
    question_id = request.form['question_id']
    user_answer = request.form['user_answer']
    user_answers = session.get('user_answers', {})
    user_answers[question_id] = user_answer
    session['user_answers'] = user_answers
    session.modified = True
    next_index = index + 1
    if next_index >= len(session['questions_ids_list']):
        return redirect(url_for('show_math_result'))
    return redirect(url_for('show_math_question', index=next_index))


@app.route('/math/result')
#This is the final report page. It takes all the user's answers
# from the session, sends them to our database manager for full
# verification, and then displays the total score and the detailed
# report (right/wrong)."
def show_math_result():
    questions_ids_list = session.get('questions_ids_list')
    user_answers = session.get('user_answers')
    print(user_answers)
    print(questions_ids_list)
    total_questions = len(questions_ids_list)

    result_list = []
    correct_count = 0

    for question_id in questions_ids_list:
        question = get_one_question(question_id)
        user_answer = (user_answers.get(str(question_id)))
        correct_answer = get_text_correct_answer(question)

        is_correct = user_answer == question.correct_answer
        if is_correct:
            correct_count += 1

        result_list.append({ "id": question.id,
                             "question_text": question.question_text,
                             "user_answer": user_answer,
                             "correct_answer": correct_answer,
                             "is_correct": is_correct })

    session['result_list'] = result_list

    return render_template(
        "show_math_result.html",
                           result = result_list,
                           correct_count = correct_count,
                           total_questions = total_questions,
                           questions_ids_list=questions_ids_list
    )


@app.route('/explanation/<int:question_id>/<string:subject_name>')
# This route performs two main tasks: generates the static explanation and
# initializes the chat session.
def show_deep_explanation(question_id, subject_name):

    if session.get('current_question_id') != question_id :
        session['current_question_id'] = question_id

        result_list = session.get('result_list', [])
        question = None
        for q in result_list:
            if q['id'] == question_id:
                question = q
                break

        ai_explanation_text = generate_detailed_explanation(
            question_text=question['question_text'],
            correct_answer=question['correct_answer'],
            is_correct=question['is_correct'],
            subject_name=subject_name
        )

        session['current_explanation_text'] = ai_explanation_text

        # --- CHAT history generation ---
        session['chat_history'] = initialize_chat_history(question_text=question['question_text'],
                                                          ai_explanation=ai_explanation_text)
        session.modified = True
    else:
        ai_explanation_text = session.get('current_explanation_text')

    return render_template('ai_explanation.html',
                           explanation_text=ai_explanation_text,
                           question_id=question_id,
                           subject_name=subject_name)

@app.route('/chat/submit/<int:question_id>/<string:subject_name>', methods=[
    'POST'])
def handle_chat_submit(question_id, subject_name):
    user_message = request.form.get('user_message')
    chat_history = session.get('chat_history', [])

    if user_message and chat_history:
        chat_history.append({"role": "user", "content": user_message})

        ai_chat_response_text = generate_chat_response(chat_history)
        chat_history.append({"role": "assistant", "content": ai_chat_response_text})

        session['chat_history'] = chat_history
        session.modified = True

    return redirect(url_for('show_deep_explanation', question_id=question_id, subject_name=subject_name))

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    #     print('Database created successfully!')
    app.run(host='0.0.0.0', port= 5007, debug=True)


