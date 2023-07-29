# Met-aromatic
Code for the following publications:
* Weber, D. S.; Warren, J. J. The Interaction between Methionine and Two Aromatic Amino Acids Is an Abundant
  and Multifunctional Motif in Proteins. _Arch. Biochem. Biophys._ **2019**, _672_, 108053.
* Weber, D. S.; Warren, J. J. A Survey of Methionine-Aromatic Interaction Geometries in the Oxidoreductase
  Class of Enzymes: What Could Met-Aromatic Interactions be Doing Near Metal Sites? _J. Inorg. Biochem._
**2018**, _186_, 34-41.
## Table of Contents
- [Synopsis](#synopsis)
- [How it works](#how-it-works)
  - [Step 1: Data preprocessing](#step-1-data-preprocessing)
  - [Step 2: The distance condition](#step-2-the-distance-condition)
  - [Step 3: The angular condition](#step-3-the-angular-condition)
  - [Summary](#summary)
- [Setup](#setup)
- [Basic usage](#basic-usage)
  - [Finding Met-aromatic pairs](#finding-met-aromatic-pairs)
  - [Finding "bridging interactions"](#finding-bridging-interactions)
- [Batch jobs and MongoDB integration](#batch-jobs-and-mongodb-integration)
  - [A brief overview](#a-brief-overview)
  - [Designing a distributed mining strategy](#designing-a-distributed-mining-strategy)
- [Using the MetAromatic API](#using-the-metaromatic-api)
  - [Example: programmatically obtaining Met-aromatic pairs](#example-programmatically-obtaining-met-aromatic-pairs)
  - [Example: programmatically obtaining bridging interactions](#example-programmatically-obtaining-bridging-interactions)
- [Tests and automation](#tests-and-automation)

## Synopsis
This program returns a list of closely spaced methionine-aromatic residue pairs for structures in the [Protein
Data Bank](https://www.rcsb.org/) (PDB). The program supports running queries on single PDB entries or large
scale multithreaded batch jobs consisting of hundreds of thousands of queries.
## How it works
### Step 1: Data preprocessing
Files in the PDB are organized using the SMCRA hierarchy: _Structure_, _Model_, _Chain_, _Residue_ and _Atom_.
For example, here is the fifth line for the entry 1RCY:
```
1         2  3   4   5   6     7         8      9       10   11              12
ATOM      5  CB  THR A   5     -13.081   2.366  23.788  1.00 37.95           C
```
Each line in a file corresponds to a single atom. In the above example, we have a carbon atom that is labelled
`CB` (column 3) on a threonine residue (`THR`, column 4) located on the `A` chain (column 5). Columns 7-9
specify the $x$, $y$, $z$ coordinates of the carbon atom.

The Met-aromatic program starts by downloading a `*.pdb` file from the PDB over FTP. The file is then stripped
down to the subset of coordinates corresponding to a chain `[A-Z]` of choosing. Most PDB entries consist of
`A` and `B` chains. The program then strips the dataset down to the residues tyrosine (`TYR`), tryptophan
(`TRP`), phenylalanine (`PHE`), and methionine (`MET`). In the last step of preprocessing, the program further
strips the dataset down to any of the following atoms:
```
MET: CE, SD, CG
TYR: CD1, CE1, CZ, CG, CD2, CE2
TRP: CD2, CE3, CZ2, CH2, CZ3, CE2
PHE: CD1, CE1, CZ, CG, CD2, CE2
```
The above atoms are the aromatic carbon atoms in the aromatic residues tyrosine (`TYR`), tryptophan, (`TRP`)
and phenylalanine (`PHE`).
### Step 2: The distance condition
The program applies the distance condition to find methionine-aromatic pairs that are _physically near each
other_. To do so, the program first finds the midpoints between all neighbouring aromatic carbon atoms in all
of tyrosine, tryptophan and phenylalanine. These midpoints are denoted using a `*`:
```
TYR: CD1*|CE1*|CZ*|CG*|CD2*|CE2*
TRP: CD2*|CE3*|CZ2*|CH2*|CZ3*|CE2*
PHE: CD1*|CE1*|CZ*|CG*|CD2*|CE2*
```
Next, the program finds all the vectors projecting from all methionine `SD` atoms to all the midpoints `*`. As
an example, a substructure consisting of one methionine and two phenylalanines would have 12 possible such
vectors, depicted here as $\vec{v}$, owing to the fact there can exist a total of six midpoints between
neighbouring atoms in a hexagonal arrangement of atoms and there are two such arrangements for two
phenylalanine residues.

To apply the distance condition, the program simply banks those methionine-aromatic pairs where one or more
vectors $\vec{v}$ are less than or equal to some cutoff $c$. As a motivating example, `CD1*` in `TYR` is the
midpoint between the `CD1` and `CE1` carbon atoms. A `CD1* / SD` on an aromatic / methionine pair would meet
the distance condition if the following held:

$$ \lVert \vec{v} \rVert = \sqrt{(CD1_x * -SD_x)^2 + (CD1_y * -SD_y)^2 + (CD1_z * -SD_z)^2} \leq c $$

### Step 3: The angular condition
Any methionine-aromatic pairs meeting the distance condition are subjected to the angular condition. The
angular condition can be loosely interpreted as _"find all the methionine-aromatic pairs where the methionine
lone pairs are pointing into or near the region(s) of highest electron density on a corresponding aromatic
moiety_." To apply the angular condition, two new vectors are introducted: vector $\vec{a}$ and vector
$\vec{g}$, which describe the orientation of the `SD` lone pairs in three dimensional space. To find the lone
pairs, the program considers the `SD` atom in a methionine atom to be the center of a regular tetrahedron with
vertices `CE` and `CG`. Solving for the position of the remaining two vertices yields vectors $\vec{a}$ and
$\vec{g}$. Next, the program obtains the angles between the lone pairs and $\vec{v}$:

$$
\theta = \cos^{-1}\left (\frac{\lVert \vec{a} \rVert \lVert \vec{v} \rVert}{\vec{a}\cdot\vec{v}} \right )
$$

$$
\phi = \cos^{-1}\left (\frac{\lVert \vec{g} \rVert \lVert \vec{v} \rVert}{\vec{g}\cdot\vec{v}} \right )
$$

Last, a methionine-aromatic pair is deemed interacting if any of $\theta$ or $\phi$ is less than or equal to
some cutoff angle $\delta$, that is, if:

$$
\theta \leq \delta \vee \phi \leq \delta
$$

holds.
### Summary
The end result is a dataset consisting of methionine-aromatic pairs whereby one or both of the methionine lone
pairs are pointing into or near the region of highest electron density on the corresponding aromatic residues.
A representative figure is shown below:

<p align="center">
  <img width="336" height="300" src=./pngs/pair-met18-tyr122.png>
</p>

## Setup
Simply run:
```
pip install MetAromatic
```
## Basic usage
### Finding Met-aromatic pairs
The easiest means of performing Met-aromatic calculations is to run jobs in a terminal session. The simplest
query follows:
```
runner pair 1rcy
```
Here, the `pair` argument specifies that we want to run a single aromatic interaction calculation. The query
will yield the following results:
```
-------------------------------------------------------------------
ARO        POS        MET POS    NORM       MET-THETA  MET-PHI
-------------------------------------------------------------------
TYR        122        18         4.211      75.766     64.317
TYR        122        18         3.954      60.145     68.352
TYR        122        18         4.051      47.198     85.151
TYR        122        18         4.39       53.4       95.487
TYR        122        18         4.62       68.452     90.771
TYR        122        18         4.537      78.568     76.406
PHE        54         148        4.777      105.947    143.022
PHE        54         148        4.61       93.382     156.922
PHE        54         148        4.756      93.287     154.63
-------------------------------------------------------------------
```
Above we have an order VI interaction between TYR 122 and MET 18, that is, all six vectors $\vec{v}$
projecting from the `SD` on MET 18 to the midpoints on TYR 122 meet Met-aromatic criteria. We also have an
order IV interaction between PHE 54 and MET 148. The `NORM` column specifies the actual distance (in
$\overset{\circ}{\mathrm {A}}$) between the MET residue and one of the midpoints between two carbon atoms in
an aromatic ring, or $\lVert v \rVert$. The default cutoff $c$ was applied in the above example, at 4.9
$\overset{\circ}{\mathrm {A}}$. The cutoff can be adjusted, however, using the `--cutoff-distance` option:
```
runner --cutoff-distance 4.0 pair 1rcy
```
Reducing the cutoff distance yields an order I interaction between TYR 122 and MET 18.
```
-------------------------------------------------------------------
ARO        POS        MET POS    NORM       MET-THETA  MET-PHI
-------------------------------------------------------------------
TYR        122        18         3.954      60.145     68.352
-------------------------------------------------------------------
```
`MET-THETA` and `MET-PHI` refer to $\theta$ and $\phi$, respectively. In the above example, the default cutoff
angle $\delta$ is used ( $109.5^\circ$ ). The cutoff angle can be adjusted by using the `--cutoff-angle`
option:
```
runner --cutoff-distance 4.5 --cutoff-angle 60 pair 1rcy
```
The `--cutoff-angle` option ensures that **at least one of** $\theta$ or $\phi$ angles fall below the cutoff
$\delta$. This is seen in the below order II interaction:
```
-------------------------------------------------------------------
ARO        POS        MET POS    NORM       MET-THETA  MET-PHI
-------------------------------------------------------------------
TYR        122        18         4.051      47.198     85.151
TYR        122        18         4.39       53.4       95.487
-------------------------------------------------------------------
```
The default lone pair interpolation model is `cp` or Cross Product (a thorough description is available in my
master's thesis: [Applications of numerical linear algebra to protein structural analysis: the case of
methionine-aromatic motifs](https://summit.sfu.ca/item/18741)). There exists another model, `rm` or Rodrigues
Method for predicting the positions of lone pairs. This model is based on the Rodrigues' Rotation Formula. The
model type can be passed as follows:
```
runner --cutoff-distance 4.5 --cutoff-angle 60 --model rm pair 1rcy
```
Which yields similar results:
```
-------------------------------------------------------------------
ARO        POS        MET POS    NORM       MET-THETA  MET-PHI
-------------------------------------------------------------------
TYR        122        18         3.954      57.237     64.226
TYR        122        18         4.051      45.097     80.768
TYR        122        18         4.39       52.505     91.841
-------------------------------------------------------------------
```
Note that the Euclidean distances between TYR aromatic carbon atoms and MET remain unchanged. By default, this
program searches for "A" delimited chains. Some researchers may, however, be interested in searching for
aromatic interactions in a different chain within a multichain protein. The `--chain` option can be used to
specify the chain:
```
runner --cutoff-distance 4.5 --cutoff-angle 60 --model rm --chain B pair 1rcy
```
In this case, no results are returned because the PDB entry 1rcy does not contain a "B" chain.
### Finding "bridging interactions"
Bridging interactions are interactions whereby two or more aromatic residues meet the criteria of the
Met-aromatic algorithm, for example, in the example below (PDB entry 6C8A):
<p align="center">
  <img width="399" height="300" src=./pngs/bridge-tyr-phe-6c8a.png>
</p>

We can specify a search for bridging interactions, instead of conventional aromatic interactions, using the
`bridge` argument. For example, to search for bridging interactions with a 7.0 $\overset{\circ}{\mathrm {A}}$
$\lVert v \rVert$ cutoff in 6LU7:
```
runner --cutoff-distance 7.0 bridge 6lu7
```
Which will return a list as follows:
```
-------------------------------------------------------------------
{MET264}-{PHE219}-{TYR209}
{MET276}-{TRP207}-{TRP218}
{PHE185}-{PHE181}-{MET165}
-------------------------------------------------------------------
```
Where each row corresponds to a bridge. This program treats bridging interactions as networks with a defined
set of vertices. For example, the above examples are 2-bridges with 3 vertices: ARO - MET - ARO. The
`--vertices` option can be passed to search for n-bridges:
```
runner --cutoff-distance 6.0 bridge 6lu7 --vertices 4
```
## Batch jobs and MongoDB integration
### A brief overview
This software is normally used for large scale Protein Data Bank mining efforts and stores the results in a
MongoDB database (https://www.mongodb.com/).  To start a batch job, ensure that the host is running a valid
MongoDB installation then supply a batch file. A batch file can be a regular text file consisting of delimited
PDB codes:
```
1xak, 1uw7, 2ca1
1qz8, 2fxp, 2fyg
2cme, 6mwm, spam
```
The command follows:
```
runner batch </path/batch/file> --threads <num-threads> --database <db> --collection <collection>
```
The MongoDB dump database is specified using the `--database` option. The collection is specified with the
`--collection` option. The `--threads` option specifies how many threads to use for processing the batch. The
recommended number of threads is 12 on a 300 Mbps network and on a machine that is idle.  By default, mining
jobs are run on `localhost` and on port `27017`. A "healthy" batch job will log as follows:
```
1970-01-01T00:00:00 MainThread I Handshaking with MongoDB at "mongodb://localhost:27017/"
1970-01-01T00:00:00 MainThread I Imported pdb codes from file /tmp/foo.txt
1970-01-01T00:00:00 Batch_0 I Getting Met-aromatic interactions for PDB entry 1xak
1970-01-01T00:00:00 Batch_1 I Getting Met-aromatic interactions for PDB entry 1uw7
1970-01-01T00:00:00 Batch_2 I Getting Met-aromatic interactions for PDB entry 2ca1
1970-01-01T00:00:00 Batch_0 E No methionine residues found for entry "1xak"
1970-01-01T00:00:00 Batch_0 I Processed 1xak. Count: 1
1970-01-01T00:00:00 Batch_0 I Getting Met-aromatic interactions for PDB entry 1qz8
1970-01-01T00:00:00 Batch_2 I Processed 2ca1. Count: 2
1970-01-01T00:00:00 Batch_2 I Getting Met-aromatic interactions for PDB entry 2fyg
1970-01-01T00:00:00 Batch_1 I Processed 1uw7. Count: 3
1970-01-01T00:00:00 Batch_1 I Getting Met-aromatic interactions for PDB entry 2fxp
1970-01-01T00:00:01 Batch_2 I Processed 2fyg. Count: 4
1970-01-01T00:00:01 Batch_2 I Getting Met-aromatic interactions for PDB entry 1rcy
1970-01-01T00:00:01 Batch_0 I Processed 1qz8. Count: 5
1970-01-01T00:00:01 Batch_0 I Getting Met-aromatic interactions for PDB entry 2cme
1970-01-01T00:00:01 Batch_1 E No methionine residues found for entry "2fxp"
1970-01-01T00:00:01 Batch_1 I Processed 2fxp. Count: 6
1970-01-01T00:00:01 Batch_1 I Getting Met-aromatic interactions for PDB entry 6mwm
1970-01-01T00:00:02 Batch_2 I Processed 1rcy. Count: 7
1970-01-01T00:00:02 Batch_0 E Found no Met-aromatic interactions for entry "2cme"
1970-01-01T00:00:02 Batch_0 I Processed 2cme. Count: 8
1970-01-01T00:00:02 Batch_1 E No aromatic residues found for entry "6mwm"
1970-01-01T00:00:02 Batch_1 I Processed 6mwm. Count: 9
1970-01-01T00:00:02 MainThread I Batch job complete!
1970-01-01T00:00:02 MainThread I Results loaded into database: default_ma
1970-01-01T00:00:02 MainThread I Results loaded into collection: default_ma
1970-01-01T00:00:02 MainThread I Batch job statistics loaded into collection: default_ma_info
1970-01-01T00:00:02 MainThread I Batch job execution time: 2.213000 s
```
A batch job will generate a collection secondary to the collection specified by `--collection`. This secondary
collection will house all the batch job parameters and other statistics and the collection name will be
suffixed with `_info`. For example, the above scenario would generate the `default_ma_info` collection:
```
{
        "_id" : ObjectId("6145d54c6f016f61e0afcaa5"),
        "num_workers" : 3,
        "cutoff_distance" : 4.9,
        "cutoff_angle" : 109.5,
        "chain" : "A",
        "model" : "cp",
        "data_acquisition_date" : ISODate("1970-01-01T00:00:02.077Z"),
        "batch_job_execution_time" : 2.213,
        "number_of_entries" : 9
}
```
### Designing a distributed mining strategy
A user may be tempted to mine data on a high performance machine and then route the results to a storage
server. This software supports this. As mentioned before, running a batch job will export data to a MongoDB
server listening on `localhost:27017` by default. However, the `--uri` option can be used to route results to
another server. The `--uri` option accepts a valid MongoDB URI string and overrides both the host and port
specified using the `--host` and `--port` options, respectively. For example, to run a batch job against a
MongoDB server listening on `localhost` and port 27018, one would pass:
```
runner batch --uri=mongodb://localhost:27018/ </path/to/batch.txt>
```
To run a batch job against a server `ma-results.local:27017`, with MongoDB user "abc" and password "password,"
one would pass:
```
runner batch --uri=mongodb://abc:password@ma-results.local:27017/ </path/to/batch.txt>
```
More information regarding valid URI connection string formats can be found at [Connection String URI Format —
MongoDB Manual](https://www.mongodb.com/docs/manual/reference/connection-string/).
## Using the MetAromatic API
One may be interested in extending the Met-aromatic project into a customized workflow. The instructions
provided in the [Setup](#setup) section install MetAromatic source into `site-packages`. Therefore, the API
can be exposed for use in a custom script.
### Example: programmatically obtaining Met-aromatic pairs
The command:
```
runner --cutoff-distance=4.1 pair 1rcy
```
Will return:
```
-------------------------------------------------------------------
ARO        POS        MET POS    NORM       MET-THETA  MET-PHI
-------------------------------------------------------------------
TYR        122        18         3.954      60.145     68.352
TYR        122        18         4.051      47.198     85.151
-------------------------------------------------------------------
```
To programmatically emulate this command, the following script applies:
```python3
from json import dumps
from MetAromatic import MetAromatic

def main() -> None:
    arguments = {
        'cutoff_distance': 4.1,
        'cutoff_angle': 109.5,
        'chain': 'A',
        'model': 'cp'
    }

    results = MetAromatic(**arguments).get_met_aromatic_interactions('1rcy')

    for interaction in results.interactions:
        print(dumps(interaction, indent=4))

if __name__ == '__main__':
    main()
```
Which will print to `stdout`:
```json
{
    "aromatic_residue": "TYR",
    "aromatic_position": 122,
    "methionine_position": 18,
    "norm": 3.954,
    "met_theta_angle": 60.145,
    "met_phi_angle": 68.352
}
{
    "aromatic_residue": "TYR",
    "aromatic_position": 122,
    "methionine_position": 18,
    "norm": 4.051,
    "met_theta_angle": 47.198,
    "met_phi_angle": 85.151
}
```
This output roughly matches that of the aforementioned `runner` invocation.
### Example: programmatically obtaining bridging interactions
The command:
```
runner bridge 6lu7
```
Will return:
```
-------------------------------------------------------------------
{PHE134}-{TYR182}-{MET130}
-------------------------------------------------------------------
```
To programmatically emulate this command, the following script applies:
```python3
from MetAromatic import GetBridgingInteractions

def main() -> None:
    arguments = {
        'cutoff_distance': 4.9,
        'cutoff_angle': 109.5,
        'chain': 'A',
        'model': 'cp'
    }

    results = GetBridgingInteractions(arguments).get_bridging_interactions('6lu7', 3)
    print(results.bridges[0])

if __name__ == '__main__':
    main()
```
Running this script will return:
```
{'MET130', 'PHE134', 'TYR182'}
```
Which roughly matches the output of the aforementioned `runner` invocation.
## Tests and automation
To test the program, run the following target:
```
make test
```
This target will run all unit tests within a `nox` generated virtual environment.
