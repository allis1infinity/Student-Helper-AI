from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MathQuestion(db.Model):
    __tablename__ = 'math_questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String, nullable=False)
    option_b = db.Column(db.String, nullable=False)
    option_c = db.Column(db.String, nullable=False)
    option_d = db.Column(db.String, nullable=False)
    correct_answer = db.Column(db.String, nullable=False)
    topic = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'Question {self.id}: {self.topic}'