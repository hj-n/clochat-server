from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import os

from register import register_tasks, register_participant, register_demographics, register_task_order, register_conversation_start, register_new_conversation, register_survey_answer, register_new_persona, register_persona_dialogue, register_persona_img, register_is_category_finished

from retreive import retreive_current_task_trial_indices, retrieve_task_info, retreive_conversations, retreive_persona_dialogue, retreive_persona_info, retreive_persona_preview, retreive_persona_info_list, retreive_next_persona_num, retreive_next_trial_index

from status_check import is_study_complete

from chatgpt_communication import get_new_answer_chatgpt, get_translation_dalle_prompt, get_new_answer_clochat
from dalle_communication import get_new_images

import json

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
	task_index = db.Column(db.Integer)
	trial_index = db.Column(db.Integer)
	## connected Participant
	participant = db.Column(db.Integer, db.ForeignKey('participant.id_num'))

	is_start = db.Column(db.Boolean)
	is_end	 = db.Column(db.Boolean)

	## conversation data
	content      = db.Column(db.String(3600))
	role         = db.Column(db.String(80))
	study_type   = db.Column(db.String(80))

class SurveyAnswer(db.Model):
	survey_id = db.Column(db.Integer, primary_key=True)
	## connected Participant
	participant = db.Column(db.Integer, db.ForeignKey('participant.id_num'))
	## connected Task
	task = db.Column(db.Integer, db.ForeignKey('task.task_id_num'))
	task_index = db.Column(db.Integer)
	study_type = db.Column(db.String(80))
	survey_type = db.Column(db.String(80))
	survey_result = db.Column(db.String(3600))

class Persona(db.Model):
	persona_id = db.Column(db.Integer, primary_key=True)
	## connected Participant
	participant = db.Column(db.Integer, db.ForeignKey('participant.id_num'))
	persona_num = db.Column(db.Integer)
	input_dialogue = db.Column(db.String(100000))
	is_category_finished = db.Column(db.String(80))
	system_prompt = db.Column(db.String(10000))
	kr_prompt = db.Column(db.String(3600))
	en_prompt = db.Column(db.String(3600))
	img_urls = db.Column(db.String(3600))
	img_url_index = db.Column(db.Integer)


"""
Server functions
"""

@app.route('/', methods=["GET"])
def hello_world():
	return "Hello, World!"


@app.route('/register', methods=["POST"])
def register():
	id_num = request.args.get("id")
	if id_num:
		if len(Participant.query.filter_by(id_num=id_num).all()) == 0:
			register_participant(db, Participant, id_num)
			register_task_order(db, Task, Participant, id_num)
			register_conversation_start(db, Conversation, Participant, id_num, 0, 0,"chatgpt")
		return "OK"
	else:
		return "ERROR"
	
@app.route('/demographics', methods=["POST"])
def demographics():
	args = request.args
	register_demographics(db, Participant, args)
	return "OK"


@app.route('/currenttasktrialindices', methods=["GET"])
def get_current_task_indices():
	args = request.args
	id_num = args.get("id")
	study_type = args.get("studyType")

	if id_num and study_type:
		task_indices, trial_indices = retreive_current_task_trial_indices(Conversation, id_num, study_type)
		return jsonify({
			"taskIndices": task_indices,
			"trialIndices": trial_indices
		})
	else:
		return "ERROR"

@app.route('/taskinfo', methods=["GET"])
def get_task_info():
	args = request.args
	id_num     = args.get("id")
	task_index = args.get("index")
	study_type = args.get("studyType")

	if task_index and study_type:
		task_info = retrieve_task_info(Participant, Task, id_num, task_index, study_type)
		return jsonify(task_info)
	else:
		return "ERROR"
	
@app.route('/postconversation', methods=["POST"])
def post_conversation():
	args = request.args
	id_num     = args.get("id")
	task_index = args.get("taskIndex")
	trial_index = args.get("trialIndex")
	content 	 = args.get("content")
	study_type = args.get("studyType")
	persona_num = args.get("personaNum")
	role 		   = "user"

	if id_num and task_index and content and study_type:
		register_new_conversation(db, Conversation, Participant, id_num, task_index, trial_index, study_type, content, role)
		conversations = retreive_conversations(Conversation, id_num, task_index, trial_index, study_type)
		if study_type == "chatgpt":
			answer = get_new_answer_chatgpt(conversations)
		elif study_type == "clochat":
			answer = get_new_answer_clochat(db, Persona, conversations, id_num, persona_num)
		register_new_conversation(db, Conversation, Participant, id_num, task_index, trial_index, study_type, answer, "assistant")

		return "OK"

@app.route('/getconversations', methods=["GET"])
def get_conversations():
	args = request.args
	id_num = args.get("id")
	task_index = args.get("taskIndex")
	trial_index = args.get("trialIndex")
	study_type = args.get("studyType")

	if id_num and task_index and study_type:
		conversations = retreive_conversations(Conversation, id_num, task_index, trial_index, study_type)
		conversations_json = []
		for conversation in conversations:
			if conversation.is_start or conversation.is_end:
				continue
			conversations_json.append({"content": conversation.content, "role": conversation.role})
		return jsonify(conversations_json)
	else:
		return "ERROR"

@app.route('/postconversationstart', methods=["POST"])
def post_conversation_start():
	args = request.args
	id_num = args.get("id")
	task_index = args.get("taskIndex")
	trial_index = args.get("trialIndex")
	study_type = args.get("studyType")

	if id_num and task_index and study_type and trial_index:
		register_conversation_start(db, Conversation, Participant, id_num, task_index, trial_index, study_type)
		return "OK"
	else:
		return "ERROR"

