import re

# helper for inverse() and removenegatives()
def islist(x):
    return type(x) == type([0]) # bite me

movetypes = "URFLBDurflbdMESmesxyz"
modifiers = ["", "2", "'"]
def movetostr(m):
    """Moves are represented by ints [0, 3m) where m = len(movetypes).

    [0, m)    cw quarter turns
    [m, 2m)   half quarter turns
    [2m, 3m)  ccw turns
    """
    lm = len(movetypes)
    return movetypes[m % lm] + modifiers[m // lm]

def strtomove(m):
    return movetypes.index(m[0]) + modifiers.index(m[1:]) * len(movetypes)

def tokenize(alg):
    "Split (RU'23R'U')2 -> ( R U ' 23 R ' U ' ) 2"
    r = "([0-9]+|'| |\(|\)|[" + movetypes + "])"
    return [l for l in re.split(r, alg) if l.strip() != ""]

def inverse(tree):
    "transform [[movetype, quarter turns]] -> [[movetype, -quarter turns]]"
    "transform [[move tree, quarter turns]] -> [[inverted tree, quarter turns]]"
    result = []
    for i in range(len(tree)-1, -1, -1):
        m = tree[i]
        if islist(m[0]):
            result.append([inverse(m[0]), m[1]])
        else:
            result.append([m[0], -m[1]])
    return result

def removenegatives(tree):
    "force [[move tree, q]] where all q > 0"
    for i in range(len(tree)):
        if tree[i][1] < 0:
            tree[i] = inverse([tree[i]])[0]
            tree[i][1] *= -1
            if not islist(tree[i][0]):
                tree[i][1] %= 4
        if islist(tree[i][0]): # is a list
            removenegatives(tree[i][0])

def flattened(tree):
    "transform [[[a, b], c]] -> [[[a, b]]*c]"
    result = []
    for i in range(len(tree)):
        if islist(tree[i][0]): # append copies of recursively expanded sublist
            result += flattened(tree[i][0]) * tree[i][1]
        else:
            result.append([tree[i][0], tree[i][1] % 4])
    return result
    
def transform(tokens):
    "transform ( R U ' 23 R ' U ' ) 2 -> [[movetype, quarter turns]]"
    tree = []
    lparens = []
    # build tree of moves
    for i in range(len(tokens)):
        t = tokens[i]
        if t == "(" or t == ")" or t in movetypes: # pop unnecessary )
            if len(tree) > 0 and tree[-1] == ")":
                tree.pop()
                lparens.pop()
        if t == "(": # push (
            lparens.append(len(tree))
        elif t == ")": # push )
            if i != len(tokens)-1:
                tree.append(t)
        elif t in movetypes: # push new move
            m = movetypes.index(t)
            tree.append([m, 1])
        elif t == "w": # wide moves
            if len(tree) > 0:
                tree[-1][0] += 6
        else: # apply modifier
            n = int(t.replace("'", "-1"))
            if len(tree) > 0:
                if tree[-1] == ")": # if modifying sequence, create new subtree
                    tree.pop()
                    l = lparens.pop()
                    moves = tree[l:]
                    del tree[l:]
                    tree.append([moves, n])
                else: # if modifying single move, multiply qtm count
                    tree[-1][1] *= n
    removenegatives(tree)
    return flattened(tree)

def fasttransform(tokens):
    "transform R U ' R R -> [[movetype, quarter turns]], doesn't handle parentheses"
    result = []
    # build tree of moves
    for i in range(len(tokens)):
        t = tokens[i]
        if t in movetypes: # push new move
            m = movetypes.index(t)
            result.append([m, 1])
        elif t == "w": # wide moves
            if len(result) > 0:
                result[-1][0] += 6
        else: # apply modifier
            if len(result) > 0:
                result[-1][1] *= int(t.replace("'", "-1"))
    return result    

# TODO: R L R' = L? R L r' = M L?
def compressed(movelist):
    "transform [[R, 1], [R, 1]] -> [[R, 2]]"
    result = []
    for m in movelist:
        if len(result) > 0 and result[-1][0] == m[0]:
            result[-1][1] = (result[-1][1] + m[1]) % 4
        else:
            result.append([m[0], m[1] % 4])
    i = 0
    while i < len(result):
        if result[i][1] == 0:
            del result[i]
        else:
            i += 1
    if len(result) == len(movelist): # certainly incompressible
        return result
    else:
        return compressed(result)

def parse(alg):
    """transform "(R U R')2" -> [1, m, 2m+1] where m = len(movetypes)"""
    if "(" not in alg or ")" not in alg:
        moves = compressed(fasttransform(tokenize(alg)))
    else:
        moves = compressed(transform(tokenize(alg)))
    return [m[0] + len(movetypes)*(m[1] - 1) for m in moves]

def ltrim(m, types):
    "remove leading movetypes"
    result = []
    i = 0
    while i < len(m):
        if m[i] % len(movetypes) not in types:
            break
        i += 1
    return m[i:]

def rtrim(m, types):
    "remove trailing movetypes"
    return ltrim(m[::-1], types)[::-1]

def movecount(moves):
    return len(moves)

def algmovecount(moves):
    return len(moves)

def tostr(moves):
    return " ".join([movetostr(m) for m in moves])

trans = {}
t = {} # helper dict to populate trans{}
t["x"] = {"U": "B", "R": "R", "F": "U", "L": "L", "B": "D", "D": "F", "M": "M", "E": "S", "S": "E'", "x": "x", "y": "z'", "z": "y"}
t["y"] = {"U": "U", "R": "F", "F": "L", "L": "B", "B": "R", "D": "D", "M": "S'", "E": "E", "S": "M", "x": "z", "y": "y", "z": "x'"}
t["z"] = {"U": "R", "R": "D", "F": "F", "L": "U", "B": "B", "D": "L", "M": "E'", "E": "M", "S": "S", "x": "y'", "y": "x", "z": "z"}
#t["x"] = {"E": "S", "S": "E'"}
for rtype in t: # for each rotation type
    if type(rtype) == type("0"): # process string keys only
        for i in range(1, 4): # for each rotation
            r = parse(rtype + str(i))[0]
            trans[r] = {}
            for mtype in t[rtype]: # for each move type
                if type(mtype) == type("0"): # process string keys only
                    for j in range(1, 4): # for each move
                        m = parse(mtype + str(j))[0]
                        newm = mtype
                        mods = movetostr(m)[1:]
                        for k in range(i): # apply rotation, yielding move type + modifier string
                            mods += t[rtype][newm][1:]
                            newm = t[rtype][newm][0]
                        trans[r][m] = parse(newm + mods)[0] # add proper entry in trans{}{}
del t # delete helper dict

#for t in trans:
#	print(tostr([t]))
#	for m in trans[t]:
#		print(movetostr(m) + " " + movetostr(t) + " = " + movetostr(trans[t][m]))
def rewriteone(m, rule, i):
    "rewrite alg by substituting ith move according to rule = [replacement move sequence, rotation to be applied to following moves]"
    l = []
    for j in range(i):
        l.append(m[j])
    l += rule[0]
    for j in range(i+1, len(m)):
        l.append(trans[rule[1]][m[j]])
    return l

def rewritemany(m, rules, i, last):
    "collect all possible rewrites m from ith move onwards, given rules and last occurrence"
    algs = []
    for j in range(i, last+1): # !!length can change
        if m[j] in rules:
            new = rewriteone(m, rules[m[j]], j)
            if j == last:
                algs += [m, new]
            else:
                algs += rewritemany(m, rules, j+1, last)
                algs += rewritemany(new, rules, j+1, last)
            break
    if len(algs) == 0:
        return [m]
    else:
        return algs

def rewrite(m, rules):
    """Collect all possible rewrites of m.

    rules = {move: [[replacement sequence], rotation to be applied to following moves]}
    """
    last = max([-1] + [i for i in range(len(m)) if m[i] in rules])
    return rewritemany(m, rules, 0, last)
