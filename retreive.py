
import json

def retreive_current_task_indices(Conversations, id_num, study_type):
	conversations = Conversations.query.filter_by(participant=id_num, study_type=study_type).all()
	task_indices = [c.task_index for c in conversations]
	task_indices = list(set(task_indices))
	task_indices.sort()
	return task_indices

def retrieve_task_info(Participant, Task, id_num, task_index, study_type):
	participant = Participant.query.filter_by(id_num=id_num).first()
	if study_type == "chatgpt":
		task_list = json.loads(participant.chatgpt_list)
	elif study_type == "clochat":
		task_list = json.loads(participant.clochat_list)
	
	task_id = task_list[int(task_index)]
	task = Task.query.filter_by(task_id_num=task_id).first()
	task_info = {"title": task.title, "description": task.description}
	return task_info