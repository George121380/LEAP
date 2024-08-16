def choose_relative_items_prompt(goal,unknown=None,additional_information=None,goal_representation=None):
    if additional_information==None:
        additional_information="None"
    categories=""
    num=0
    for cat in unknown:
        categories+=str(num)+"."+cat.replace("is_","")+"\n"
        num+=1
    prompt="""
The goal is: """+goal+""".
The additional information is: """+additional_information+"""
My goal representation is: """+goal_representation +"""
The unknown categories are: """+categories+"""
## Task Instructions:
I have a goal that needs to be accomplished, and I have provided some additional information to support this goal. To achieve the goal, I have proposed a goal representation. By parsing this goal representation, I can obtain the sequence of actions needed to complete the goal. Currently, there are some objects in the environment whose locations are unknown to me. I need you to use common sense, based on my goal, to help me determine which of these objects might be relevant to my task, and then help me select these objects and return the corresponding object numbers.

## Output Format:
You only need to output a list of item numbers in the form of: [a,b,c,...]. Please do not provide any explanations or descriptions.

## Example:
when the goal is: Cut a tomato and put it in the bowl.
The additional information is: The tomato is in the fridge.
The goal representation is:
behavior find_tomato(fridge:item, tomat:item):
    body:
        achieve_once open(fridge)
        achieve inhand(tomato)
        achieve_once closed(fridge)

behavior cut_tomato(tomato:item):
    body:
        achieve cut(tomato)

behavior put_tomato_in_bowl(tomato:item, bowl:item):
    body:
        achieve inside(tomato, bowl)
    
behavior __goal__():
    body:
        bind tomato:item where:
            is_tomato(tomato)
        bind fridge:item where:
            is_fridge(fridge)
        bind bowl:item where:
            is_bowl(bowl)
        find_tomato(fridge, tomato)
        cut_tomato(tomato)
        put_tomato_in_bowl(tomato, bowl)
        
The unknown categories are:
0. bread
1. onion
2. bacon
3. faucet
4. chair
5. stove
6. knife
7. spatula
8. sugar
9. countertop
10. water
11. oil
12. salt
13. pepper
14. curtain
15. book
16. tomato
17. egg
18. pan
19. bowl

Your output should be: [6,16,19]

Example Analysis:
In the goal, additional information, and goal representation, the three items tomato, bowl, and fridge are mentioned. However, note that in the unknown categories, only tomato and bowl appear, which means fridge is a known item and therefore does not need to be selected. But pay special attention to the fact that the list of case outputs includes 6, which is a knife. Although this item is not explicitly mentioned in the goal, additional information, and goal representation, based on your common sense, you can infer that if you want to cut a tomato, you need a tool to cut the tomato, and a knife is a very likely tool. So, based on common sense, you also need to select this item. Additionally, please note that the output should only contain a list with numbers, and no extra information is needed. If you think no items need to be output, just output "None". But please boldly guess items that might be useful.
"""
    return prompt