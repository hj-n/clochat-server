
import json
from copy import deepcopy

def retreive_current_task_trial_indices(Conversations, id_num, study_type):
	conversations = Conversations.query.filter_by(participant=id_num, study_type=study_type).all()
	task_indices = [c.task_index for c in conversations]
	task_indices = list(set(task_indices))
	task_indices.sort()
	trial_indices = []

	for index in range(max(task_indices) + 1):
		if index in task_indices:
			trial_indices_for_task = [c.trial_index for c in conversations if c.task_index == index]
			trial_indices_for_task.sort()
			trial_indices_for_task = list(set(trial_indices_for_task))
			trial_indices.append(trial_indices_for_task)
		else:
			trial_indices.append([])
	return task_indices, trial_indices

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

def retreive_conversations(Conversations, id_num, task_index, trial_index, study_type):
	conversations = Conversations.query.filter_by(participant=id_num, task_index=task_index, trial_index=trial_index, study_type=study_type).all()
	return conversations

def retreive_persona_dialogue(Persona, id_num, persona_num):
	persona = Persona.query.filter_by(participant=id_num, persona_num=persona_num).first()

	return {
		"dialogue": json.loads(persona.input_dialogue),
		"is_category_finished": json.loads(persona.is_category_finished)
	}