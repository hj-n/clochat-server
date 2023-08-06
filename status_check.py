import json

def is_study_complete(Participants, id_num, study_type, task_index):
	participant = Participants.query.filter_by(id_num=id_num).first()
	if study_type == "chatgpt":
		task_list = json.loads(participant.chatgpt_list)
	elif study_type == "clochat":
		task_list = json.loads(participant.clochat_list)

	
	if int(task_index) + 1 == len(task_list):
		return True
	else:
		return False