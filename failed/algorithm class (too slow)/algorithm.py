import re

# helper for Algorithm.inverse() and Algorithm.removenegatives()
def islist(x):
    return type(x) == type([0]) # bite me

class Algorithm:
    movetypes = "URFLBDurflbdMESmesxyz"
    # moves represented by ints [0, 3m) where m = len(movetypes)
    # [0, m)    cw quarter turns
    # [m, 2m)   half quarter turns
    # [2m, 3m)  ccw turns
    @staticmethod
    def movetostring(m):
        modifiers = ["", "2", "'"]
        lm = len(Algorithm.movetypes)
        return Algorithm.movetypes[m % lm] + modifiers[m // lm]

    # split (RU'23R'U')2 -> ( R U ' 23 R ' U ' ) 2
    @staticmethod
    def tokenize(alg):
        r = "([0-9]+|'| |\(|\)|[" + Algorithm.movetypes + "])"
        return [l for l in re.split(r, alg) if l.strip() != ""]

    # transform [[movetype, quarter turns]] -> [[movetype, -quarter turns]]
    # transform [[move tree, quarter turns]] -> [[inverted tree, quarter turns]]
    @staticmethod
    def inverse(tree):
        result = []
        for i in range(len(tree)-1, -1, -1):
            m = tree[i]
            if islist(m[0]):
                result.append([Algorithm.inverse(m[0]), m[1]])
            else:
                result.append([m[0], -m[1]])
        return result

    # force [[move tree, q]] where all q > 0
    @staticmethod
    def removenegatives(tree):
        for i in range(len(tree)):
            if tree[i][1] < 0:
                tree[i] = Algorithm.inverse([tree[i]])[0]
                tree[i][1] *= -1
                if not islist(tree[i][0]):
                    tree[i][1] %= 4
            if islist(tree[i][0]): # is a list
                Algorithm.removenegatives(tree[i][0])

    # transform [[[a, b], c]] -> [[[a, b]]*c]
    @staticmethod
    def flattened(tree):
        result = []
        for i in range(len(tree)):
            if islist(tree[i][0]): # append copies of recursively expanded sublist
                result += Algorithm.flattened(tree[i][0]) * tree[i][1]
            else:
                result.append([tree[i][0], tree[i][1] % 4])
        return result
        
    # transform ( R U ' 23 R ' U ' ) 2 -> [[movetype, quarter turns]]
    @staticmethod
    def transform(tokens):
        tree = []
        lparens = []
        # build tree of moves
        for i in range(len(tokens)):
            t = tokens[i]
            if t == "(" or t == ")" or t in Algorithm.movetypes: # pop unnecessary )
                if len(tree) > 0 and tree[-1] == ")":
                    tree.pop()
                    lparens.pop()
            if t == "(": # push (
                lparens.append(len(tree))
            elif t == ")": # push )
                if i != len(tokens)-1:
                    tree.append(t)
            elif t in Algorithm.movetypes: # push new move
                m = Algorithm.movetypes.index(t)
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
        Algorithm.removenegatives(tree)
        return Algorithm.flattened(tree)

    # transform [[R, 1], [R, 1]] -> [[R, 2]]
    # TODO: R L R' = L? R L r' = M L?
    @staticmethod
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
            return Algorithm.compressed(result)

    # transform "R U R' U'" -> [1, 0, 2m+1, 2m] where m = len(movetypes)
    @staticmethod
    def parse(alg):
        moves = Algorithm.compressed(Algorithm.transform(Algorithm.tokenize(alg)))
        return [m[0] + len(Algorithm.movetypes)*(m[1] - 1) for m in moves]

    # construct from string
    def __init__(self, s):
        self.moves = Algorithm.parse(s)
        self.eval = None

    # construct from moves[]
    @classmethod
    def frommoves(cls, moves):
        self = cls("")
        self.moves = moves
        return self

    def getmoves(self):
        return self.moves
    
    def movecount(self):
        return len(self.moves)

    def algmovecount(self):
        return len(self.moves)

    # return (and cache) evaluation by Analyzer
    def geteval(self, analyzer):
        if self.eval is None:
            self.eval = analyzer.analyze(self.moves)
        return self.eval

    def __str__(self):
        return " ".join([Algorithm.movetostring(m) for m in self.moves])

    @staticmethod
    # rewrite alg by substituting ith move with wide move
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

    @staticmethod
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
