AUTHOR:  
DAVID S. WEBER  
dsw7@sfu.ca  

 ** Example UI Layout **
![aa](https://github.com/dsw7/MetAromatic/blob/master/gui_example_v1_4.png)
  
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
  
  
**SOME LEGACY NOTES FROM SFU VAULT**    
 
  
NOTES:  
Known issues with operating Tcl/Tkinter on MacOSX platforms.  
Users will need to have third party ActiveTcl 8.5 installed  
for Python installations prior to v3.7 and MacOSX 10.6 or later.  
MacOSX distributable seems to work on every machine tested so far.  
MacOSX 10.8+ also has ActiveTcl 8.5 installed by default (I think)  
  
4beh is an example of a PDB entry that throws an exception. 4beh has  
the typical string formatting error: could not convert string to float: '67.440-104.578'  
which is basically a crashed string. I've had this problem... pretty much forever  
  
TODO:  
(1) Fix issue with uppercase PDB code string literals not equating to lowercase string literals   % DONE  
(2) RESULT records are not properly labelled - consider a short "header RESULT record"            % DONE *  
(3) Automate version number in main window title                                                  % DONE  
(4) Change 'src' label in MacOSX toolbar upon program start                                       % DONE  
(5) Deploy Windows binaries  
(6) Create proper save window (like I did in laser program)                                       % DONE  
(7) Throw in a proper exception handler for bad PDB codes                                         % DONE  
(8) Low level routine processes all entries in multimodel entries -> fix this                     % DONE  
    $%&* I had this bug before too....  
(9) Add dropdown menu for chains and structures  
(10) Redeploy for (8-11)  
(11) Fix issue with lowlevel AMET BMET separation                                                 % DONE  
  
* Added a button that prints a legend to console  
 
REFERENCES:  
// A great refresher on using virtualenv/py2app to deploy MacOSX standalones  
> https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/  
  
// info on errno 63 - an error which occurs when setup.py shares pwd with main script dependencies  
> https://stackoverflow.com/questions/7701255/py2app-ioerror-errno-63-file-name-too-long  
   
   
**END OF LEGACY NOTES**  


