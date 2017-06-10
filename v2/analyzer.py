import sys
import os
import ast
import math
import itertools
from algorithm import *

class Analyzer:
    def __init__(self, n):
        self.n = n
        self.r = 3 * len(movetypes)
        self.kmax = self.r**n
        self.pr = {}
        
    # construct chain from collection
    @classmethod
    def fromcollection(cls, n, collection):
        self = cls(n)
        if os.path.isfile(collection):
            f = open(collection, "r")
            l = f.readlines()
        else:
            sys.stdout.write("Error: " + collection + " does not exist.\n")
            return
        for line in l:
            self.count(parse(line.split("\t\t")[1]))
        self.normalize()
        return self

    # update counts with moves
    def count(self, m):
        if len(m) <= self.n: # nothing to count
            return
        key = 0
        for i in range(self.n):
            key = (key * self.r) + m[i]
        for i in range(self.n, len(m)):
            new = m[i]
            self.pr.setdefault(key, {})
            self.pr[key].setdefault(new, 0)
            self.pr[key][new] += 1
            key = (key * self.r) % self.kmax + new

    # transform counts into transition probabilities
    def normalize(self):
        for j in self.pr:
            total = float(sum([self.pr[j][k] for k in self.pr[j]]))
            for k in self.pr[j]:
                self.pr[j][k] /= total
        
    # construct chain from stored data
    @classmethod
    def fromsaved(cls, stored):
        f = open(stored, "r")
        n = ast.literal_eval(f.readline().strip())
        self = cls(n)
        self.pr = ast.literal_eval(f.readline().strip())
        return self

    # store chain in fname
    def save(self, fname):
        g = open(fname, "w")
        g.write(str(self.n) + "\n" + str(self.pr) + "\n")
        g.close()
    
    # evaluate movelist m
    def analyze(self, m):
        result = 0
        zero = 1e-10
        key = 0
        for i in range(self.n):
            key = (key * self.r) + m[i]
        for i in range(self.n, len(m)):
            new = m[i]
            if key in self.pr and new in self.pr[key]:
                result += math.log(self.pr[key][new]) # log-likelihood
            else:
                result += math.log(zero)
            key = (key * self.r) % self.kmax + new
        return result / len(m) # normalize by alg length
