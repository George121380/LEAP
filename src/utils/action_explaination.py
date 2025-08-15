import re

def controller_to_natural_language(controller_call):
    # Use regular expression to parse controller name and parameters
    match = re.match(r'(\w+)\(([^)]+)\)', controller_call)
    
    if match:
        controller = match.group(1)
        params = [param.strip() for param in match.group(2).split(',')]
        
        # Generate appropriate sentence based on parameter count
        if len(params) == 1:
            x = params[0]
            if controller == 'walk_executor':
                return f"Walk to {x}."
            elif controller == 'switchoff_executor':
                return f"Switch off {x}."
            elif controller == 'switchon_executor':
                return f"Switch on {x}."
            elif controller == 'grab_executor':
                return f"Grab {x}."
            elif controller == 'standup_executor':
                return f"{x} stand up."
            elif controller == 'wash_executor':
                return f"Wash {x}."
            elif controller == 'scrub_executor':
                return f"Scrub {x}."
            elif controller == 'rinse_executor':
                return f"Rinse {x}."
            elif controller == 'sit_executor':
                return f"Sit on {x}."
            elif controller == 'lie_executor':
                return f"Lie on {x}."
            elif controller == 'open_executor':
                return f"Open {x}."
            elif controller == 'close_executor':
                return f"Close {x}."
            elif controller == 'plugin_executor':
                return f"Plug in {x}."
            elif controller == 'plugout_executor':
                return f"Plug out {x}."
            elif controller == 'find_executor':
                return f"Find {x}."
            elif controller == 'turnto_executor':
                return f"Turn to {x}."
            elif controller == 'cut_executor':
                return f"Cut {x}."
            elif controller == 'eat_executor':
                return f"Eat {x}."
            elif controller == 'sleep_executor':
                return f"Make {x} sleep."
            elif controller == 'greet_executor':
                return f"Greet {x}."
            elif controller == 'drink_executor':
                return f"Drink {x}."
            elif controller == 'lookat_executor':
                return f"Look at {x}."
            elif controller == 'wipe_executor':
                return f"Wipe {x}."
            elif controller == 'puton_executor':
                return f"Put {x} on."
            elif controller == 'putoff_executor':
                return f"Take {x} off."
            elif controller == 'read_executor':
                return f"Read {x}."
            elif controller == 'touch_executor':
                return f"Touch {x}."
            elif controller == 'type_executor':
                return f"Type on {x}."
            elif controller == 'watch_executor':
                return f"Watch {x}."
            elif controller == 'move_executor':
                return f"Move {x}."
            elif controller == 'push_executor':
                return f"Push {x}."
            elif controller == 'pull_executor':
                return f"Pull {x}."
            else:
                return "Unknown controller"
        
        elif len(params) == 2:
            x, y = params
            if controller == 'put_executor':
                return f"Put {x} on {y}."
            elif controller == 'putin_executor':
                return f"Put {x} into {y}."
            elif controller == 'pour_executor':
                return f"Pour {x} into {y}."
            elif controller == 'exp':
                return f"look for {x} around {y}."
            elif controller == 'obs':
                return f"Observe around {x} with the question of {y}."
            else:
                return "Unknown controller"
        else:
            return "Invalid parameter input."
    else:
        return "Invalid controller format."
