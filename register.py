import json
import random

TASK_PATH = "./assets/task_generated.json"

def register_tasks(db, Task):
	tasks = json.load(open(TASK_PATH))

	for task in tasks:
		task_id = task["task_id"]
		type    = task["type"]
		title   = task["title"]
		desc    = task["description"]
		task = Task(task_id_num=task_id, type=type, title=title, description=desc)
		db.session.add(task)
	
	db.session.commit()


def register_participant(db, Participant, id_num):
	participant = Participant(id_num=id_num)
	db.session.add(participant)
	db.session.commit()

def register_task_order(db, Task, Participant, id_num):
	## get list of task types
	task_types = Task.query.with_entities(Task.type).distinct().all()
	task_types = [t[0] for t in task_types]

	clochat_list = []
	chatgpt_list = []

	for task_type in task_types:
		tasks = Task.query.filter_by(type=task_type).all()
		task_ids = [t.task_id_num for t in tasks]
		random.shuffle(task_ids)
		clochat_list += task_ids[:2]
		chatgpt_list += task_ids[2:]

	random.shuffle(clochat_list)
	random.shuffle(chatgpt_list)
	
	participant = Participant.query.filter_by(id_num=id_num).first()
	participant.clochat_list = json.dumps(clochat_list)
	participant.chatgpt_list = json.dumps(chatgpt_list)

	db.session.commit()

def get_task_id(Participant, study_type, id_num, task_index):
	participant = Participant.query.filter_by(id_num=id_num).first()
	if study_type == "chatgpt":
		task_list = json.loads(participant.chatgpt_list)
	elif study_type == "clochat":
		task_list = json.loads(participant.clochat_list)
	
	task_id = task_list[int(task_index)]
	return task_id

def register_conversation_start(db, Conversation, Participant, id_num, task_index, trial_index, study_type, persona_num):
	task_id = get_task_id(Participant, study_type, id_num, task_index)

	conversation = Conversation(task=task_id, task_index=task_index, trial_index=trial_index, participant=id_num, is_start=True, is_end=False, content="", role="", study_type=study_type)
	
	if study_type == "clochat":
		conversation.related_persona = persona_num

	db.session.add(conversation)
	db.session.commit()

def register_new_conversation(db, Conversation, Participant, id_num, task_index, trial_index, study_type, content, role, persona_num):
	task_id = get_task_id(Participant, study_type, id_num, task_index)

	conversation = Conversation(
		task=task_id,
		task_index=task_index,
		trial_index=trial_index,
		participant=id_num,
		is_start=False,
		is_end=False,
		content=content,
		role=role,
		study_type=study_type,
	)

	if study_type == "clochat":
		conversation.related_persona = persona_num

	db.session.add(conversation)
	db.session.commit()
	



def register_survey_answer(db, SurveyAnswer, Participant, id_num, task_index, study_type, survey_type, survey_result):
	task_id = get_task_id(Participant, study_type, id_num, task_index)

	survey_answer = SurveyAnswer(
		task=task_id,
		task_index=task_index,
		participant=id_num,
		survey_type=survey_type,
		survey_result=survey_result,
		study_type=study_type,
	)

	db.session.add(survey_answer)
	db.session.commit()




def register_demographics(db, Participant, args):
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

def register_new_persona(db, Persona, id_num, persona_num):
	persona = Persona(
		participant=id_num, persona_num=persona_num, 
		input_dialogue="[{}, {}, {}, {} ,{}, {}]",
		is_category_finished = "[false, false, false, false, false, false]",
		img_urls = "[]",
	)
	db.session.add(persona)
	db.session.commit()

def register_persona_dialogue(db, Persona, id_num, persona_num, dialogue, is_category_finished):
	persona = Persona.query.filter_by(participant=id_num, persona_num=persona_num).first()
	persona.input_dialogue = dialogue
	persona.is_category_finished = is_category_finished
	db.session.commit()

def register_is_category_finished(db, Persona, id_num, persona_num, is_category_finished):
	persona = Persona.query.filter_by(participant=id_num, persona_num=persona_num).first()
	persona.is_category_finished = is_category_finished
	db.session.commit()

def register_persona_img(db, Persona, id_num, person_num, img_urls, img_url_index, prompt_kr, prompt_en):
	persona = Persona.query.filter_by(participant=id_num, persona_num=person_num).first()
	persona.img_urls = img_urls
	persona.img_url_index = img_url_index
	persona.kr_prompt = prompt_kr
	persona.en_prompt = prompt_en
	db.session.commit()