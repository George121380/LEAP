def split_definitions_and_behaviors(code_block: str) -> dict:
    """
    This function splits a block of code into individual function definitions and behaviors 
    based on 'def' and 'behavior' keywords.
    """
    definitions = []
    behaviors = []
    current_block = []
    current_type = None

    for line in code_block.splitlines():
        stripped_line = line.strip()

        # Detect the start of a new function definition
        if stripped_line.startswith("def"):
            if current_block:
                if current_type == "def":
                    definitions.append("\n".join(current_block))
                elif current_type == "behavior":
                    behaviors.append("\n".join(current_block))
            current_block = [line]
            current_type = "def"
        # Detect the start of a new behavior definition
        elif stripped_line.startswith("behavior"):
            if current_block:
                if current_type == "def":
                    definitions.append("\n".join(current_block))
                elif current_type == "behavior":
                    behaviors.append("\n".join(current_block))
            current_block = [line]
            current_type = "behavior"
        else:
            current_block.append(line)

    # Add the last block of code
    if current_block:
        if current_type == "def":
            definitions.append("\n".join(current_block))
        elif current_type == "behavior":
            behaviors.append("\n".join(current_block))

    return {"functions": definitions, "behaviors": behaviors}


# Example usage
code_block = '''
def is_window_unvisited_and_not_known(window: item):
    # Function to check if a window is unvisited and not already known
    symbol is_unvisited_and_not_known=not visited(window) and window=window_63 and window=window_86 
and window=window_348
    return is_unvisited_and_not_known

behavior identify_window(window:item):
    body:
        if not visited(window):
            observe(window, ""Check if it is a window"")

behavior explore_room(room:item):
    body:
        foreach window: item:
            if is_window(window) and inside(window, room) and is_window_unvisited_and_not_known(wind
ow):
                identify_window(window)

behavior explore_house():
    body:
        foreach room: item:
            if is_room(room):
                explore_room(room)

behavior __goal__():
    body:
        explore_house()
'''

# Split the code block
result = split_definitions_and_behaviors(code_block)

# Print functions
print("Functions:\n")
for function in result['functions']:
    print(function)
    print("\n" + "-"*50 + "\n")

# Print behaviors
print("Behaviors:\n")
for behavior in result['behaviors']:
    print(behavior)
    print("\n" + "-"*50 + "\n")