@app.route('/postsurveyresult', methods=["POST"])
def post_survey_result():
	args = request.args
	id_num = args.get("id")
	task_index = args.get("taskIndex")
	study_type = args.get("studyType")
	survey_type = args.get("surveyType")
	survey_result = args.get("surveyResult")

	if id_num and task_index and study_type and survey_type and survey_result:
		register_survey_answer(db, SurveyAnswer, Participant, id_num, task_index, study_type, survey_type, survey_result)
		return "OK"
	else:
		return "ERROR"


@app.route('/checkstudycomplete', methods=["GET"])
def check_study_complete():
	args = request.args
	id_num = args.get("id")
	study_type = args.get("studyType")
	task_index = args.get("taskIndex")

	if id_num and study_type and task_index:
		return jsonify({"isComplete": is_study_complete(Participant, id_num, study_type, task_index)})
	else:
		return "ERROR"

@app.route('/postnewpersona', methods=["POST"])
def post_new_persona():
	args = request.args
	id_num = args.get("id")
	persona_num = args.get("personaNum")
	
	if id_num and persona_num:
		register_new_persona(db, Persona, id_num, persona_num)
		return "OK"
	else:
		return "ERROR"

@app.route('/getpersonadialogue', methods=["GET"])
def get_persona_dialogue():
	args = request.args
	id_num = args.get("id")
	persona_num = args.get("personaNum")

	if id_num and persona_num:

		result = retreive_persona_dialogue(Persona, id_num, persona_num)
		return jsonify({
			"dialogue": result["dialogue"],
			"isCategoryFinished": result["is_category_finished"]
		})
	else:
		return "ERROR"
	
@app.route('/postpersonadialogue', methods=["POST"])
def post_persona_dialogue():
	args = request.args
	id_num = args.get("id")
	persona_num = args.get("personaNum")
	dialogue = args.get("dialogue")
	is_category_finished = args.get("isCategoryFinished")


	if id_num and persona_num and dialogue:
		register_persona_dialogue(db, Persona, id_num, persona_num, dialogue, is_category_finished)
		return "OK"
	else:
		return "ERROR"
	
@app.route('/postiscategoryfinished', methods=["POST"])
def post_is_category_finished():
	args = request.args
	id_num = args.get("id")
	persona_num = args.get("personaNum")
	is_category_finished = args.get("isCategoryFinished")

	if id_num and persona_num and is_category_finished:
		register_is_category_finished(db, Persona, id_num, persona_num, is_category_finished)
		return "OK"
	else:
		return "ERROR"
	
@app.route('/getgeneratedimageurls', methods=["GET"])
def get_generated_image_urls():
	args = request.args
	prompt_kr = args.get("prompt")

	if prompt_kr:
		prompt_en = get_translation_dalle_prompt(prompt_kr)
		image_urls = get_new_images(prompt_en)
		return jsonify({
			"promptEn": prompt_en,
			"imageUrls": image_urls
		})
	else:
		return "ERROR"
		

@app.route('/postpersonaimg', methods=["POST"])
def post_persona_img():
	args = request.args
	id_num = args.get("id")
	persona_num = args.get("personaNum")
	img_urls = args.get("imgUrls")
	img_url_index = args.get("imgUrlIndex")
	prompt_kr = args.get("promptKr")
	prompt_en = args.get("promptEn")

	if id_num and persona_num and img_urls and img_url_index:
		register_persona_img(db, Persona, id_num, persona_num, img_urls, img_url_index, prompt_kr, prompt_en)
		return "OK"
	else:
		return "ERROR"

@app.route('/getpersonainfo', methods=["GET"])
def get_persona_info():
	args = request.args
	id_num = args.get("id")
	persona_num = args.get("personaNum")

	if id_num and persona_num:
		persona_info = retreive_persona_info(Persona, id_num, persona_num)
		return jsonify(persona_info)
	else:
		return "ERROR"

@app.route('/getpersonapreview', methods=["GET"])
def get_persona_preview():
	args = request.args
	id_num = args.get("id")
	persona_num = args.get("personaNum")
	preview_prompt = args.get("previewPrompt")

	if id_num and persona_num and preview_prompt:
		preview_answer = retreive_persona_preview(Persona, id_num, persona_num, preview_prompt)
		return preview_answer
	else:
		return "ERROR"
	
@app.route('/getpersonainfolist', methods=["GET"])
def get_persona_info_list():
	args = request.args
	id_num = args.get("id")

	if id_num:
		persona_info_list = retreive_persona_info_list(Persona, id_num)
		return jsonify(persona_info_list)
	else:
		return "ERROR"


@app.route('/getnextpersonanum', methods=["GET"])
def get_next_persona_num():
	args = request.args
	id_num = args.get("id")

	if id_num:
		return str(retreive_next_persona_num(Persona, id_num))
	else:
		return "ERROR"


@app.route('/getnexttrialindex', methods=["GET"])
def get_next_trial_index():
	args = request.args
	id_num = args.get("id")
	task_index = args.get("taskIndex")
	study_type = args.get("studyType")

	if id_num and study_type:
		return str(retreive_next_trial_index(Conversation, id_num, task_index, study_type))
	else:
		return "ERROR"


with app.app_context():
	if not os.path.exists('database.db'):
		db.create_all()

	if len(Task.query.all()) == 0:
		register_tasks(db, Task)


if __name__ == '__main__':


	app.run(host='0.0.0.0', port=9109)

	## if db task is not itiniated, init it


