from openai import OpenAI


def ask_GPT(system,content):
    with open("/Users/liupeiqi/workshop/Research/api_key.txt","r") as f:
        api_key = f.read().strip()
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content":content}
        ]
    )
    # print(completion.choices[0].message.content)
    return completion.choices[0].message.content