from openai import OpenAI
import time

def ask_GPT(system,content): # GPT-4o
    # start_time = time.time()
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
    end_time = time.time()
    # print(completion.choices[0].message.content)
    # print(f"Time for GPT:{end_time-start_time:.2f}s")
    return completion.choices[0].message.content

# def ask_GPT(system,content): # Deepseek
#     start_time = time.time()
#     client = OpenAI(api_key="sk-122b9c8681964b78883c3c45c9629865", base_url="https://api.deepseek.com")
#     response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=[
#             {"role": "system", "content": system},
#             {"role": "user", "content": content},
#         ],
#         stream=False
#     )
#     end_time = time.time()
#     print(f"Time for DeepSeek:{end_time-start_time:.2f}s")
#     return response.choices[0].message.content


if __name__ == '__main__':
    system = "You are a robot"
    content = "Beijing"
    print(ask_GPT(system,content))