def obs_query_prompt(observation,target_obj,question):

    prompt="""
### Task Instruction ###
I have now asked a question regarding the target item, and I need you to provide a brief answer based on the your observed. Please provide a definite answer, such as 'yes' or 'no,' 'is' or 'is not.' Do not give ambiguous answers like 'not mentioned in the observation,' 'cannot be determined,' etc.

### Target Object ###
"""+target_obj+"""

### Question ###
"""+question+"""

### Your Observation ###
"""+observation+"""

### Examples ###

Example 1:
There are tomato_1, egg_81, and onion_9 in the fridge_87. And the kitchen_cabinet_12 is close to the fridge_87.

Example 2:
No book inside the drawer_3. But there is a novel close to the drawer_3.

### Output Format ###
Please respond briefly in the third person. Your response must explicitly mention the target item.
"""

    return prompt