import sys
import re
import os
import ast
from trainer import algness, load_counts
faces = ["U", "R", "F", "L", "B", "D"]

# rewrite alg by substituting ith move with wide move
subs = {"R": "l", "R'": "l'", "R2": "l2", "L": "r", "L'": "r'", "L2": "r2"}
# = {"r": {"R'": "M'"}, "l": {"L'": "M"}, "r'": {"R": "M'"}, "l'": {"L": "M'"}}
trans = {"R": [2,1,5,3,0,4], "R'": [4,1,0,3,5,2], "R2": [5,1,4,3,2,0], "L": [4,1,0,3,5,2], "L'": [2,1,5,3,0,4], "L2": [5,1,4,3,2,0] }
def substitute(alg, i):
    moves = alg.split(" ")
    old = moves[i]
    moves[i] = subs[moves[i]]
    for j in range(i+1, len(moves)):
        face = faces.index(moves[j][0])
        moves[j] = faces[trans[old][face]] + moves[j][1:]
#    if moves[i] in slices:
#        if i > 0 and moves[i-1] in slices[moves[i]]:
#            m = moves.pop(i-1)
#            moves[i-1] = slices[moves[i-1]][m]
#        elif i < len(moves)-1 and moves[i+1] in slices[moves[i]]:
#            m = moves.pop(i+1)
#            moves[i] = slices[moves[i]][m]
    return " ".join(moves)

# collect all possible rewrites of L, R moves from the ith move onwards
def rewrites(alg, i):
    algs = []
    moves = alg.split(" ")
    lr = re.compile("L|R")
    for j in range(i, len(moves)):
        if lr.match(moves[j][0]):
            substituted = substitute(alg, j)
            if j == len(moves)-1 or lr.search(" ".join(moves[j+1:])) is None:
                algs += [alg, substituted]
            else:
                algs += rewrites(alg, j+1)
                algs += rewrites(substituted, j+1)
            break
    return algs
 
# collect list of raw algorithms
fname = sys.argv[1]
alg_re = re.compile("([URFLDBMES][2']? )+")
raw = [line[0:alg_re.match(line).span()[1]].strip() for line in open(fname) if alg_re.match(line)]

# collect list of rewritten algorithms with substitutions r = L x, l = R x'
algs = []
for alg in raw:
    algs += rewrites(alg, 0)

# for each algorithm, compute effort
ranks = []
counts = load_counts("trained.txt")
for alg in algs:
    if "B" not in alg:
        ranks.append([alg, algness(alg, counts)])

# sort and print algorithms in ascending order of effort
sorted_algs = sorted(ranks, key=lambda x: x[1])
for i in range(len(sorted_algs)):
    print(str(sorted_algs[i][1]) + "\t\t" + sorted_algs[i][0])
