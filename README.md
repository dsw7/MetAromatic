# Met-aromatic
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

Next we want to save the results of our batch job. Our results are stored using MongoDB. Data can be exported to a MongoDB database as follows:
```
$ python runner.py --code 1rcy --export-mongo
```
MongoDB export can be modified as follows:
```
$ python runner.py --code 1rcy --export-mongo --mongoport 27017 --mongohost localhost --database foobar --collection hamspam
```
Default MongoDB parameters are passed if no export parameters are specified. No data is saved if no export parameter is passed.
## The (optional) Tkinter user interface
The Tkinter user interface is basically the GUI version of `runner.py` with the `--code` parameter. There is one major difference however: data in the user interface can only be exported in the form of .txt/.csv. An image of the layout is shown below:
<img src="https://github.com/dsw7/MetAromatic/blob/master/frontend/images/gui_example_v19_90_labelled.png">    
Start the user interface as follows:
```
$ cd frontend/
$ python frontend.py
```
Then follow the instructions:
1. User must input a PDB code into **A**.  
2. User then selects the minimum distance between a methionine SD and an aromatic carbon atom (Phe, Tyr or Trp) that is deemed "interacting". This selection is made in edit box **B**. The vector has been termed vector v throughout literature. See **More information about cutoff distances and cutoff angles**.  
3. User selects the minimum cutoff angle between a methionine SD lone pair and vector v. Any lone pair / vector v combination is "deemed non-interacting". This selection is made in edit box **C**. See **More information about cutoff distances and cutoff angles**.  
4. The user can select which aromatic amino acids to include in the search in **D**.  
5. There are two models used for estimating the positions of lone pairs relative to the CG-SD-CE bonding frame in methionine. The radio buttons **E** and **F** allow for specifying these models. The "Cross product interpolation" generally provides a more accurate estimation.  
6. The "Go" button, **G**, executes the query by fetching the structure from the Protein Data Bank.  
7. The "Legend" button (**H**) can be used to print example output to the prompt (**K**) to help understand what the output data means. 
8. "Save data?" (**I**) does exactly as the name implies.  
9. "Exit" (**J**) does exactly as the name implies.  
10. The prompt (**K**) yields all the output data obtained from the Met-aromatic algorithm.  
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
$ cd tests/
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
