from flask import Flask, render_template, request, redirect, url_for
from models import db, MathQuestion
import os
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
db_file_name = os.path.join(data_dir, 'questions.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('Database created successfully!')
    app.run(host='0.0.0.0', port= 5001, debug=True)


