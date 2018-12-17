## AUTHOR:  
DAVID S. WEBER  
dsw7@sfu.ca  
  
---
## Description  
An application wrapping the Met-aromatic algorithm such that biochemists  
do not have to manually run scripts using interpreters/DEs.  
  
---
## Instructions  
  
<img src="https://github.com/dsw7/MetAromatic/blob/master/gui_example_v1_4_labelled.png" class="center">     

1. User must input a PDB code into **A**.  
2. User then selects the minimum distance between a methionine SD and an aromatic carbon atom (Phe, Tyr or Trp) that is deemed "interacting". This selection is made in edit box **B**. The vector has been termed vector v throughout literature.  
3. User selects the minimum cutoff angle between a methionine SD lone pair and vector v. Any lone pair / vector v combination is "deemed non-interacting". This selection is made in edit box **C**.  
4. The user can select which aromatic amino acids to include in the search in **D**.  
5. There are two models used for estimating the positions of lone pairs relative to the CG-SD-CE bonding frame in methionine. The ratio buttons **E** and **F** allow for specifying these models. The "Cross product interpolation" generally provides a more accurate estimation.  
6. The "Go" button, **G**, executes the query by fetching the structure from the Protein Data Bank.  
7. The "Legend" button (**H**) can be used to print example output to the prompt (**K**) to help understand what the output data means.  
8. "Save data?" (**I**) does exactly as the name implies.  
9. "Exit" (**J**) does exactly as the name implies.  
10. The prompt (**K**) yields all the output data obtained from the Met-aromatic algorithm.  

## More information about cutoff distances and cutoff angles  

The following figure provides an excellent overview of the geometry of the system being probed by Met-aromatic. We have a vector **v** in our figure below. **v** points from the methionine SD coordinate to a midpoint between two aromatic carbon atoms. _Distance condition_. Methionine / aromatic residue pairs are saved for further analysis if the vector **v** between the two is of magnitude ≤ to the value inputted in **B**. _Angular condition_. We also have two vectors, **a** and **g**. These vectors estimate the position and direction of the lone pairs of the sulfur atom. Here, an interaction is printed to the prompt **if** either the **a** / **v** angle **or** the **g** / **v** angle is ≤ the value inputted into edit box **C**.    
  
<img src="https://github.com/dsw7/MetAromatic/blob/master/cd_schematic_chapter2.png" width="500" class="center">  

---
## Description of directories  

    ~/MetAromatic/docs                          // contains deploy instructions + other supporting info  
    ~/MetAromatic/MetAromatic.py                // the "main" file - this runs the Tkinter master  
    ~/MetAromatic/setup.py                      // a custom setup.py file for py2app  
    ~/MetAromatic/icon_gaJ_icon.ico             // a custom .ico icon if I ever decide to make a Windows of app
    ~/MetAromatic/gui_example_v1_4_labelled.png // example UI layout .png for v1.4  
    ~/MetAromatic/dependencies                  // all dependency scripts are located here  
  
    ->
  
    ~/dependencies/PDB_filegetter.py         // connects to RCSB PDB and fetches a PDB file  
    ~/dependencies/EC_classifier.py          // tries to get EC classifier from a local PDB file  
    ~/dependencies/get_organism_from_file.py // attempts to find protein's host organism  
    ~/dependencies/ma_lowlevel.py            // a raw implementation of the Met-aromatic algorithm  
    ~/dependencies/methods.py                // some linear algebraic methods for computing lone pair positions  
   
## TODO:  
--- 
1. Consider refactoring met_aromatic() in ~/dependencies/ma_lowlevel.py in the future?  
  
---  
## Legacy notes from SFU Vault  
  
**NOTES:**  
Known issues with operating Tcl/Tkinter on MacOSX platforms.  
Users will need to have third party ActiveTcl 8.5 installed  
for Python installations prior to v3.7 and MacOSX 10.6 or later.  
MacOSX distributable seems to work on every machine tested so far.  
MacOSX 10.8+ also has ActiveTcl 8.5 installed by default (I think)  
  
4beh is an example of a PDB entry that throws an exception. 4beh has  
the typical string formatting error: could not convert string to float: '67.440-104.578'  
which is basically a crashed string. I've had this problem... pretty much forever  
  
**TODO:**   
1. Fix issue with uppercase PDB code string literals not equating to lowercase string literals   % DONE  
2. RESULT records are not properly labelled - consider a short "header RESULT record"            % DONE *  
3. Automate version number in main window title                                                  % DONE  
4. Change 'src' label in MacOSX toolbar upon program start                                       % DONE  
5. Deploy Windows binaries  
6. Create proper save window (like I did in laser program)                                       % DONE  
7. Throw in a proper exception handler for bad PDB codes                                         % DONE  
8. Low level routine processes all entries in multimodel entries -> fix this                     % DONE  
    $%&* I had this bug before too....  
9. Add dropdown menu for chains and structures  
10. Redeploy for (8-11)  
11. Fix issue with lowlevel AMET BMET separation                                                 % DONE  
  
**REFERENCES:**  
A great refresher on using virtualenv/py2app to deploy MacOSX standalones  
https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/  
  
Info on errno 63 - an error which occurs when setup.py shares pwd with main script dependencies  
https://stackoverflow.com/questions/7701255/py2app-ioerror-errno-63-file-name-too-long  
   



