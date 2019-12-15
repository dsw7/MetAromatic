## Met-aromatic
Code for the following publications:  
* Weber, D. S.; Warren, J. J. The Interaction between Methionine and Two Aromatic Amino Acids Is an Abundant and Multifunctional Motif in Proteins. _Arch. Biochem. Biophys._ **2019**, _672_, 108053.  
* Weber, D. S.; Warren, J. J. A Survey of Methionine-Aromatic Interaction Geometries in the Oxidoreductase Class of Enzymes: What Could Met-Aromatic Interactions be Doing Near Metal Sites? _J. Inorg. Biochem._ **2018**, _186_, 34-41.  
## Synopsis
The majority of the driver code is located in the ```metaromatic/``` directory. A simple Tkinter GUI is available for staff who prefer to use user interfaces and is located under ```frontend/```. Unit tests are located in the ```tests/``` directory.



---  
A low level object oriented package for running the Met-aromatic algorithm. See DSW thesis for a theoretical description.

### Contents
```
./runner.py                              -- Runs MetAromatic algorithm over cmd
./engine/                                -- Contains all core code
./tests/                                 -- Unit tests executed here
./dispatcher.py                          -- Exports engine directory to standalone directory
./versionhandler.py                      -- Script for versioning the package
./version.py                             -- Version file
```

### Usage: runner.py
---
To run the program:
```
$ python runner.py <args>
```
The program requires, at bare minimum, either a valid PDB code or a path to a text file containing a list of PDB codes to analyze. Here the arbitrary PDB code 1rcy is analyzed:
```
$ python runner.py --code 1rcy
```
A batch job can be performed as follows:
```
$ python runner.py --batch /path/to/delimiter.txt
```
The PDB codes in the batch job text file should be separated by newline characters. *NOTE:* Both code and batch parameters cannot be passed simultaneously. Next come the Met-aromatic algorithm constraints:
```
$ python runner.py --code 1rcy --cutoff 4.9 --angle 90.0 --model cp
```
Here the cutoff has been set to 4.9 Angstroms (the max norm of vector *v*) and the maximum angle of either Met-theta or Met-phi cannot exceed 90.0 degrees. The model used to interpolate lone pair positions is cp or Cross Product. These parameters do not have to be passed. Default values are used if these values are not specified. Defaults can be obtained by reading:
```
$ python runner.py --help
```
Console output is normally suppressed. Suppression can be lifted by passing the verbose parameter:
```
$ python runner.py --code 1rcy --verbose
```
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
