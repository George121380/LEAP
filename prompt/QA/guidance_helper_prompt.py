def Guidance_helper_prompt(task,knowledge):

    kl=''
    for k in knowledge:
        kl+=f'- {k}: {knowledge[k]}\n'
    prompt="""
### Task Instruction ###
You have a household robot that is completing a task but encounters some difficulties and seeks your help. However, you are a responder with limited knowledge and can only provide specific information. If the robot's question goes beyond that specific information, you must reply with "I don't know."

### Robot's Question ###
"""+task+"""

### Info you can provide ###
"""+kl+"""

### Output Format ###
You must answer carefully. If the robot's question is not related to the info you can provide, you must say "I don't know." If the robot's question is relevant to the information you can provide, for example, if similar keywords and relevant content appear, answer using simple, clear natural language, as if you are teaching a child, with one short sentence. Please do not output in a numbered list; you should organize the content into a complete sentence.
"""

    return prompt