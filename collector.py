import sys
import os
import urllib
import re

# extract algs from cubesolv.es/solve/i, save to f (TODO: handle // CMLL(EO))
def collectone(f, i):
    # fetch from URL
    sys.stdout.write("Fetching " + str(i) + " - ")
    s = urllib.urlopen("http://cubesolv.es/solve/" + str(i)).read()
    r = re.compile("([URFLDBMESurflbdxyz][2']? ?)+.*LL")
    l = re.search("alg.cubing.net/\?alg=(.*)&amp;setup=",s)
    if l is None:
        sys.stdout.write("no reconstruction found.\n")
        return
    l = l.group(1).replace("_", " ").replace("-", "'").replace("%0A", "\n").split("\n")
    algs = [a.split("//")[0].strip() for a in l if a[-2:] == "LL"]
    
    # store in collection
    for alg in algs:
        f.write(str(i) + "\t\t" + alg + "\n")
    sys.stdout.write("collected (" + ", ".join([alg[0:20] + "..." for alg in algs]) + ").\n")

# extract algs from cubesolv.es/solve/(1 .. i), save to collection
def collect(maxindex, collection):
    sys.stdout.write("Collecting first " + str(maxindex) + " solves...\n")
    start = 1
    if os.path.isfile(collection):
        sys.stdout.write("Previous collection detected - ")
        start = 1 + int(open(collection, "r").readlines()[-1].split("\t\t")[0])
        sys.stdout.write("resuming from " + str(start) + ".\n")
    f = open(collection, "a")
    for i in range(start, maxindex+1):
        collectone(f, i)
    f.close()
    sys.stdout.write("Done.\n")
