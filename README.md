# Met-aromatic
Code for the following publications:  
* Weber, D. S.; Warren, J. J. The Interaction between Methionine and Two Aromatic Amino Acids Is an Abundant and Multifunctional Motif in Proteins. _Arch. Biochem. Biophys._ **2019**, _672_, 108053.  
* Weber, D. S.; Warren, J. J. A Survey of Methionine-Aromatic Interaction Geometries in the Oxidoreductase Class of Enzymes: What Could Met-Aromatic Interactions be Doing Near Metal Sites? _J. Inorg. Biochem._ **2018**, _186_, 34-41.  
## Updates
I am porting this code to C++ for increased performance. See [MetAromaticCPP](https://github.com/dsw7/MetAromaticCPP).
## Synopsis
This program returns a list of closely spaced methionine-aromatic residue pairs for structures in the [Protein Data Bank](https://www.rcsb.org/) (PDB). The program supports running queries on single PDB entries or large scale multithreaded batch jobs consisting of hundreds of thousands of queries. 
## How it works
<!---
Use svg for rendering and HTML for the embed code!
--->
### Step 1: Data preprocessing
Files in the PDB are organized using the SMCRA hierarchy: _Structure_, _Model_, _Chain_, _Residue_ and _Atom_. For example, here is the fifth line for the entry 1RCY:
```
1         2  3   4   5   6     7         8      9       10   11              12
ATOM      5  CB  THR A   5     -13.081   2.366  23.788  1.00 37.95           C
```
Each line in a file corresponds to a single atom. In the above example, we have a carbon atom that is labelled `CB` (column 3) on a threonine residue (`THR`, column 4) located on the `A` chain (column 5). Columns 7-9 specify the _x_, _y_, _z_ coordinates of the carbon atom.  

The Met-aromatic program starts by downloading a `*.pdb` file from the PDB over FTP. The file is then stripped down to the subset of coordinates corresponding to a chain `[A-Z]` of choosing. Most PDB entries consist of `A` and `B` chains. The program then strips the dataset down to the residues tyrosine (`TYR`), tryptophan (`TRP`), phenylalanine (`PHE`), and methionine (`MET`). In the last step of preprocessing, the program further strips the dataset down to any of the following atoms:
```
MET: CE, SD, CG  
TYR: CD1, CE1, CZ, CG, CD2, CE2
TRP: CD2, CE3, CZ2, CH2, CZ3, CE2
PHE: CD1, CE1, CZ, CG, CD2, CE2
```
The above atoms are the aromatic carbon atoms in the aromatic residues tyrosine (`TYR`), tryptophan, (`TRP`) and phenylalanine (`PHE`).
### Step 2: The distance condition
The program applies the distance condition to find methionine-aromatic pairs that are _physically near each other_. To do so, the program first finds the midpoints between all neighbouring aromatic carbon atoms in all of tyrosine, tryptophan and phenylalanine. These midpoints are denoted using a `*`: 
```
TYR: CD1*|CE1*|CZ*|CG*|CD2*|CE2*
TRP: CD2*|CE3*|CZ2*|CH2*|CZ3*|CE2*
PHE: CD1*|CE1*|CZ*|CG*|CD2*|CE2*
```
Next, the program finds all the vectors projecting from all methionine `SD` atoms to all the midpoints `*`. As an example, a substructure consisting of one methionine and two phenylalanines would have 12 possible such vectors, depicted here as <img src="https://latex.codecogs.com/svg.latex?\vec{v}">, owing to the fact there can exist a total of six midpoints between neighbouring atoms in a hexagonal arrangement of atoms and there are two such arrangements for two phenylalanine residues.

To apply the distance condition, the program simply banks those methionine-aromatic pairs where one or more vectors <img src="https://latex.codecogs.com/svg.latex?\vec{v}"> are less than or equal to some cutoff <img src="https://latex.codecogs.com/svg.latex?c">. As a motivating example, `CD1*` in `TYR` is the midpoint between the `CD1` and `CE1` carbon atoms. A `CD1* / SD` on an aromatic / methionine pair would meet the distance condition if the following held:
<p align="center">
  <img width="500" height="35" src="https://latex.codecogs.com/svg.latex?\|\vec{v}\|=\sqrt{(CD1_x*-SD_x)^2&plus;(CD1_y*-SD_y)^2&plus;(CD1_z*-SD_z)^2}&space;\leq&space;c">
</p>

### Step 3: The angular condition
Any methionine-aromatic pairs meeting the distance condition are subjected to the angular condition. The angular condition can be loosely interpreted as _"find all the methionine-aromatic pairs where the methionine lone pairs are pointing into or near the region(s) of highest electron density on a corresponding aromatic moiety_." To apply the angular condition, two new vectors are introducted: vector <img src="https://latex.codecogs.com/svg.latex?\vec{a}" /> and vector <img src="https://latex.codecogs.com/svg.latex?\vec{g}" />, which describe the orientation of the `SD` lone pairs in three dimensional space. To find the lone pairs, the program considers the `SD` atom in a methionine atom to be the center of a regular tetrahedron with vertices `CE` and `CG`. Solving for the position of the remaining two vertices yields vectors <img src="https://latex.codecogs.com/svg.latex?\vec{a}"> and <img src="https://latex.codecogs.com/svg.latex?\vec{g}">. Next, the program obtains the angles between the lone pairs and <img src="https://latex.codecogs.com/svg.latex?\vec{v}">:  
<p align="center">
  <img src="https://latex.codecogs.com/svg.latex?\theta,&space;\phi&space;=&space;cos^{-1}\left&space;(\frac{\|\vec{a}\|\|\vec{v}\|}{\vec{a}\cdot\vec{v}}&space;\right&space;),&space;cos^{-1}\left&space;(\frac{\|\vec{g}\|\|\vec{v}\|}{\vec{g}\cdot\vec{v}}&space;\right&space;)" title="\theta, \phi = cos^{-1}\left (\frac{\|\vec{a}\|\|\vec{v}\|}{\vec{a}\cdot\vec{v}} \right ), cos^{-1}\left (\frac{\|\vec{g}\|\|\vec{v}\|}{\vec{g}\cdot\vec{v}} \right )" />
</p>

Last, a methionine-aromatic pair is deemed interacting if any of <img src="https://latex.codecogs.com/svg.latex?\theta"> or <img src="https://latex.codecogs.com/svg.latex?\phi" /> is less than or equal to some cutoff angle <img src="https://latex.codecogs.com/svg.latex?\delta">, that is, if <img src="https://latex.codecogs.com/svg.latex?\theta&space;\leq&space;\delta&space;\vee&space;\phi&space;\leq&space;\delta"> holds.
### Summary
The end result is a dataset consisting of methionine-aromatic pairs whereby one or both of the methionine lone pairs are pointing into or near the region of highest electron density on the corresponding aromatic residues. A representative figure is shown below:
<p align="center">
  <img width="336" height="300" src=https://github.com/dsw7/MetAromatic/blob/master/docs/met18_tyr122.png>
</p>

## Running Met-aromatic jobs in the terminal
The easiest means of performing Met-aromatic calculations is to run jobs in a terminal session. The simplest query follows:
```
$ ./runner.py single-met-aromatic-query 1rcy
```
Here, the `single-met-aromatic-query` argument specifies that we want to run a single aromatic interaction calculation. The query will yield the following results:
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
Above we have an order VI interaction between TYR 122 and MET 18, that is, all six vectors <img src="https://latex.codecogs.com/svg.latex?\vec{v}" /> projecting from the `SD` on MET 18 to the midpoints on TYR 122 meet Met-aromatic criteria. We also have an order IV interaction between PHE 54 and MET 148. The `NORM` column specifies the actual distance (in <img src="https://latex.codecogs.com/svg.latex?\AA" />) between the MET residue and one of the midpoints between two carbon atoms in an aromatic ring, or <img src="https://latex.codecogs.com/svg.latex?\left&space;\|&space;\vec{v}&space;\right&space;\|" />. The default cutoff <img src="https://latex.codecogs.com/svg.latex?c" /> was applied in the above example, at 4.9 <img src="https://latex.codecogs.com/svg.latex?\AA" />. The cutoff can be adjusted, however, using the `--cutoff-distance` option:
```
$ ./runner.py single-met-aromatic-query 1rcy --cutoff-distance 4.0
```
Reducing the cutoff distance yields an order I interaction between TYR 122 and MET 18.
```
ARO        POS        MET        POS        NORM       MET-THETA  MET-PHI
===========================================================================
TYR        122        MET        18         3.95401    60.14475   68.35187
===========================================================================
```
`MET-THETA` and `MET-PHI` refer to <img src="https://latex.codecogs.com/svg.latex?\theta" /> and <img src="https://latex.codecogs.com/svg.latex?\phi" />, respectively. In the above example, the default cutoff angle <img src="https://latex.codecogs.com/svg.latex?\delta" /> is used (<img src="https://latex.codecogs.com/svg.latex?109.5^\circ" />). The cutoff angle can be adjusted by using the `--cutoff-angle` option:
```
$ ./runner.py single-met-aromatic-query 1rcy --cutoff-distance 4.5 --cutoff-angle 60
```
The `--cutoff-angle` option ensures that **at least one of** <img src="https://latex.codecogs.com/svg.latex?\theta" /> or <img src="https://latex.codecogs.com/svg.latex?\phi" /> angles fall below the cutoff <img src="https://latex.codecogs.com/svg.latex?\delta" />. This is seen in the below order II interaction:
```
ARO        POS        MET        POS        NORM       MET-THETA  MET-PHI
===========================================================================
TYR        122        MET        18         4.05137    47.19765   85.15065
TYR        122        MET        18         4.38983    53.39991   95.48742
===========================================================================
```
The default lone pair interpolation model is `cp` or Cross Product (a thorough description is available in https://github.com/dsw7/DSW-Thesis). There exists another model, `rm` or Rodrigues Method for predicting the positions of lone pairs. This model is based on the Rodrigues' Rotation Formula. The model type can be passed as follows:
```
$ ./runner.py single-met-aromatic-query 1rcy --cutoff-distance 4.5 --cutoff-angle 60 --model rm
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
Note that the Euclidean distances between TYR aromatic carbon atoms and MET remain unchanged. By default, this program searches for "A" delimited chains. Some researchers may, however, be interested in searching for aromatic interactions in a different chain within a multichain protein. The `--chain` option can be used to specify the chain:
```
$ ./runner.py single-met-aromatic-query 1rcy --cutoff-distance 4.5 --cutoff-angle 60 --model rm --chain B
```
In this case, no results are returned because the PDB entry 1rcy does not contain a "B" chain. But what about bridging interactions? Bridging interactions are interactions whereby two or more aromatic residues meet the criteria of the Met-aromatic algorithm, for example, in the example below (PDB entry 6C8A):  
<p align="center">
  <img width="399" height="300" src=https://github.com/dsw7/MetAromatic/blob/master/docs/tyr_phe_bridge_6c8a.png>
</p>  

We can specify a search for bridging interactions, instead of conventional aromatic interactions, using the `single-bridging-interaction-query` argument. For example, to search for bridging interactions with a 7.0 <img src="https://latex.codecogs.com/svg.latex?\AA" /> <img src="https://latex.codecogs.com/svg.latex?\left&space;\|&space;\vec{v}&space;\right&space;\|" /> cutoff in 6LU7:
```
$ ./runner.py single-bridging-interaction-query 6lu7 --cutoff-distance 7.0
```
Which will return a list as follows:
```
PHE185     MET165     PHE181
TYR209     PHE219     MET264
TRP207     TRP218     MET276
```
Where each row corresponds to a bridge. This program treats bridging interactions as networks with a defined set of vertices. For example, the above examples are 2-bridges with 3 vertices: ARO - MET - ARO. The `--vertices` option can be passed to search for n-bridges:
```
$ ./runner.py single-bridging-interaction-query 6lu7 --cutoff-distance 6.0 --vertices 4
```
## Batch jobs
This software is normally used for large scale Protein Data Bank mining efforts. To run a batch job, first supply a batch. A batch
can be a regular text file consisting of delimited PDB codes:
```
1BPY, 1CWE, 1DZI, 1EAK, 1EB1, 1GU4, 1GU5, 1GXC, 1GY3, 1H6F,
1JYR, 1M4H, 1MCD, 1N0X, 1NU8, 1O6P, 1OKV, 2A2X, 1WB0
```
The results of the batch job are stored in a MongoDB database (https://www.mongodb.com/). The command follows:
```
$ ./runner.py run-batch-job /path/to/pdb_codes.txt --threads 3 --database small_batch --collection example
```
The MongoDB dump database is specified using the `--database` option. The collection is specified with the `--collection` option. The `--threads` option specifies how many threads to use for processing the batch. The recommended number of threads is 12 on a 300 Mbps network and a machine that is running no other processes. By default, mining jobs are run on `localhost` and on port `27017`. However, results can be routed to other servers by specifying hosts and/or ports using the `--host` and `--port` parameters. A batch job will generate a collection secondary to the collection specified by `--collection`. This secondary collection will house all the batch job parameters and other statistics and the collection name will be suffixed with `_info`. An example `*_info` collection for the above example follows:
```
{
        "_id" : ObjectId("5e6b2e1326dea0202cec2963"),
        "num_threads" : 3,
        "cutoff_distance" : 6,
        "cutoff_angle" : 109.5,
        "chain" : "A",
        "model" : "cp",
        "batch_job_execution_time" : 4.938377618789673,
        "data_acquisition_date" : ISODate("2020-03-12T23:54:11.719Z"),
        "number_of_entries" : 19
}
```
## Tests and automation
This project is well tested. Tests can be ran as follows:
```
$ ./runner.py run-tests
```
Coverage tests can be ran as follows:
```
$ ./runner.py run-tests-with-coverage
```
This will create an `htmlcov` directory under `/tmp`. The coverage report can be viewed by opening `/tmp/htmlcov/index.html` in a browser. A custom path can be specified with the `--path-to-html` option. The testing and linting process for this project can also be automated using `nox`, that is, by running:
```
$ nox
```
Or
```
$ python3 -m nox
```
The project's `noxfile` will create a `nox` `envdir` under `/tmp` named `.nox_met_aromatic`. The `noxfile` will lint the project and run tests with coverage. The `.nox_met_aromatic` directory will contain the environments for the corresponding `nox` sessions, an `htmlcov` directory containing the coverage report, and the `nox` report, `nox_report_met_aromatic` after the run has completed.
