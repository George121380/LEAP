from openai import OpenAI

def ask_GPT(system,content):
    with open("api_key.txt","r") as f:
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

def get_goal_inter_prompt(goal,item_list=None):
    items=""
    for item in item_list:
        items+="- "+item+"\n"
    prompt="""
The goal is: """+goal+""".
# Task Instructions:
Please analyze the provided goal and convert it into a discription like the Example. Your output should includes: defining a goal function, designing a behavior, where the goal in the behavior is the goal function. In the body section, write out the required states or relationships. The keyword "promotable" in the body section indicates that the involved "achieve" statements can be executed in any order.  Finally, output a standalone goal that only includes the goal function.

#The available states are:
- is_on(x: item)
- is_off(x: item)
- plugged(x: item)
- unplugged(x: item)
- open(x: item)
- closed(x: item)
- dirty(x: item)
- clean(x: item)
- sitting(x: character)
- lying(x: character)

#The available relationships are:
- on(x: item, y: item)
- inside(x: item, y: item)
- between(x: item, y: item, z: item)
- close_item(x: item, y: item)
- close(x: character, y: item)
- facing(x: item, y: item)
- holds_rh(x: character, y: item)
- holds_lh(x: character, y: item)

#We have those items in the scene:
"""+items+"""

#Example:
When the goal is: I find the groceries and carry them into the kitchen. I place them on the counter and begin to sort them out. I place the vegetables, eggs, cheese, and milk in the fridge.

The output is like: 
######example start#####
def all_foods_in_basket_in_fridge(basket: item):
  return inside[vegetables, fridge] and inside[eggs, fridge] and inside[cheese, fridge] and inside[milk, fridge] and closed[fridge]

behavior put_foods_in_fridge(basket: item):
  goal:
    all_foods_in_basket_in_fridge(basket)
  body:
    promotable:
      achieve inside(vegetables, basket)
      achieve inside(eggs, basket)
      achieve inside(cheese, basket)
      achieve inside(milk, basket)
    achieve closed(fridge)

goal:
  all_foods_in_basket_in_fridge(basket)
######example end#####  

#Output Format:
You can only output the discription of the converted goal. Don't make any explaination."######example start#####" and "######example end#####" are not included in the output.

    """
    return prompt

if __name__ == '__main__':
    system = "I have a goal described in natural language, and I need it converted into a structured format."
    goal="put the apple on the light"
    item_list=["dining_room","broom","floor","dustpan","dirt","trashcan","apple","light"]
    content = get_goal_inter_prompt(goal,item_list)
    print('=' * 80)
    print(f"When Goal instruction is: {goal}")
    print('=' * 80)
    print("The Goal interpretation is:\n")
    ask_GPT(system,content)
    print('=' * 80)
