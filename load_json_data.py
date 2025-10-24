import json
import os
from models import db, MathQuestion
from flask import Flask


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, 'data')
db_file_name = os.path.join(data_dir, 'questions.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def load_data_from_json(json_file):
    """Load data from JSON file into the database."""
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f'ERROR! File {json_file} not found.')
    except json.decoder.JSONDecodeError:
        print(f'ERROR! File {json_file} could not be decoded (invalid JSON).')


    with app.app_context():
        db.create_all()
        db.session.query(MathQuestion).delete()

        for question in data:
            new_question = MathQuestion(
                question_text = question['question_text'],
                option_a = question['option_a'],
                option_b = question['option_b'],
                option_c = question['option_c'],
                option_d = question['option_d'],
                correct_answer = question['correct_option'],
                topic = question.get('topic', 0)
            )
            db.session.add(new_question)

        db.session.commit()
        print(f'Successfully added {len(data)} questions!')

if __name__ == '__main__':
    load_data_from_json('math_question.json')




