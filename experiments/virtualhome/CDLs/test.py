# behavior put(inhand_obj: item, obj: item):
#   body:
#     assert not is_room(obj)
#     #assert not pourable(inhand_obj) or not recipient(obj)
#     achieve not unknown(obj)
#     achieve not unknown(inhand_obj)
#     achieve_once inhand(inhand_obj)
#     achieve_once close_char(char, obj)
#     put_executor(inhand_obj, obj)

#   eff:
#     holds_rh[char, inhand_obj] = False
#     holds_lh[char, inhand_obj] = False
#     inhand[inhand_obj] = False
#     on[inhand_obj, obj] = True
#     close[inhand_obj, obj] = True
#     close[obj, inhand_obj] = True
#     foreach inter in (findall x: item: close(x, obj) and not unknown(x)):
#       close[inter, inhand_obj] = True
#       close[inhand_obj, inter] = True
#     has_a_free_hand[char] = True



states = []
properties = []
all_item_list = []

def call_primitive_controller(primitive_name, *args):
    pass # api to virtualhome controllers

def grab_function(item):
    if states['in_hand'][item.id]:
        pass # ...
    else:
        pass # ...

def getclose_function(location):
    pass

def find_function(item):
    if states['unknown'][item.id]:
        pass # run a LLM based exploration algorithm like our method
        return True # We can assume that the item will be find eventually, because the 'human' could help LLM to find it
    else:
        return True

def put_function(item, surface):
    find_function(item)
    find_function(surface)
    grab_function(item) # assume we have this (we can write this by python, just temporarily omitted)
    call_primitive_controller('put', item, surface)

    # Just like eff, we can set states change here
    states['in_hand'][item.id] = False
    #......

def empty_a_hand():
    if states['has_a_free_hand']['char']:
        return
    else:
        surface=None
        for item in all_item_list:
            if properties['surface'][item.id] and not states['unknown'][item.id]:
                surface=item
                break

        inhand_item=None
        for item in all_item_list:
            if states['in_hand'][item.id]:
                inhand_item=item
                break

        put_function(inhand_item, surface)


def py_bind(req):
    condition=parse_req(req) # parse all requirements
    for item in all_item_list:
        if condition:
            return item