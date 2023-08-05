from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import os

from register import register_tasks, register_participant, register_demographics, register_task_order, register_conversation_start

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db = SQLAlchemy(app)
CORS(app)

"""
Model for the database
"""



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
	clochat_list = db.Column(db.String(80))
	chatgpt_list = db.Column(db.String(80))

    
	def __repr__(self):
		return '<Participant %r>' % self.id_num
	
class Task(db.Model):
	task_id_num = db.Column(db.Integer, primary_key=True)
	type        = db.Column(db.String(80))
	title       = db.Column(db.String(80))
	description = db.Column(db.String(3600))

class Conversation(db.Model):
	conver_id = db.Column(db.Integer, primary_key=True)
	## connected Task
	task = db.Column(db.Integer, db.ForeignKey('task.task_id_num'))
	## connected Participant
	participant = db.Column(db.Integer, db.ForeignKey('participant.id_num'))

	is_start = db.Column(db.Boolean)
	is_end	 = db.Column(db.Boolean)

	## conversation data
	conversation = db.Column(db.String(3600))
	speaker      = db.Column(db.String(80))


"""
Server functions
"""


@app.route('/register', methods=["POST"])
def register():
	id_num = request.args.get("id")
	if id_num:
		if len(Participant.query.filter_by(id_num=id_num).all()) == 0:
			register_participant(db, Participant, id_num)
			register_task_order(db, Task, Participant, id_num)
			register_conversation_start(db, Conversation, Participant, id_num, 0, "chatgpt")
			register_conversation_start(db, Conversation, Participant, id_num, 1, "clochat")
		return "OK"
	else:
		return "ERROR"
	
@app.route('/demographics', methods=["POST"])
def demographics():
	args = request.args
	register_demographics(db, Participant, args)
	return "OK"



with app.app_context():
	if not os.path.exists('database.db'):
		db.create_all()

	if len(Task.query.all()) == 0:
		register_tasks(db, Task)


if __name__ == '__main__':


	app.run(debug=True, host='0.0.0.0', port=8888)

	## if db task is not itiniated, init it


