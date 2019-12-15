## Met-aromatic
Code for the following publications:  
* Weber, D. S.; Warren, J. J. The Interaction between Methionine and Two Aromatic Amino Acids Is an Abundant and Multifunctional Motif in Proteins. _Arch. Biochem. Biophys._ **2019**, _672_, 108053.  
* Weber, D. S.; Warren, J. J. A Survey of Methionine-Aromatic Interaction Geometries in the Oxidoreductase Class of Enzymes: What Could Met-Aromatic Interactions be Doing Near Metal Sites? _J. Inorg. Biochem._ **2018**, _186_, 34-41.  
## Synopsis
The majority of the driver code is located in the ```metaromatic/``` directory. A simple Tkinter GUI is available for staff who prefer to use user interfaces and is located under ```frontend/```. Unit tests are located in the ```tests/``` directory.
## Running Met-aromatic jobs in the terminal
The easiest method of performing Met-aromatic calculations is to run jobs in the terminal. First, change directories:
```
$ cd metaromatic/
```
The `runner.py` file is the bridge between the user and the program's internals. Access the help menu to see a list of options:
```
$ python runner.py -h
```
A valid PDB code is passed to the runner to get a list of closely spaced methionine-aromatic residues in a PDB structure. Here the arbitrary PDB code 1rcy is analyzed:
```
$ python runner.py --code 1rcy
```
This will not print the results to the terminal. The results must be accessed by passing the verbosity flag:
```
$ python runner.py --code 1rcy --verbose
```
The verbose flag forces the program to print the results in a nicely formatted Pandas DataFrame. We are ultimately interested in running batch jobs however. To do so, the batch argument is passed with a path to a text file containing a list of PDB codes:
```
$ python runner.py --batch /path/to/delimiter.txt
```
The PDB codes in the batch job text file should be separated by newline characters. *NOTE:* Both code and batch parameters cannot be passed simultaneously. Next come the Met-aromatic algorithm constraints:
```
$ python runner.py --code 1rcy --cutoff 4.9 --angle 90.0 --model cp
```
Here the cutoff has been set to 4.9 Angstroms (the max norm of vector *v*) and the maximum angle of either Met-theta or Met-phi cannot exceed 90.0 degrees. The model used to interpolate lone pair positions is cp or Cross Product. These parameters do not have to be passed. Default values are used if these values are not specified. Defaults can also be obtained in the help menu.

Data can be exported to a MongoDB database as follows:
```
$ python runner.py --code 1rcy --export-mongo
```
MongoDB export can be modified as follows:
```
$ python runner.py --code 1rcy --export-mongo --mongoport 27017 --mongohost localhost --database foobar --collection hamspam
```
Default MongoDB parameters are passed if no export parameters are specified. No data is saved if no export parameter is passed.

### Usage: dispatcher.py
This script packages the engine into a directory onto the host machine's desktop. Usage follows:
```
$ python dispatcher.py
```
