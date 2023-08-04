from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db = SQLAlchemy(app)

CORS(app)



class Participant(db.Model):
	id_num = db.Column(db.Integer, primary_key=True)
	name   = db.Column(db.String(80))
	age    = db.Column(db.String(80))
	phone  = db.Column(db.String(80))
	gender = db.Column(db.String(80))
	edu    = db.Column(db.String(80))
	job    = db.Column(db.String(80))
	freq   = db.Column(db.Integer)
	gen_ai_friendliness = db.Column(db.Integer)
	llm_friendliness    = db.Column(db.Integer)
	prompting_friendliness = db.Column(db.Integer)

    
	def __repr__(self):
		return '<Participant %r>' % self.id_num
	
with app.app_context():
	if not os.path.exists('database.db'):
		db.create_all()


@app.route('/')
def index():
	return "TEST"

@app.route('/register', methods=["POST"])
def register():
	param = request.args.get("id")
	if param:
		participant = Participant(id_num=int(param))
		db.session.add(participant)
		db.session.commit()
		return "OK"
	else:
		return "ERROR"
	
@app.route('/demographics', methods=["POST"])
def demographics():
	args = request.args
	id_num = args.get("id")

	participant = Participant.query.filter_by(id_num=id_num).first()
	participant.name = args.get("name")
	participant.age = args.get("age")
	participant.phone = args.get("phone")
	participant.gender = args.get("gender")
	participant.edu = args.get("edu")
	participant.job = args.get("job")
	participant.freq = int(args.get("freq"))
	participant.gen_ai_friendliness = int(args.get("gen_ai_friendliness"))
	participant.llm_friendliness = int(args.get("llm_friendliness"))
	participant.prompting_friendliness = args.get("prompting_friendliness")

	db.session.commit()

	return "OK"



if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8888)

