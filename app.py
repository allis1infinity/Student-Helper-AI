from flask import Flask, render_template, request, redirect, url_for, session
from models import db, MathQuestion
import os
from db_manager import get_questions, get_one_question
from dotenv import load_dotenv
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
    questions_num = 25
    questions_ids_list = get_questions(questions_num)
    session['questions_ids_list'] = questions_ids_list
    session['user_answer'] = {}
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
    return render_template('show_question.html',
                           question=question_to_show,
                           total_questions=total_questions,
                           current_index=index
                           )

@app.route('/math/answer', methods=['POST'])
# This is where the user's selection is sent. We simply store the
# question ID and the user's answer into the session data.
# We DO NOT check for correctness here. Then, we redirect to the
# next question.
def handle_math_answer():
    pass

@app.route('/math/result')
#This is the final report page. It takes all the user's answers
# from the session, sends them to our database manager for full
# verification, and then displays the total score and the detailed
# report (right/wrong)."
def show_math_result():
    pass


@app.route('/math/explanation/<int:question_id>')
# This is our special feature. When the student clicks a button on
# the result page, this route is triggered. It calls the LLM service
# to generate a detailed, step-by-step solution for that specific
# math problem.
def show_math_deep_explanation():
    pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Database created successfully!')
    app.run(host='0.0.0.0', port= 5001, debug=True)


