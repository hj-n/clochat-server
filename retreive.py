
import json
from chatgpt_communication import convert_input_dialogue_to_persona_prompt, get_preview

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

def retreive_persona_info(Persona, id_num, persona_num):
	persona = Persona.query.filter_by(participant=id_num, persona_num=persona_num).first()

	return ({
		"promptKr": persona.kr_prompt,
		"promptEn": persona.en_prompt,
		"imgUrls":  json.loads(persona.img_urls),
		"imgUrlIndex":  persona.img_url_index,
		"inputDialogue": json.loads(persona.input_dialogue),
	})

def retreive_persona_preview(Persona, id_num, persona_num, preview_prompt):
	persona = Persona.query.filter_by(participant=id_num, persona_num=persona_num).first()
	input_dialogue_str = persona.input_dialogue

	persona_prompt = convert_input_dialogue_to_persona_prompt(input_dialogue_str)
	print(persona_prompt)
	answer = get_preview(persona_prompt, preview_prompt)

	return answer

def retreive_persona_info_list(Persona, id_num):
	personas = Persona.query.filter_by(participant=id_num).all()
	persona_info_list = []
	for persona in personas:
		persona_info_list.append({
			"imageDialogue": json.loads(persona.input_dialogue),
			"imgUrls":  json.loads(persona.img_urls),
			"imgUrlIndex":  persona.img_url_index,
			"personaNum": persona.persona_num,
			"promptKr": persona.kr_prompt,
			"promptEn": persona.en_prompt,
		})
	return persona_info_list

def retreive_next_persona_num(Persona, id_num):
	personas = Persona.query.filter_by(participant=id_num).all()
	persona_nums = [p.persona_num for p in personas]
	if len(persona_nums) == 0:
		return 0
	else:
		return max(persona_nums) + 1
	
def retreive_next_trial_index(Conversations, id_num, task_index, study_type):
	conversations = Conversations.query.filter_by(participant=id_num, task_index=task_index, study_type=study_type).all()
	trial_indices = [c.trial_index for c in conversations]
	if len(trial_indices) == 0:
		return 0
	else:
		return max(trial_indices) + 1
	

def retreive_survey_result(SurveyAnswer, id_num):
	survey_answers = SurveyAnswer.query.filter_by(participant=id_num).all()

	survey_answer_list = []
	for survey_answer in survey_answers:
		survey_answer_list.append({
			"taskIndex": survey_answer.task_index,
			"studyType": survey_answer.study_type,
			"surveyType": survey_answer.survey_type,
			"surveyResult": json.loads(survey_answer.survey_result)
		})

	return survey_answer_list