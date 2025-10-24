import random

from models import db, MathQuestion

def get_questions(num_questions):
    questions = MathQuestion.query.all()
    random_questions = random.sample(questions, num_questions)
    question_ids_list = [question.id for question in random_questions]
    return question_ids_list


def get_one_question(question_id):
    return MathQuestion.query.get(question_id)

