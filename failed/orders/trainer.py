import urllib
import re
import sys
import os
import ast

n = 0
# update counts{} using alg
def count(counts, alg):
    m = alg.split(" ")
    for i in range(len(m)-n):
        k = "".join(m[i:i+n+1]).upper()
        if k in counts:
            counts[k] += 1
        else:
            counts[k] = 1

# evaluate alg using counts{}
def algness(alg, counts):
    result = 0
    m = alg.split(" ")
    for i in range(len(m)-n):
        k = "".join(m[i:i+n+1]).upper()
        if k in counts:
            result += counts[k]
    return result / len(m)

def collect(counts, collection, storage, i):
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
    if os.path.isfile(collection):
        f = open(collection, "a")
    else:
        f = open(collection, "w")
    for alg in algs:
        f.write(alg + "\n")
    f.close()
    sys.stdout.write("algs stored (" + ", ".join([alg[0:8] + "..." for alg in algs]) + ") - ")

    # update counts
    counts["last_collected"] = i
    for alg in algs:
        count(counts, alg)
    g = open(storage, "w")
    g.write(str(counts))
    g.close()
    sys.stdout.write("counts updated.\n")

def learn(maxindex, collection, storage):
    if os.path.isfile(storage):
        sys.stdout.write("Prior detected - ")
        f = open(storage, "r")
        counts = ast.literal_eval(f.readline())
        sys.stdout.write("counts loaded.\n")
    else:
        counts = {}
    if "last_collected" in counts:
        start = counts["last_collected"] + 1
    else:
        start = 1
    sys.stdout.write("Collecting first " + str(maxindex) + "...\n")
    for i in range(start, maxindex+1):
        collect(counts, collection, storage, i)
    sys.stdout.write("\nDone.\n");

if __name__ == "__main__":
    learn(4800, "collection.txt", "trained.txt")
