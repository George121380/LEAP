from openai import OpenAI
import time

LLM_MODEL = "gpt-4o"
# LLM_MODEL = "deepseek"

def ask_GPT(system,content):
    while True:
        try:
            if LLM_MODEL == "gpt-4o": # GPT-4o api
                # with open("/Users/liupeiqi/workshop/Research/api_key.txt","r") as f:
                #     api_key = f.read().strip()
                client = OpenAI(api_key="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")
                completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content":content}
                    ]
                )
            elif LLM_MODEL == "deepseek": # Deepseek api
                client = OpenAI(api_key="sk-7eb58550af8a4042aca7d33d495ec2e0", base_url="https://api.deepseek.com")
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
            
        except Exception as e:
            print(e)
            time.sleep(1)
            continue

if __name__ == '__main__':
    system = """
    Please answer the question based on the scenario.
    Scenario:
    Peppa Pig has a golden egg that she loves very much, and she keeps it at home in her collection. One day, Peppa invited her two new friends (they just know each other), Shaun the Sheep and Winnie the Pooh, over to her house to study together. At some point, Peppa had to leave the house for a while. Shaun the Sheep, being mischievous, found a brand new hammer that had never been used before. He used the hammer to smash Peppa’s golden egg but, fearing Peppa's anger when she returned, he handed the hammer to Winnie the Pooh. Shaun then began to work on his homework, while Winnie, curious about the hammer, started playing with it. Throughout the entire process, Peppa didn’t witness any of this. A little while later, Peppa returned home, only to find her golden egg broken, Shaun doing his homework, and Winnie playing with the hammer."""
    Q1 = "After Peppa Pig returns, what would she feel?"
    Q2 = "After Peppa Pig returns, who will she think broke the golden egg, and why."
    Q3 = "If you were Daddy Pig and witnessed the whole process at home, and then saw Peppa get very angry after returning, what would you say to her"
    print(ask_GPT(system,Q1))
    print('#'*10)
    print(ask_GPT(system,Q2))
    print('#'*10)
    print(ask_GPT(system,Q3))