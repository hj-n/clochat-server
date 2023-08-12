import openai
import requests
import numpy as np

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

	## download images
	new_urls = []
	for url in urls:
		img_data = requests.get(url).content
		seed_num = np.random.randint(100000000000)
		with open(f'./static/img/{seed_num}.jpg', 'wb') as handler:
			handler.write(img_data)
		
		new_urls.append(f'/static/img/{seed_num}.jpg')


	return new_urls
