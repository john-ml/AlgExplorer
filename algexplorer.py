import sys
import re
import os
import ast
import time
from analyzer import Analyzer
from collector import collect
from algorithm import *

# helper for main
def out(s):
    sys.stdout.write(s)
    sys.stdout.flush()

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
        out("Processing " + fcollection + " - ")
        c = Analyzer.fromcollection(n, fcollection)
        c.save(ftrained)
        out("saved to " + ftrained + ".\n")
    
    # collect list of raw algorithms
    out("Processing " + falgs + " - extracted ")
    alg_re = re.compile("([URFLDBMESurfldbxyz][2']?[2']? )+([URFLDBMESurfldbxyz][2']?[2']?)") # CE algs
    raw = []
    prevlen = str(len(raw))
    out(prevlen)
    for l in open(falgs):
        if alg_re.match(l):
            raw.append(parse(l[0:alg_re.match(l).span()[1]].strip()))
            if len(raw) % 1000 == 0:
                out("\b" * len(prevlen))
                prevlen = str(len(raw)/1000) + "k"
                out(prevlen)
    out("\b" * len(prevlen))
    out(str(len(raw)) + " algorithms.\n")

    # collect list of rewritten algorithms with substitutions r = L x, l = R x'
    algs = []
    if "-s" in flags:
        out("Performing substitutions ")
        rules = {strtomove("L"): [parse("r"), parse("x")[0]], strtomove("L'"): [parse("r'"), parse("x'")[0]],
                 strtomove("R"): [parse("l"), parse("x'")[0]], strtomove("R'"): [parse("l'"), parse("x")[0]],
                 strtomove("L2"): [parse("r2"), parse("x2")[0]], strtomove("R2"): [parse("l2"), parse("x2")[0]]}
        frac = 0
        for i in range(len(raw)):
            newfrac = progress_bar_size*i // len(raw)
            if newfrac != frac:
                out("|"*(newfrac-frac))
                frac = newfrac
            algs += rewrite(raw[i], rules)
        out("|"*(progress_bar_size - frac))
        out(" - constructed " + str(len(algs)-len(raw)) + " new algorithms.\n")
    else:
        algs = raw

    # trim algorithms of leading and trailing moves
    if "-tl" in flags:
        ltrims = flags[flags.index("-tl") + 1]
        out("Trimming " + ltrims + " (left) ")
        frac = 0
        for i in range(len(algs)):
            newfrac = progress_bar_size*i // len(algs)
            if newfrac != frac:
                out("|"*(newfrac-frac))
                frac = newfrac
            algs[i] = ltrim(algs[i], [movetypes.index(m) for m in ltrims])
        out("|"*(progress_bar_size - frac) + " - ")
    if "-tr" in flags:
        rtrims = flags[flags.index("-tr") + 1]
        if "-tl" in flags:
            out("trimming ")
        else:
            out("Trimming ")
        out(rtrims + " (right) ")
        frac = 0
        for i in range(len(algs)):
            newfrac = progress_bar_size*i // len(algs)
            if newfrac != frac:
                out("|"*(newfrac-frac))
                frac = newfrac
            algs[i] = rtrim(algs[i], [movetypes.index(m) for m in rtrims])
        out("|"*(progress_bar_size - frac) + " - ")
    if "-tl" in flags or "-tr" in flags:
        algs = [alg for alg in algs if alg != []]
        out("done.\n")
    
    # TODO: -r [xyz] to consider x, y, and z rotations before each alg (but never two rotations?)

    # sort algorithms descending algness, then ascending movecount
    out("Ranking algorithms ")
    sorted_algs = []
    if "-b" not in flags:
        c = Analyzer.fromsaved(ftrained)
        frac = 0
        for i in range(len(algs)):
            newfrac = progress_bar_size*i // len(algs)
            if newfrac != frac:
                out("|"*(newfrac-frac))
                frac = newfrac
            sorted_algs.append([c.analyze(algs[i]), algs[i]])
        out("|"*(progress_bar_size - frac))
    else: # analyze using Chad Batten's method
        out("(Batten)")
        bdflist = [strtomove("B"), strtomove("D"), strtomove("F")]
        bdf = [sum([1 for m in alg if m % len(movetypes) in bdflist]) for alg in algs]
        bdfgen = [len(set([movetostr(m % len(movetypes)).upper() for m in alg])) for alg in algs]
        bmoves = [[1,3]["B" in tostr(alg).upper()] for alg in algs]
        mt = [bdf[i] * bdfgen[i] * bmoves[i]**1.8 for i in range(min(len(bdf), len(bdfgen), len(bmoves)))]
        qtmmap = {0: 1, 1: 2, 2: 1}
        qtm = [sum([qtmmap[m//len(movetypes)] for m in alg]) for alg in algs]
        avgqtm = sum(qtm) / len(qtm)
        avgmt = sum(mt) / len(mt)
        t4 = avgqtm / avgmt
        if t4 < 1:
            t4 = 1 / (avgqtm * avgmt)
        else:
            t4 = avgqtm / avgmt
        fuf = [len(re.findall("F['2]? U['2]? F", tostr(alg).upper())) for alg in algs]
        evals = [(1.1*mt[i])**2 + (qtm[i]/t4)**1.7 + 4*fuf[i]**2 for i in range(min(len(mt), len(qtm), len(fuf)))]
        for i in range(len(algs)):
            sorted_algs.append([-evals[i], algs[i]])
    out(" - sorting - ")
    sorted_algs = sorted(sorted_algs, key=lambda x: -x[0])
    sorted_algs = sorted(sorted_algs, key=lambda x: movecount(x[1]))
    bar_size = 20
    out("done.\n")

    if "-o" in flags: # file output
        fout = flags[flags.index("-o") + 1]
        out("Writing " + fout + " ")
        output = open(fout, "w")
        frac = 0
        for i in range(len(sorted_algs)):
            newfrac = progress_bar_size*i // len(algs)
            if newfrac != frac:
                out("|"*(newfrac-frac))
                frac = newfrac
            moves = movecount(sorted_algs[i][1])
            if i == 0 or moves != movecount(sorted_algs[i-1][1]):
                output.write("-"*bar_size + str(moves) + " MOVERS" + "-"*bar_size + "\n")
            output.write("%6.2f\t%s\n" % (sorted_algs[i][0], tostr(sorted_algs[i][1])))
        out("|"*(progress_bar_size - frac))
        out(" - done.\n")
   
    if "-p" in flags: # peek at top n algs for each movecount level
        maxpeek = int(flags[flags.index("-p") + 1])
        peeked = 0
        for i in range(len(sorted_algs)):
            moves = movecount(sorted_algs[i][1])
            if i == 0 or moves != movecount(sorted_algs[i-1][1]):
                out("-"*bar_size + str(moves) + " MOVERS" + "-"*bar_size + "\n")
                peeked = 0
            if peeked < maxpeek:
                out("%6.2f\t%s\n" % (sorted_algs[i][0], tostr(sorted_algs[i][1])))
                peeked += 1

    end = time.time()
    out("Total time: %.3fs\n" % (end - start))
