# Met-aromatic
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Code for the following publications:
* Weber, D. S.; Warren, J. J. The Interaction between Methionine and Two Aromatic Amino Acids Is an Abundant
  and Multifunctional Motif in Proteins. _Arch. Biochem. Biophys._ **2019**, _672_, 108053.
* Weber, D. S.; Warren, J. J. A Survey of Methionine-Aromatic Interaction Geometries in the Oxidoreductase
  Class of Enzymes: What Could Met-Aromatic Interactions be Doing Near Metal Sites? _J. Inorg. Biochem._
**2018**, _186_, 34-41.
## Table of Contents
- [Synopsis](#synopsis)
- [Setup](#setup)
- [How it works](#how-it-works)
  - [Step 1: Data preprocessing](#step-1-data-preprocessing)
  - [Step 2: The distance condition](#step-2-the-distance-condition)
  - [Step 3: The angular condition](#step-3-the-angular-condition)
  - [Summary](#summary)
- [Finding Met-aromatic pairs](#finding-met-aromatic-pairs)
- [Finding "bridging interactions"](#finding-bridging-interactions)
- [Running jobs and MongoDB integration](#running-batch-jobs-and-mongodb-integration)
- [Using the MetAromatic API](#using-the-metaromatic-api)
  - [Example: programmatically obtaining Met-aromatic pairs](#example-programmatically-obtaining-met-aromatic-pairs)
  - [Example: programmatically obtaining bridging interactions](#example-programmatically-obtaining-bridging-interactions)

## Synopsis
This program returns a list of closely spaced methionine-aromatic residue pairs for structures in the [Protein
Data Bank](https://www.rcsb.org/) (PDB). The program supports running queries on single PDB entries or large
scale multithreaded batch jobs consisting of hundreds of thousands of queries.

## Setup
Simply run:
```console
pip install MetAromatic
```

## How it works
> [!NOTE]
> See my master's thesis [^1] for a more indepth discussion surrounding the "Met-aromatic" algorithm.
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

## Finding Met-aromatic pairs
The easiest means of performing Met-aromatic calculations is to run jobs in a terminal session. The simplest
query follows:
```console
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
```console
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
```console
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
master's thesis. [^1] There exists another model, `rm` or Rodrigues Method for predicting the positions of
lone pairs. This model is based on the Rodrigues' Rotation Formula. The model type can be passed as follows:
```console
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
```console
runner --cutoff-distance 4.5 --cutoff-angle 60 --model rm --chain B pair 1rcy
```
In this case, no results are returned because the PDB entry 1rcy does not contain a "B" chain.

## Finding "bridging interactions"
Bridging interactions are interactions whereby two or more aromatic residues meet the criteria of the
Met-aromatic algorithm, for example, in the example below (PDB entry 6C8A):
<p align="center">
  <img width="399" height="300" src=./pngs/bridge-tyr-phe-6c8a.png>
</p>

We can specify a search for bridging interactions, instead of conventional aromatic interactions, using the
`bridge` argument. For example, to search for bridging interactions with a 7.0 $\overset{\circ}{\mathrm {A}}$
$\lVert v \rVert$ cutoff in 6LU7:
```console
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
```console
runner --cutoff-distance 6.0 bridge 6lu7 --vertices 4
```

## Running batch jobs and MongoDB integration
> [!NOTE]
> This section assumes a host is running MongoDB [^2] and familiarity with the MongoDB suite of products.

This software is normally used for large scale Protein Data Bank mining efforts and stores the results in a
MongoDB database. To get started, prepare a batch file of PDB codes to scan. A batch file can be a regular
text file consisting of delimited PDB codes:
```
1xak, 1uw7, 2ca1, 1qz8, 2fxp, 2fyg, 2cme, 6mwm, spam
```
Then run:
```console
runner batch </path/batch/file> --threads <num-threads> --database <db> --collection <collection>
```
The MongoDB database name is specified using the `--database` option and the collection name is specified with
the `--collection` option. The `--threads` option specifies how many threads to use for processing the batch.
The hostname of the server hosting the MongoDB deployment can be provided using the `--host` option if the
MongoDB deployment is not bound to localhost.

> [!IMPORTANT]
> The program assumes that authentication is enabled and will prompt for a username and password.

If no issues arise when connecting to MongoDB, the batch job will proceed. Below is an example of output
corresponding to the above 9 codes:
```
... MainThread INFO Importing pdb codes from file /tmp/foo.txt
... MainThread INFO Splitting list of PDB codes into 3 chunks
... MainThread INFO Deploying 3 workers!
... MainThread INFO Registering SIGINT to thread terminator
... Batch_0 INFO Processing 1xak. Count: 1
... Batch_1 INFO Processing 1uw7. Count: 2
... Batch_2 INFO Processing 2ca1. Count: 3
... Batch_0 INFO Processing 1qz8. Count: 4
... Batch_1 INFO Processing 2fxp. Count: 5
... Batch_2 INFO Processing 2fyg. Count: 6
... Batch_0 INFO Processing 2cme. Count: 7
... Batch_2 INFO Processing spam. Count: 8
... Batch_1 INFO Processing 6mwm. Count: 9
... MainThread INFO Batch job complete!
... MainThread INFO Results loaded into database: test
... MainThread INFO Results loaded into collection: test
... MainThread INFO Batch job execution time: 1.746000 s
... MainThread INFO Loading:
{
    "batch_job_execution_time": 1.746,
    "data_acquisition_date": "...", // date truncated for clarity
    "num_workers": 3,
    "number_of_entries": 9,
    "chain": "A",
    "cutoff_angle": 109.5,
    "cutoff_distance": 4.9,
    "model": "cp"
}
Into collection: test_info
... MainThread INFO Unregistering SIGINT from thread terminator
```
And deployed with the command:
```console
runner batch /tmp/foo.txt --threads 3 --database test --collection test
# Where foo.txt contains: 1xak, 1uw7, 2ca1, 1qz8, 2fxp, 2fyg, 2cme, 6mwm, spam
```
A batch job will generate a collection secondary to the collection specified by `--collection`. This secondary
collection will house all the batch job parameters and other statistics and the collection name will be
suffixed with `_info`. Note that the above command generated:
```javascript
{
    "batch_job_execution_time": 1.746,
    "data_acquisition_date": "...", // date truncated for clarity
    "num_workers": 3,
    "number_of_entries": 9,
    "chain": "A",
    "cutoff_angle": 109.5,
    "cutoff_distance": 4.9,
    "model": "cp"
}
```

## Using the MetAromatic API
One may be interested in extending the Met-aromatic project into a customized workflow. The instructions
provided in the [Setup](#setup) section install MetAromatic source into `site-packages`. Therefore, the API
can be exposed for use in a custom script.
### Example: programmatically obtaining Met-aromatic pairs
The command:
```console
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
The following snippet approximates the above output:
```python3
from json import dumps
from MetAromatic import get_pairs_from_pdb


def main() -> None:
    results = get_pairs_from_pdb(
        cutoff_distance=4.1, cutoff_angle=109.5, chain="A", model="cp", pdb_code="1rcy"
    )

    for interaction in results.interactions:
        print(dumps(interaction.to_dict(), indent=4))


if __name__ == "__main__":
    main()
```
Which will print to `stdout`:
```json
{
    "aromatic_position": 122,
    "aromatic_residue": "TYR",
    "met_phi_angle": 68.352,
    "met_theta_angle": 60.145,
    "methionine_position": 18,
    "norm": 3.954
}
{
    "aromatic_position": 122,
    "aromatic_residue": "TYR",
    "met_phi_angle": 85.151,
    "met_theta_angle": 47.198,
    "methionine_position": 18,
    "norm": 4.051
}
```

### Example: programmatically obtaining bridging interactions
The command:
```console
runner bridge 6lu7
```
Will return:
```
-------------------------------------------------------------------
{PHE134}-{TYR182}-{MET130}
-------------------------------------------------------------------
```
The following snippet approximates the above output:
```python3
from MetAromatic import get_bridges


def main() -> None:
    results = get_bridges(
        chain="A",
        code="6lu7",
        cutoff_angle=109.5,
        cutoff_distance=4.9,
        model="cp",
        vertices=3,
    )

    for bridge in results.bridges:
        print(bridge)


if __name__ == "__main__":
    main()
```
Running this script will print:
```
{'MET130', 'PHE134', 'TYR182'}
```

<!-- footnotes will always be placed at the bottom of a markdown file so place here -->

[^1]: See [Applications of numerical linear algebra to protein structural analysis: the case of
methionine-aromatic motifs](https://summit.sfu.ca/item/18741)).
[^2]: See [MongoDB](https://www.mongodb.com/) for more information.
