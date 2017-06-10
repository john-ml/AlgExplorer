AlgExplorer v1.0

A command-line utility that sorts a list of algorithms by how usable they are for speedsolving.

Usage: algexplorer.py <input path> <stored model> [-c <collection path> -t <collection path> -s -p <max peek> -o <output path>]

<input path>: Path to file with list of algorithms to be sorted.
<stored model>: Path to file with stored Markov model (used to evaluate algorithms).
-c <collection path>: Collects algs from cubesolv.es and stores in <collection path>.
-t <collection path>: Reads algs from <collection path>, constructs Markov model, stores in <stored model>.
-s: In addition to algorithms in <input path>, also considers algorithms with substitutions L = r x', R = l x.
-p <max peek>: Prints top <max peek> algorithms for each movecount level.
-o <output path>: Writes complete sorted list to <output path>

Sample usage:
> algexplorer.py yperm_ruf.txt trained.txt -s -p 5 -o output.txt
Processing yperm_ruf.txt - extracted 237 algorithms.
Performing substitutions |||||||||| - constructed 16043 new algorithms.
Ranking algorithms |||||||||| - sorting - writing output.txt - done.
--------------------13 MOVERS--------------------
 -8.09  R' U' l D2 l' U R U F2 U' F2 U' F2
 -8.63  R2 U' R2 U' R2 U F U F' R2 F U' F'
 -8.74  F U F' R2 F U' F' U' R2 U R2 U R2
 -9.76  F2 U F2 U F2 U' R' U' l D2 l' U l
 -9.78  F2 U F2 U F2 U' R' U' l D2 l' U R
--------------------14 MOVERS--------------------
 -2.04  R2 U' l D' l' U R U F U' F' U' F R
 -2.19  R2 U' R F' R' U R U F U' F' U' F R
 -2.54  R' F' U F U F' U' R' U' l D l' U l2
 -2.65  R' F' U F U F' U' R' U' l D l' U R2
 -2.72  R' F' U F U F' U' R' U' R F R' U R2
--------------------15 MOVERS--------------------
 -1.52  R2 U' R2 U' R2 U R' F' R U R2 U' R' F R
 -1.80  R' F' R U R2 U' R' F R U' R2 U R2 U R2
 -1.88  l' U' l U R2 U' R' F R U' R2 U R2 U R2
 -1.88  R2 U' R2 U' R2 U R' F' R U R2 U' l' U l
 -1.90  R2 U' R2 U' R2 U R' F' R U R2 U' l' U R
--------------------16 MOVERS--------------------
 -0.88  F R' F R2 U' R' U' R U R' F' R U R' U' F'
 -1.24  F R' F R2 U' R' U' R U l' U' l U R' U' F'
 -1.45  F l' U l2 F' l' U' R U R' F' R U R' U' F'
 -1.81  F l' U l2 F' l' U' R U l' U' l U R' U' F'
 -2.49  F R' F R2 U' R' U' R U R' F' l F l' U' F'
--------------------17 MOVERS--------------------
 -0.90  F R U' R' U' R U R' F' R U R' U' R' F R F'
 -0.94  F R' F' R U R U' R' F R U' R' U R U R' F'
 -0.96  F l' U' l U R U' R' F R U' R' U R U R' F'
 -1.02  F R U' R' U' R U R' F' R U R' U' l' U R U'
 -1.07  F R U' R' U' R U R' F' R U R' U' l' U l F'
--------------------18 MOVERS--------------------
 -2.78  U R U2 R' U' F2 R U2 R' U2 l' U2 l U R U2 R' U2
 -2.79  U R U2 R' U' F2 R U2 R' U2 R' F2 R U R U2 R' U2
 -3.52  U R F U' R2 F R F' R U F' R' U' F R U R' F'
 -3.69  U R F U' R2 F R F' R U F' R' U' F R U l' U'
 -4.03  U R U2 R' U' F2 R U2 R' U2 l' U2 l U R U2 l' B2
Total time: 1.496s