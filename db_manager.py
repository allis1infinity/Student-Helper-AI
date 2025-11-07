import random

from models import db, MathQuestion

def get_questions(num_questions):
    questions = MathQuestion.query.all()
    random_questions = random.sample(questions, num_questions)
    question_ids_list = [question.id for question in random_questions]
    return question_ids_list


def get_one_question(question_id):
    return MathQuestion.query.get(question_id)


def get_text_correct_answer(question):

    if question.correct_answer == 'A':
        return 'A',question.option_a
    if question.correct_answer == 'B':
        return 'B', question.option_b
    if question.correct_answer == 'C':
        return 'C',question.option_c
    if question.correct_answer == 'D':
        return 'D', question.option_d
    else:
        return 'No answer'



