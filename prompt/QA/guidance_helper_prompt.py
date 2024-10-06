def Guidance_helper_prompt(task,knowledge):

    kl=''
    for k in knowledge:
        kl+=f'- {k}:\n {knowledge[k]}\n'
    prompt="""
### Task Instruction ###
A household robot is trying to complete a task but encounters some difficulties and asks for your assistance. You can only provide specific information. If the robot's question is outside the scope of this information, respond with "I don't know."

### Robot's Question ###
"""+task+"""

### Info you can provide ###
"""+kl+"""

### Output Format ###
Answer precisely. If the robot's question does not match the available information, simply reply, "I don't know." If the question is relevant, respond with a concise and clear explanation, as if teaching a child, using one short sentence. Organize your response naturally without using a numbered list, and avoid changing verbs or the sequence of the original content.
"""

    return prompt