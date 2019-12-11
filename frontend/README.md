## AUTHOR:  
DAVID S. WEBER  
dsw7@sfu.ca  

---
## Description  
An application wrapping the Met-aromatic algorithm such that biochemists  
do not have to manually run scripts using interpreters/DEs.  

---
## Instructions  
<img src="https://github.com/dsw7/MetAromaticEngine/blob/master/frontend/images/gui_example_v19_90_labelled.png">    

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

## More information about cutoff distances and cutoff angles  
The following figure provides an excellent overview of the geometry of the system being probed by Met-aromatic. We have a vector **v** in our figure below. **v** points from the methionine SD coordinate to a midpoint between two aromatic carbon atoms. _Distance condition_. Methionine / aromatic residue pairs are saved for further analysis if the vector **v** between the two is of magnitude ≤ to the value inputted in **B**. _Angular condition_. We also have two vectors, **a** and **g**. These vectors estimate the position and direction of the lone pairs of the sulfur atom. Here, an interaction is printed to the prompt **if** either the **a** / **v** angle **or** the **g** / **v** angle is ≤ the value inputted into edit box **C**.    
<img src="https://github.com/dsw7/MetAromaticEngine/blob/master/frontend/images/cd_schematic_chapter2.png" width="400">  

---  
## Interpreting the results  
The protein 1rcy was analyzed using the MetAromatic application. Here we set ||**v**|| ≤ 4.9 Angstroms and the cutoff angle ≤ 109.5 degrees. The results are as follows:  

<img src="https://github.com/dsw7/MetAromaticEngine/blob/master/frontend/images/results_1rcy_v19_90.png">  
  
Consider the last three RESULT lines:  
    
    #                     ||v|| Met-theta Met-phi
    RESULT PHE 54 MET 148 4.777 105.947 143.022  
    RESULT PHE 54 MET 148 4.610 93.3820 156.922  
    RESULT PHE 54 MET 148 4.756 93.2870 154.630  

Here the SD on MET 148 is ≤ 4.9 Angstroms of a total of three of six midpoints on the PHE 54 aromatic ring. The angle between 3 vectors **v** and the two SD lone pairs is ≤ 109.5 degrees in three cases.  

---  
## Running the program
Simply run:
```
$ python MetAromatic.py
```
## Generating binaries (deprecated)
Simply run:
```
$ python dispatcher.py
```
This script will package the program into a standalone executable file. The executable
file will be located inside the _dist_ folder which will be placed onto the host machine's
Desktop. A _build_ folder will also be generated. This folder can be discarded.