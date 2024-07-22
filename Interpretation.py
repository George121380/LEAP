from openai import OpenAI

from prompt.goal_interpretation_prompt import get_goal_inter_prompt

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
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content



def goal_interpretation(goal,additional_information,item_list=None):
    if ":item" in item_list[0]:
        for item in item_list:
            item=item.replace(":item",'')
    system = "I have a goal described in natural language, and I need it converted into a structured format."
    content = get_goal_inter_prompt(goal,item_list,additional_information)

    print('=' * 80)
    print(f"When Goal instruction is: {goal}")
    converted_content=ask_GPT(system,content)
    print('=' * 80)
    print("The Goal interpretation is:\n")
    print('=' * 80)

    return converted_content