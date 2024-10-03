from openai import OpenAI
import time

LLM_MODEL = "gpt-4o"
# LLM_MODEL = "deepseek"

def ask_GPT(system,content):
    if LLM_MODEL == "gpt-4o": # GPT-4o api
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
    elif LLM_MODEL == "deepseek": # Deepseek api
        client = OpenAI(api_key="sk-122b9c8681964b78883c3c45c9629865", base_url="https://api.deepseek.com")
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": content},
            ],
            stream=False
        )
    else:
        raise ValueError("Invalid LLM_MODEL")
    return completion.choices[0].message.content

if __name__ == '__main__':
    system = "You are a robot"
    content = "Beijing"
    print(ask_GPT(system,content))