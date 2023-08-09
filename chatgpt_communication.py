import openai
import dalle_communication as dalle


## read txt file
with open("./key.txt", "r") as f:
	openai.api_key = f.read()


def get_new_answer_chatgpt(conversations):
	messages = []
	
	for conversation in conversations:
		if conversation.is_start or conversation.is_end:
			continue
		messages.append({"role": conversation.role, "content": conversation.content})
	response = openai.ChatCompletion.create(
		model="gpt-4",
		messages=messages
	)

	answer = response['choices'][0]['message']['content']
	return answer


def get_translation_dalle_prompt(prompt_kr):
	system_message = "You are a professional Korean-English Translator."
	user_message = f"""
		Translate the following korean message into English Dall-E prompt. \n
		---- \n
		'{prompt_kr}' \n
		----
		Please put the translated result within '<' and '>'
	"""
	
	messages = [
		{"role": "system", "content": system_message},
		{"role": "user", "content": user_message}
	]

	response = openai.ChatCompletion.create(
		model="gpt-4",
		messages=messages
	)

	answer = response['choices'][0]['message']['content']

	english_prompt = answer.split("<")[1].split(">")[0]

	return english_prompt


def convert_input_dialogue_to_persona_prompt(input_dialogue):
	# based on  https://github.com/f/awesome-chatgpt-prompts

	system_message = """
	 You are a professional JSON parser and persona creator. \n
	 I will provide you with a JSON string containing a information about a person. \n
	 The JSON string will consists of an array, and the information will be depicted in Korean. \n
	 Each element of the array repesents the cues on the following aspects of a persona: \n
	 1. Basic Demogrpahic Information (기본 정보)
	 2. Verbal, Conversation Styles (대화 스타일) 
	 3. Noverbal Styles / Emoticon (비언어적 스타일, 이모티콘 사용 여부)
	 4. Knowledge and Interest (지식과 관심사)
	 5. Verbal Relational Contents (기타 대화 관계적 내용)
	 6. Else (기타) \n
	 \n
	 Please write the ChatGPT system prompt that you think would make ChatGPT to act like the persona described in the JSON string. \n
	 Do not write explanations. \n
	 If the name and personal info of the persona is not specified, you can freely choose the name of it. \n
	 Please put the system prompt within '<' and '>'. 
	"""

	user_message = f"""
	The following is the JSON string containing the information about a person. \n
	---- \n
	'{input_dialogue}' 
	"""

	messages = [
		{ "role": "system", "content": system_message },
		{ "role": "user", "content": user_message}
	]

	response = openai.ChatCompletion.create(
		model="gpt-4",
		messages=messages
	)

	answer = response['choices'][0]['message']['content']

	persona_prompt = answer.split("<")[1].split(">")[0]

	return persona_prompt


def get_preview(persona_prompt, preview_prompt):
	messages = [
		{ "role": "system", "content": persona_prompt },
		{ "role": "user", "content": preview_prompt}
	]

	response = openai.ChatCompletion.create(
		model="gpt-4",
		messages=messages
	)

	answer = response['choices'][0]['message']['content']

	return answer
