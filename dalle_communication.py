import openai

with open("./key.txt", "r") as f:
	openai.api_key = f.read()


def get_new_images(prompt):
	response = openai.Image.create(
		prompt=prompt,
		n=4,
		size="512x512"
	)
	data = response['data']
	urls = []
	for i in range(4):
		urls.append(data[i]['url'])
	return urls