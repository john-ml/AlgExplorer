import re

def tokenize(alg):
    return alg.split(" ")

# rewrite alg by substituting ith move with wide move
faces = ["U", "R", "F", "L", "B", "D"]
def rewriteone(alg, i):
    subs = {"R": "l", "R'": "l'", "R2": "l2", "L": "r", "L'": "r'", "L2": "r2"}
    trans = {"R": [2,1,5,3,0,4], "R'": [4,1,0,3,5,2], "R2": [5,1,4,3,2,0] }
    trans["L"], trans["L'"], trans["L2"] = trans["R'"], trans["R"], trans["R2"]
    moves = tokenize(alg)
    old = moves[i]
    moves[i] = subs[moves[i]]
    for j in range(i+1, len(moves)):
        face = faces.index(moves[j][0])
        moves[j] = faces[trans[old][face]] + moves[j][1:]
    return " ".join(moves)

# collect all possible rewrites of L, R moves from the ith move onwards
def rewrite(alg, i):
    algs = []
    moves = tokenize(alg)
    lr = re.compile("L|R")
    for j in range(i, len(moves)):
        if lr.match(moves[j][0]):
            new = rewriteone(alg, j)
            if j == len(moves)-1 or lr.search(" ".join(moves[j+1:])) is None:
                algs += [alg, new]
            else:
                algs += rewrite(alg, j+1)
                algs += rewrite(new, j+1)
            break
    return algs

def movecount(alg):
    return len(alg.split(" "))
def algmovecount(alg):
    pass