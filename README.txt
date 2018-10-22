AUTHOR:
DAVID S. WEBER
dsw7@sfu.ca


~/MetAromatic/docs              // contains deploy instructions + other supporting info
~/MetAromatic/MetAromatic.py    // the "main" file - this runs the Tkinter master
~/MetAromatic/setup.py          // a custom setup.py file for py2app
~/MetAromatic/icon_gaJ_icon.ico // a custom .ico icon if I ever decide to make a Windows implementation of MetAromatic
~/MetAromatic/dependencies      // all dependency scripts are located here

->

~/dependencies/PDB_filegetter.py         // connects to RCSB PDB and fetches a PDB file
~/dependencies/EC_classifier.py          // tries to get EC classifier from a local PDB file
~/dependencies/get_organism_from_file.py // attempts to find protein's host organism
~/dependencies/ma_lowlevel.py            // a raw implementation of the Met-aromatic algorithm
~/dependencies/methods.py                // some linear algebraic methods for computing lone pair positions

TODO:
(1) Consider refactoring met_aromatic() in ~/dependencies/ma_lowlevel.py in the future?
