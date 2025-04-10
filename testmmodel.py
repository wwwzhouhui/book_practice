from openai import OpenAI

client = OpenAI(
	base_url="https://ai.gitee.com/v1",
	api_key="CSW0YJEY0AJVXWFSOA6CKRI6H06UAJUYK7IS1LBZ",
)

response = client.chat.completions.create(
	model="Qwen2.5-VL-32B-Instruct",
	stream=True,
	max_tokens=1024,
	temperature=0.2,
	top_p=1,
	extra_body={
		"top_k": -1,
	},
	frequency_penalty=1.2,
	messages=[
		{
			"role": "user",
			"content": [
				{
					"type": "text",
					"text": "Please describe this image"
				},
				{
					"type": "image_url",
					"image_url": {
						"url": "https://mypicture-1258720957.cos.ap-nanjing.myqcloud.com/image-20241226112202015.png"
					}
				}
			]
		}
	],
)

# 遍历流式响应并打印结果
for chunk in response:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")