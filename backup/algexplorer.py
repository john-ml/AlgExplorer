import sys
import re
import os
import ast
import time
from analyzer import Analyzer
from collector import collect
from algorithm import *

if __name__ == "__main__":
    falgs, ftrained, flags = sys.argv[1], sys.argv[2], sys.argv[3:]
    progress_bar_size = 10
    start = time.time()
    n = 2

    if "-c" in flags: # collect
        fcollection = flags[flags.index("-t") + 1]
        collect(4800, fcollection)

    if "-t" in flags: # train
        fcollection = flags[flags.index("-t") + 1]
        sys.stdout.write("Processing " + fcollection + " - ")
        c = Analyzer.fromcollection(2, fcollection)
        c.save(ftrained)
        sys.stdout.write("saved to " + ftrained + ".\n")
    
    # collect list of raw algorithms
    sys.stdout.write("Processing " + falgs + " - ")
    alg_re = re.compile("([URFLDBMESurfldbmesxyz][2']? )+")
    raw = [l[0:alg_re.match(l).span()[1]].strip() for l in open(falgs) if alg_re.match(l)]
    sys.stdout.write("extracted " + str(len(raw)) + " algorithms.\n")

    # TODO: expand parentheses, nospaces, etc.

    # collect list of rewritten algorithms with substitutions r = L x, l = R x'
    algs = []
    if "-s" in flags:
        sys.stdout.write("Performing substitutions ")
        frac = 0
        for i in range(len(raw)):
            newfrac = progress_bar_size*i / len(raw)
            if newfrac != frac:
                sys.stdout.write("|"*int(newfrac-frac))
                frac = newfrac
            algs += rewrite(raw[i], 0)
        sys.stdout.write("|"*int(progress_bar_size - frac))
        sys.stdout.write(" - constructed " + str(len(algs)-len(raw)) + " new algorithms.\n")
    else:
        algs = raw
    
    # TODO: -r [xyz] to consider x, y, and z rotations before each alg (but never two rotations?)

    # sort algorithms descending algness, then ascending movecount (TODO: don't let pre/post AUF affect movecount, can just change the way moves is computed! perhaps algmoves(s))
    sys.stdout.write("Ranking algorithms ")
    c = Analyzer.fromsaved(ftrained)
    frac = 0
    sorted_algs = []
    for i in range(len(algs)):
        newfrac = progress_bar_size*i / len(algs)
        if newfrac != frac:
            sys.stdout.write("|"*int(newfrac-frac))
            frac = newfrac
        sorted_algs.append([c.analyze(algs[i]), algs[i]])
    sys.stdout.write("|"*int(progress_bar_size - frac))
    sys.stdout.write(" - sorting - ")
    sorted_algs = sorted(sorted_algs, key=lambda x: -x[0])
    sorted_algs = sorted(sorted_algs, key=lambda x: len(x[1].split(" ")))
    bar_size = 20
    
    if "-o" in flags: # file output
        fout = flags[flags.index("-o") + 1]
        sys.stdout.write("writing " + fout + " - ")
        out = open(fout, "w")
        for i in range(len(sorted_algs)):
            moves = movecount(sorted_algs[i][1])
            if i == 0 or moves != movecount(sorted_algs[i-1][1]):
                out.write("-"*bar_size + str(moves) + " MOVERS" + "-"*bar_size + "\n")
            out.write("%6.2f\t%s\n" % tuple(sorted_algs[i]))

    sys.stdout.write("done.\n")
   
    if "-p" in flags: # peek at top n algs for each movecount level
        maxpeek = int(flags[flags.index("-p") + 1])
        peeked = 0
        for i in range(len(sorted_algs)):
            moves = movecount(sorted_algs[i][1])
            if i == 0 or moves != movecount(sorted_algs[i-1][1]):
                sys.stdout.write("-"*bar_size + str(moves) + " MOVERS" + "-"*bar_size + "\n")
                peeked = 0
            if peeked < maxpeek:
                sys.stdout.write("%6.2f\t%s\n" % tuple(sorted_algs[i]))
                peeked += 1

    end = time.time()
    sys.stdout.write("Total time: %.3fs" % (end - start))
