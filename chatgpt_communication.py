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
