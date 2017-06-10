import sys
import re
faces = ["U", "R", "F", "L", "B", "D"]

# rewrite alg by substituting ith move with wide move
substitutions = {"R": "l", "R'": "l'", "R2": "l2", "L": "r", "L'": "r'", "L2": "r2"}
translations = {"R": [2,1,5,3,0,4], "R'": [4,1,0,3,5,2], "R2": [5,1,4,3,2,0], "L": [4,1,0,3,5,2], "L'": [2,1,5,3,0,4], "L2": [5,1,4,3,2,0] }
def substitute(alg, i):
    moves = alg.split(" ")
    substituted = moves[i]
    moves[i] = substitutions[moves[i]]
    for j in range(i+1, len(moves)):
        moves[j] = faces[translations[substituted][faces.index(moves[j][0])]] + moves[j][1:]
    return " ".join(moves)

# collect all possible rewrites of L, R moves from the ith move onwards
def rewrites(alg, i):
    algs = []
    moves = alg.split(" ")
    lr = re.compile("L|R")
    for j in range(i, len(moves)):
        if moves[j][0] in ["L", "R"]:
            substituted = substitute(alg, j)
            if j == len(moves)-1 or lr.search(" ".join(moves[j+1:])) is None:
                algs += [alg, substituted]
            else:
                algs += rewrites(alg, j+1)
                algs += rewrites(substituted, j+1)
            break
    return algs


# evaluate ergonomics of alg (higher value -> worse)
# assumptions:
#   - two types of moves: "flicks" (U,F,B,D) and "turns" (R,L)
#     - turns modify wrist position
#     - ease of flicks determined by wrist position
#   - overall effort given by avg effort per move
#   - grip = (0, 1, 2, 3) mod 4 -> thumb on DR, FR, UR, BR
#   - initial LH = 0, RH grip = whatever minimizes effort
#   - 1 effort = 1 R2 turn (RH grip = -1)

# returns (effort, new lh, new rh) for move given lh, rh grips
flick_cost = 0.1
lr_cost = 0.1
halfturn_cost = 0.1
regrip_cost = 2
twist_cost = 0.5
def move(lh, rh, move):
    dlr = {"L'": (1, 0), "L": (-1, 0), "R'": (0, -1), "R": (0, 1)}
    if move.upper() in dlr:
        result = [lr_cost, lh + dlr[move.upper()][0], rh + dlr[move.upper()][1]]
    elif move[0].upper() == "L":
        if abs(lh+2) < abs(lh-2):
            new_lh = lh+2
        else:
            new_lh = lh-2
        result = [halfturn_cost, new_lh, rh]
    elif move[0].upper() == "R":
        if abs(rh+2) < abs(rh-2):
            new_rh = rh+2
        else:
            new_rh = rh-2
        result = [halfturn_cost, lh, new_rh]
    else:
        # flicks defined relative to lh
        flicks = ["F", "U", "B", "D"];
        flicks = flicks[lh:] + flicks[:lh];
        
        # regrips[][] defined relative to flick and offset between grips
        # gives "expected number of regrips"
        offset = ((rh - lh) + 4 * ((rh - lh) // 4 + 1)) % 4
        directions = {"": 1, "'": 0, "2": 2}
        regrips = [[[0.8, 1, 1], [0.5, 0.8, 0.9], [1, 1, 1], [0.5, 0.5, 0.5]], \
                   [[0, 0, 0.8], [0.1, 0, 0.8], [0.8, 0.8, 0.8], [0, 0.5, 0.8]], \
                   [[1, 1, 1], [0.8, 0.8, 0.8], [0.8, 1, 1], [1, 1, 1]], \
                   [[0.8, 0.8, 0.8], [0.8, 0.8, 0.8], [0.8, 0.8, 0.8], [0.8, 0.8, 0.8]]] # efforts[flick][offset][direction]
        new_offsets = [[[0, -1, -1], [1, 1, -1], [-1, -1, -1], [3, 3, 3]], \
                       [[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3]], \
                       [[1, 1, 1], [1, 1, 1], [1, 1, 1], [3, 3, 1]], \
                       [[0, 0, 0], [1, 1, 1], [2, 2, 2], [3, 3, 3]]] # new_offsets[flick][offset][direction]
        flick = flicks.index(move[0].upper())
        direction = directions[move[1:]]

        # reset RH grip
        # offset should always = flick-1 because U=1 when offset=0
        new_rh = new_offsets[flick][offset][direction] + lh
        new_rh = (new_rh + (new_rh // 4 + 1) * 4) % 4
        if new_rh == 3: # special case
            new_rh = -1
        if move[1:] == "2":
            flick_count = 2
        else:
            flick_count = 1
        if new_rh != rh:
            new_lh = 0
        else:
            new_lh = lh
        result = [flick_cost*flick_count + regrip_cost*regrips[flick][offset][direction], new_lh, new_rh]
        #print(flick, offset, direction, regrips[flick][offset][direction], flick_count, result)
    result[0] += twist_cost * (2*abs(result[1])**3 + abs(result[2])**2)
    return result[0], result[1], result[2]

# returns overall effort of alg
def effort(alg):
    lh, rh = [0, 0, 0, 0], [-1, 0, 1, 2]
    moves = alg.split(" ")
    total_effort = [0, 0, 0, 0]
    for i in range(len(moves)):
        for j in range(4):
            e, lh[j], rh[j] = move(lh[j], rh[j], moves[i])
            total_effort[j] += e
    return min(total_effort) / len(moves)
 
# collect list of raw algorithms
fname = sys.argv[1]
alg_re = re.compile("([URFLDBMES][2']? )+")
raw = [line[0:alg_re.match(line).span()[1]].strip() for line in open(fname) if alg_re.match(line)]

# collect list of rewritten algorithms with substitutions r = L x, l = R x'
algs = []
for alg in raw:
    algs += rewrites(alg, 0)

# for each algorithm, compute effort
efforts = []
for alg in algs:
    efforts.append([alg, effort(alg)])

# sort and print algorithms in ascending order of effort
sorted_algs = sorted(efforts, key=lambda x: x[1])
for i in range(len(sorted_algs)):
    print(sorted_algs[i][0], sorted_algs[i][1])
