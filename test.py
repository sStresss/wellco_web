p_str = 'hello my world'

def refactor(pp_str):
    arr = pp_str.split(' ')
    temp = ''
    for elem in reversed(arr):
        if len(temp) == 0:
            temp = elem
        else:
            temp = temp + ' ' + elem
    return temp


print(refactor(p_str))