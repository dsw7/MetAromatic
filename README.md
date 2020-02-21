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
In this case, no results are returned because the PDB entry 1rcy does not contain a "B" chain.
### More information about cutoff distances and cutoff angles  
The following figure provides an excellent overview of the geometry of the system being probed by Met-aromatic. We have a vector **v** in our figure below. **v** points from the methionine SD coordinate to a midpoint between two aromatic carbon atoms. _Distance condition_. Methionine / aromatic residue pairs are saved for further analysis if the vector **v** between the two is of magnitude ≤ to the value inputted in **B**. _Angular condition_. We also have two vectors, **a** and **g**. These vectors estimate the position and direction of the lone pairs of the sulfur atom. Here, an interaction is printed to the prompt **if** either the **a** / **v** angle **or** the **g** / **v** angle is ≤ the value inputted into edit box **C**.    
<img src="https://github.com/dsw7/MetAromatic/blob/master/frontend/images/cd_schematic_chapter2.png" width="400">  
### Interpreting the results  
The protein 1rcy was analyzed using the MetAromatic application. Here we set ||**v**|| ≤ 4.9 Angstroms and the cutoff angle ≤ 109.5 degrees. The results are as follows:  
<img src="https://github.com/dsw7/MetAromatic/blob/master/frontend/images/results_1rcy_v19_90.png">  
Consider the last three RESULT lines:  
    
    #                     ||v|| Met-theta Met-phi
    RESULT PHE 54 MET 148 4.777 105.947 143.022  
    RESULT PHE 54 MET 148 4.610 93.3820 156.922  
    RESULT PHE 54 MET 148 4.756 93.2870 154.630  
Here the SD on MET 148 is ≤ 4.9 Angstroms of a total of three of six midpoints on the PHE 54 aromatic ring. The angle between 3 vectors **v** and the two SD lone pairs is ≤ 109.5 degrees in three cases.  
## Tests 
Almost all Met-aromatic code is thoroughly tested. Tests can be run as follows:
```
$ cd tests && python -m pytest -vs .
```
## Requirements
Project dependencies are located in the `requirements.txt` file. This file may not necessarily be up to date. To get up to date requirements, run:
```
$ pipreqs --force
```
The ```pipreqs``` utility can be installed as follows:
```
$ python -m pip install pipreqs
```
