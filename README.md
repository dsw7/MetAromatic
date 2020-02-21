# Met-aromatic
Code for the following publications:  
* Weber, D. S.; Warren, J. J. The Interaction between Methionine and Two Aromatic Amino Acids Is an Abundant and Multifunctional Motif in Proteins. _Arch. Biochem. Biophys._ **2019**, _672_, 108053.  
* Weber, D. S.; Warren, J. J. A Survey of Methionine-Aromatic Interaction Geometries in the Oxidoreductase Class of Enzymes: What Could Met-Aromatic Interactions be Doing Near Metal Sites? _J. Inorg. Biochem._ **2018**, _186_, 34-41.  
## Synopsis
This program returns a list of closely spaced methionine-aromatic residues in a PDB structure of choosing. All code and unit tests are located under `src/`.
## Running Met-aromatic jobs in the terminal
The easiest means of performing Met-aromatic calculations is to run jobs in a terminal session. The simplest query follows:
```
$ python runner.py --code 1rcy
```
This will yield the following results:
```
ARO        POS        MET        POS        NORM       MET-THETA  MET-PHI
===========================================================================
TYR        122        MET        18         4.21071    75.76586   64.3175
TYR        122        MET        18         3.95401    60.14475   68.35187
TYR        122        MET        18         4.05137    47.19765   85.15065
TYR        122        MET        18         4.38983    53.39991   95.48742
TYR        122        MET        18         4.61966    68.45225   90.77119
TYR        122        MET        18         4.53651    78.56813   76.4056
PHE        54         MET        148        4.77709    105.94702  143.02178
PHE        54         MET        148        4.6104     93.38207   156.92157
PHE        54         MET        148        4.75563    93.28732   154.63001
PHE        54         MET        148        5.05181    105.07358  141.00282
===========================================================================
```
Here we have an order VI interaction between TYR 122 and MET 18. We also have an order IV interaction between PHE 54 and MET 148.
The `NORM` column specifies the distance between the MET residue and one of the midpoints between two carbon atoms in an aromatic
ring. There are six TYR 122 aromatic carbon atom midpoints less than 4.9 Angstroms from MET 18 in the above result. This cutoff distance
can be specified via the `--cutoff_distance` parameter:
```
$ python runner.py --code 1rcy --cutoff_distance 4.0
```
Reducing the cutoff distance yields an order I interaction between TYR 122 and MET 18.
```
ARO        POS        MET        POS        NORM       MET-THETA  MET-PHI
===========================================================================
TYR        122        MET        18         3.95401    60.14475   68.35187
===========================================================================
```
`MET-THETA` and `MET-PHI` refer to the angles between the vector that projects from the methionine SD atom to the aromatic carbon midpoint (termed vector _v_ in literature) and the angles describing the direction of the methionine SD lone pairs (termed vectors _a_ and _g_ in literature). We set a cutoff to ensure that we are not including results where one (or both) lone pairs are pointing away from the aromatic pi system - a condition which doesn't qualify as a true aromatic interaction. The cutoff angle can be specified via the `--cutoff_angle` parameter:
```
$ python runner.py --code 1rcy --cutoff_distance 4.5 --cutoff_angle 60
```
The `--cutoff_angle` parameter ensures that **at least one of** _Met-theta_ or _Met-phi_ angles falls below the cutoff. This is seen in the below order II interaction:
```
ARO        POS        MET        POS        NORM       MET-THETA  MET-PHI
===========================================================================
TYR        122        MET        18         4.05137    47.19765   85.15065
TYR        122        MET        18         4.38983    53.39991   95.48742
===========================================================================
```
The default lone pair interpolation model is `cp` or Cross Product (a thorough description is available in https://github.com/dsw7/DSW-Thesis). There exists another model, `rm` or Rodrigues Method for predicting the positions of lone pairs. This model is based on the Rodrigues' Rotation Formula. The model type can be passed as follows:
```
$ python runner.py --code 1rcy --cutoff_distance 4.5 --cutoff_angle 60 --model rm
```
Which yields similar results:
```
ARO        POS        MET        POS        NORM       MET-THETA  MET-PHI
===========================================================================
TYR        122        MET        18         3.95401    57.23706   64.22606
TYR        122        MET        18         4.05137    45.0966    80.76811
TYR        122        MET        18         4.38983    52.50492   91.84111
===========================================================================
```
Note that the Euclidean distances between TYR aromatic carbon atoms and MET remain unchanged. Many PDB entries contain multiple chains
denoted using capital letters. By default, this program searches for "A" delimited chains. Some researchers may, however, be interested in searching for aromatic interactions in a different chain within a multichain protein. The `--chain` parameter can be used to specify the chain:
```
$ python runner.py --code 1rcy --cutoff_distance 4.5 --cutoff_angle 60 --model rm --chain B
```
In this case, no results are returned because the PDB entry 1rcy does not contain a "B" chain. But what about bridging interactions? Bridging interactions are interactions whereby two or more aromatic residues meet the criteria of the Met-aromatic algorithm, for example, in the example below:  
![Alt text](docs/tyr-bridge.png?raw=true "Title")  
We can specify a search for bridging interactions, instead of conventional aromatic interactions, using the `--query` parameter. The default is `ai` for "aromatic interactions". `bi` can be instead be passed to search for bridges meeting defined Met-aromatic criteria. For example, to search for bridging interactions with a 7.0 Angstrom MET SD / midpoint distance in 6LU7:
```
$ python runner.py --code 6lu7 --query bi --cutoff_distance 7.0
```
Which will return a list as follows:
```
PHE185     MET165     PHE181
TYR209     PHE219     MET264
TRP207     TRP218     MET276
```
Where each row corresponds to a bridge. This program treats bridging interactions as networks with a defined set of vertices. For example, the above examples are 2-bridges with 3 vertices: ARO - MET - ARO. The `--vertices` parameter can be passed to search for n-bridges:
```
$ python runner.py --code 6lu7 --query bi --cutoff_distance 6.0 --vertices 4
```
## Tests
This project is well tested. Tests can be ran as follows:
```
python runner.py --test
```
Coverage tests can be ran as follows:
```
python runner.py --testcov
```
This will create an `htmlcov/` directory in the project root. The coverage report can be viewed by opening `htmlcov/index.html` in a browser. 
