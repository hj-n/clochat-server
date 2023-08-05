import openai


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
	print(answer)
	return answer

	