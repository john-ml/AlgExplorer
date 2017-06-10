import re

# helper for inverse() and removenegatives()
def islist(x):
    return type(x) == type([0]) # bite me

movetypes = "URFLBDurflbdMESmesxyz"
modifiers = ["", "2", "'"]
# moves represented by ints [0, 3m) where m = len(movetypes)
# [0, m)    cw quarter turns
# [m, 2m)   half quarter turns
# [2m, 3m)  ccw turns
def movetostr(m):
    lm = len(movetypes)
    return movetypes[m % lm] + modifiers[m // lm]

def strtomove(m):
    return movetypes.index(m[0]) + modifiers.index(m[1:]) * len(movetypes)

# split (RU'23R'U')2 -> ( R U ' 23 R ' U ' ) 2
def tokenize(alg):
    r = "([0-9]+|'| |\(|\)|[" + movetypes + "])"
    return [l for l in re.split(r, alg) if l.strip() != ""]

# transform [[movetype, quarter turns]] -> [[movetype, -quarter turns]]
# transform [[move tree, quarter turns]] -> [[inverted tree, quarter turns]]
def inverse(tree):
    result = []
    for i in range(len(tree)-1, -1, -1):
        m = tree[i]
        if islist(m[0]):
            result.append([inverse(m[0]), m[1]])
        else:
            result.append([m[0], -m[1]])
    return result

# force [[move tree, q]] where all q > 0
def removenegatives(tree):
    for i in range(len(tree)):
        if tree[i][1] < 0:
            tree[i] = inverse([tree[i]])[0]
            tree[i][1] *= -1
            if not islist(tree[i][0]):
                tree[i][1] %= 4
        if islist(tree[i][0]): # is a list
            removenegatives(tree[i][0])

# transform [[[a, b], c]] -> [[[a, b]]*c]
def flattened(tree):
    result = []
    for i in range(len(tree)):
        if islist(tree[i][0]): # append copies of recursively expanded sublist
            result += flattened(tree[i][0]) * tree[i][1]
        else:
            result.append([tree[i][0], tree[i][1] % 4])
    return result
    
# transform ( R U ' 23 R ' U ' ) 2 -> [[movetype, quarter turns]]
def transform(tokens):
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

# transform [[R, 1], [R, 1]] -> [[R, 2]]
# TODO: R L R' = L? R L r' = M L?
def compressed(movelist):
    result = []
    for m in movelist:
        if len(result) > 0 and result[-1][0] == m[0]:
            result[-1][1] = (result[-1][1] + m[1]) % 4
        else:
            result.append([m[0], m[1]])
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

# transform "(R U R')2" -> [1, m, 2m+1] where m = len(movetypes)
def parse(alg):
    moves = compressed(transform(tokenize(alg)))
    return [m[0] + len(movetypes)*(m[1] - 1) for m in moves]

def movecount(moves):
    return len(moves)

def algmovecount(moves):
    return len(moves)

def tostr(moves):
    return " ".join([movetostr(m) for m in moves])

# rewrite alg by substituting ith move with wide move
subs = {"R": "l", "R'": "l'", "R2": "l2", "L": "r", "L'": "r'", "L2": "r2"}
for k in subs:
    if type(k) == type("0"):
        subs[strtomove(k)] = strtomove(subs[k])
        del subs[k]
trans = {"R": [2,1,5,3,0,4,2,1,5,3,0,4], "R'": [4,1,0,3,5,2,4,1,0,3,5,2], "R2": [5,1,4,3,2,0,5,1,4,3,2,0] }
trans["L"], trans["L'"], trans["L2"] = trans["R'"], trans["R"], trans["R2"]
for k in trans:
    if type(k) == type("0"):
        trans[strtomove(k)] = trans[k]
        del trans[k]
def rewriteone(m, i):
    l = []
    for j in range(i):
        l.append(m[j])
    old = m[i]
    l.append(subs[m[i]])
    for j in range(i+1, len(m)):
        face = m[j] % len(movetypes)
        l.append(trans[old][face] + m[j]//len(movetypes) * len(movetypes))
    return l

# collect all possible rewrites of L, R moves from ith move onwards, given last occurrence
def rewritemany(m, i, last):
    algs = []
    for j in range(i, last+1):
        if m[j] % len(movetypes) == strtomove("L") or m[j] % len(movetypes) == strtomove("R"):
            new = rewriteone(m, j)
            if j == last:
                algs += [m, new]
            else:
                algs += rewritemany(m, j+1, last)
                algs += rewritemany(new, j+1, last)
            break
    return algs

# collect all possible rewrites of L, R moves from ith move onwards
def rewrite(m, i):
    last = max([-1] + [len(m) - 1 - [letter % len(movetypes) for letter in m[::-1]].index(move) for move in [strtomove("R"), strtomove("L")] if move in m])
    return rewritemany(m, i, last)
