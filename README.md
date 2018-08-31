# AlgExplorer v2.0

A command-line utility that sorts a list of algorithms by how usable they are for speedsolving.

Ranking is done by a Markov model that's been trained on ~4000 solves pulled from [cubesolv.es](cubesolv.es).

It also automatically apply common substitutions like `L = r x'` to generate more ergonomic rewrites of algorithms with L, B, or D moves.

## Usage

`python algexplorer.py <input path> <stored model> [-c <collection path> -t <collection path> -s -p <max peek> -o <output path> -b -tl <left trims> -tr <right trims>]`

`<input path>`: Path to file with list of algorithms to be sorted.

`<stored model>`: Path to file with stored Markov model (used to evaluate algorithms).

`-c <collection path>`: Collects algorithms from cubesolv.es and stores in `<collection path>`.

`-t <collection path>`: Reads algorithms from `<collection path>`, constructs Markov model, stores in `<stored model>`.

`-s`: In addition to algorithms in `<input path>`, also considers algorithms with substitutions L = r x', R = l x.

`-p <max peek>`: Prints top `<max peek>` algorithms for each movecount level.

`-o <output path>`: Writes complete sorted list to `<output path>`.

`-b`: Uses Chad Batten's spreadsheet evaluation scheme.

`-tl <left trims>`: Trims all moves in `<left trims>` to the left of each algorithm.

`-tr <right trims>`: Trims all moves in `<right trims>` to the right of each algorithm.

## Sample usage:

```
> python algexplorer.py yperm_ruf.txt trained.txt -s -p 5 -o output.txt -tl Uxyz -tr Uxyz
Processing yperm_ruf.txt - extracted 237 algorithms.
Performing substitutions |||||||||| - constructed 16043 new algorithms.
Trimming Uxyz (left) |||||||||| - trimming Uxyz (right) |||||||||| - done.
Ranking algorithms |||||||||| - sorting - done.
Writing output.txt |||||||||| - done.
--------------------12 MOVERS--------------------
-15.44  l' B' R U2 R' B R B U2 B' U2 B'
-17.35  R' U' R F2 l' B R B U2 B' U2 B'
-17.85  l' B' R U2 l' D l B U2 B' U2 B'
-19.19  l' B' l F2 l' B R B U2 B' U2 B'
--------------------13 MOVERS--------------------
 -4.88  F R U' R' U' R U F U F' l' U B'
 -5.10  F2 U F' R F U' F' U' R' U R U l'
 -6.72  F l F' l' U' R U F U F' l' U B'
 -8.13  R2 U' R2 U' R2 U F U F' R2 F U' F'
 -8.51  F U F' R2 F U' F' U' R2 U R2 U R2
--------------------14 MOVERS--------------------
 -2.15  F R U' R' U' R U F U F' R' F U' F2
 -2.59  R' F' U F U F' U' R' U' R F R' U R2
 -3.56  R2 U' R F' R' U R U F U' F' U' F R
 -3.65  F R2 U F' U2 R' U' R U' F U' R' U' l'
 -3.86  F l F' l' U' R U F U F' R' F U' F2
--------------------15 MOVERS--------------------
 -1.17  R2 U' R2 U' R2 U R' F' R U R2 U' R' F R
 -1.57  R2 U' R2 U' R2 U R' F' R U R2 U' l' U R
 -1.63  R2 U' R2 U' R2 U R' F' R U R2 U' l' U l
 -1.70  R' F' R U R2 U' R' F R U' R2 U R2 U R2
 -1.89  F R U2 R' U' F' U2 F R' F R F' R U l'
--------------------16 MOVERS--------------------
 -0.76  F R' F R2 U' R' U' R U R' F' R U R' U' F'
 -0.97  F R U' R' U' R U R' F' R U R' U' l' U R
 -1.06  F R' F' R U R U' R' F R U' R' U R U l'
 -1.14  F l' U l2 F' l' U' R U R' F' R U R' U' F'
 -1.15  F R' F R2 U' R' U' R U l' U' l U R' U' F'
--------------------17 MOVERS--------------------
 -0.82  F R U' R' U' R U R' F' R U R' U' R' F R F'
 -0.86  F R' F' R U R U' R' F R U' R' U R U R' F'
 -1.04  F l' U' l U R U' R' F R U' R' U R U R' F'
 -1.09  F R U' R' U' R U R' F' R U R' U' l' U l F'
 -1.17  F R' F' R U R U' l' U l U' R' U R U R' F'
Total time: 1.465s
```
