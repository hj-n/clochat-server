import json
import random

TASK_PATH = "./assets/task_crafted.json"

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
	
	participant = Participant.query.filter_by(id_num=id_num).first()
	participant.clochat_list = json.dumps(clochat_list)
	participant.chatgpt_list = json.dumps(chatgpt_list)

	db.session.commit()


def register_conversation_start(db, Conversation, Participant, id_num, task_index, study):
	participant = Participant.query.filter_by(id_num=id_num).first()
	if study == "chatgpt":
		task_list = json.loads(participant.chatgpt_list)
	elif study == "clochat":
		task_list = json.loads(participant.clochat_list)
	
	task_id = task_list[task_index]

	conversation = Conversation(task=task_id, participant=id_num, is_start=True, is_end=False, conversation="", speaker="")
	db.session.add(conversation)
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
