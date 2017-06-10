import urllib
import re
import sys
import os
import ast

# converts move sequence to key
def key(seq):
    return "".join(seq).upper()

# update counts{} using alg
def count(counts, alg):
    m = alg.split(" ")
    for i in range(len(m)):
        k = key(m[i])
        counts.setdefault(k, 0)
        counts[k] += 1

# evaluate alg using counts{}
def algness(alg, counts):
    c = {}
    m = alg.split(" ")
    for i in range(len(m)):
        k = key(m[i])
        c.setdefault(k, 0)
        counts[k] += 1
    diff = 0
    for k in counts:
        obs = c.get(k, 0)
        exp = float(len(m))/counts["$size"] * counts[k]
        diff += (obs - exp)**2
    return diff / len(m)

def countall(counts, collection, storage):
    if os.path.isfile(collection):
        f = open(collection, "r")
        l = f.readlines()
    else:
        sys.stdout.write("Error: " + collection + " does not exist.\n")
        return
    sys.stdout.write("Processing " + collection + " - ")
    for line in l:
        count(counts, line.split("\t\t")[1])
    counts["$size"] = sum([len(m.split(" ")) for m in l])
    sys.stdout.write("storing counts - ")
    g = open(storage, "w")
    g.write(str(counts))
    g.close()
    sys.stdout.write("done.\n")

def load_counts(fname):
    f = open(fname, "r")
    return ast.literal_eval(f.readline())

def collect(f, i):
    # extract algs
    sys.stdout.write("Fetching " + str(i) + " - ")
    s = urllib.urlopen("http://cubesolv.es/solve/" + str(i)).read()
    r = re.compile("([URFLDBMESurflbdxyz][2']? ?)+.*LL")
    l = re.search("alg.cubing.net/\?alg=(.*)&amp;setup=",s)
    if l is None:
        sys.stdout.write("no reconstruction found.\n")
        return
    l = l.group(1).replace("_", " ").replace("-", "'").replace("%0A", "\n").split("\n")
    algs = [a.split("//")[0].strip() for a in l if a[-2:] == "LL"]
    
    # store algs in collection
    for alg in algs:
        f.write(str(i) + "\t\t" + alg + "\n")
    sys.stdout.write("collected (" + ", ".join([alg[0:20] + "..." for alg in algs]) + ").\n")

def learn(maxindex, collection, storage):
    start = 1
    if os.path.isfile(collection):
        sys.stdout.write("Previous collection detected - ")
        start = int(open(collection, "r").readlines()[-1].split("\t\t")[0])
        sys.stdout.write("resuming from " + str(start) + ".\n")
    sys.stdout.write("Collecting first " + str(maxindex) + " solves...\n")
    f = open(collection, "a")
    for i in range(start, maxindex+1):
        collect(f, i)
    f.close()
    sys.stdout.write("\nDone.\n")

    counts = {}
    countall(counts, collection, storage)

if __name__ == "__main__":
    learn(4800, "collection.txt", "trained.txt")
