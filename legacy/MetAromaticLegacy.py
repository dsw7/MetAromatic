# Written by David Weber
# dsw7@sfu.ca

# dependencies
# ----------------------------------------------------------------------------
import tkinter as tk
from sys                    import path as PATH; PATH.append('./utilsLegacy')   # built in
from os                     import path, getcwd, remove                         # built in
from csv                    import DictWriter, writer, QUOTE_MINIMAL            # built in
from platform               import platform                                     # built in
from re                     import search                                       # built in
from time                   import time                                         # built in
from tkinter.scrolledtext   import ScrolledText                                 # built in
from tkinter                import messagebox, filedialog                       # built in
from ma_lowlevel            import met_aromatic                                 # local
from PDB_filegetter         import PDBFile                                      # local
from EC_classifier          import get_EC_classifier                            # local
from get_organism_from_file import get_organism                                 # local


# constants
# ----------------------------------------------------------------------------
CURR_VER = '1.4'
PLATFORM = platform()
HEIGHT_OVERALL = 455
WIDTH_OVERALL = 1000
STR_CODE = 'Enter a PDB code here (ex. 1rcy)'
STR_DIST = 'Enter a cutoff distance here (Angstroms) (ex. 4.9)'
STR_ANGL = 'Enter a cutoff angle here (degrees) (ex. 109.5)'
HEADER = ['RECORD', 'AROMATIC', 'ARO POS', 'MET', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
DICT_MODEL = {}
DICT_MODEL[1] = ('Cross product', 'cp')
DICT_MODEL[2] = ('Rodrigues method', 'rm')
ROUND_T = 1


# some helper functions
# ----------------------------------------------------------------------------
def write_to_csv(data, path, header):
   # writes data to .csv file
   # data -> the data we wish to write
   # path -> path to save location
   # header -> include header labelling all columns
    with open(path, mode='w', newline='') as f:
        obj_header = DictWriter(f, fieldnames=header)
        obj_header.writeheader()         
        obj_writer = writer(f, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
        for item in data:
            obj_writer.writerow(item)


# master window and downstream definitions
# ----------------------------------------------------------------------------
master = tk.Tk()
master.geometry('{}x{}'.format(WIDTH_OVERALL, HEIGHT_OVERALL))

# I'm trying my best to keep this project on one script regardless of OS
# there's a chance we may need two different scripts for each OS?
if 'Windows' in PLATFORM:
    master.iconbitmap('./icon.ico')
    FONT = ('Consolas', 9)
elif 'Darwin' in PLATFORM:
    FONT = ('Consolas', 12)
else:
    # keep stdin open until user prompts exit
    input('Unrecognized operating system. Press any button to exit.')
    exit()
    
master.winfo_toplevel().title('MetAromaticWrapper - dsw7@sfu.ca - v{}'.format(CURR_VER))
VAR_PHE = tk.IntVar()
VAR_TYR = tk.IntVar()
VAR_TRP = tk.IntVar()
VAR_MOD = tk.IntVar()

# set defaults
VAR_PHE.set(1)
VAR_TYR.set(1)
VAR_TRP.set(1)
VAR_MOD.set(1)


def get_pattern():
    get_d = {'PHE': VAR_PHE.get(), 'TYR': VAR_TYR.get(), 'TRP': VAR_TRP.get()}
    list_d = [j for j in ['PHE', 'TYR', 'TRP'] if get_d.get(j) == True]
    return '|'.join(list_d)
          


# add input and output frames
# ----------------------------------------------------------------------------
frame_input = tk.LabelFrame(master, relief=tk.GROOVE, bd=1)
frame_input.pack(side='left', fill='both', expand=True, padx=5, pady=5)
frame_output = tk.Frame(master, relief=tk.GROOVE, bd=1)
frame_output.pack(side='right', fill='both', expand=True, padx=5, pady=5)


# input window
# ----------------------------------------------------------------------------
frame_input.pack_propagate(False)  # fixes resize issue when loading widgets

# input pdb code
code_input = tk.Entry(frame_input, relief=tk.GROOVE, bd=1, font=FONT)
code_input.pack(fill='x', padx=5, pady=5)
code_input.insert(0, STR_CODE)

# input cutoff distance for distance condition
dist_input = tk.Entry(frame_input, relief=tk.GROOVE, bd=1, font=FONT)
dist_input.pack(fill='x', padx=5, pady=5)
dist_input.insert(0, STR_DIST)

# input cutoff angle for distance condition
angle_input = tk.Entry(frame_input, relief=tk.GROOVE, bd=1, font=FONT)
angle_input.pack(fill='x', padx=5, pady=5)
angle_input.insert(0, STR_ANGL)

# label for aromatic choices
label_aromatics = tk.Label(frame_input, text='Select aromatics to include in search:', font=FONT)
label_aromatics.pack(side='top', anchor='w', padx=2.5, pady=5)

# checkbuttons for aromatic residues
checkbutton_PHE = tk.Checkbutton(frame_input, text='Phenylalanine', variable=VAR_PHE, font=FONT)
checkbutton_PHE.pack(side='top', anchor='w')
checkbutton_TYR = tk.Checkbutton(frame_input, text='Tyrosine', variable=VAR_TYR, font=FONT)
checkbutton_TYR.pack(side='top', anchor='w')
checkbutton_TRP = tk.Checkbutton(frame_input, text='Tryptophan', variable=VAR_TRP, font=FONT)
checkbutton_TRP.pack(side='top', anchor='w')

# lone pair interpolation model radio buttons
label_angmodel = tk.Label(frame_input, text='Select a lone pair interpolation model:', font=FONT)
label_angmodel.pack(side='top', anchor='w', padx=2.5, pady=5)
tk.Radiobutton(frame_input, text='Cross product interpolation', font=FONT, indicatoron=0, 
               variable=VAR_MOD, value=1).pack(side='top', fill='x', padx=35, pady=5)
tk.Radiobutton(frame_input, text='Rodrigues method interpolation', font=FONT, indicatoron=0, 
               variable=VAR_MOD, value=2).pack(side='top', fill='x', padx=35, pady=5)



# get data from PDB / met aromatic algorithm
def pass_data_from_PDB_to_console(CODE, CHAIN, ANGLE, CUTOFF, METHOD):
    """
    Clicking on go button executes wrapper_over_data_passer() which is a wrapper
    over the function pass_data_from_PDB_to_console(). pass_data_from_PDB_to_console()
    is a function that wraps my pipeline for moving data from PDB and processing
    using the Met-aromatic algorithm.
    
    Go button -> wrapper_over_data_passer() -> pass_data_from_PDB_to_console()
    
    In general I dislike wrapper functions but occasionally they are necessary, for
    example for use with Tkinter's button press commands.
    """
    t_start = time()
    # get data from PDB
    file_PDB = PDBFile(CODE)
    path_to_file = file_PDB.fetch_from_PDB()
    
    # get all data from MA algorithm
    DATA = met_aromatic(filepath=path_to_file, CHAIN=CHAIN, CUTOFF=float(CUTOFF), ANGLE=float(ANGLE), MODEL=DICT_MODEL.get(METHOD)[1])

    # get EC classifier
    EC = get_EC_classifier(path_to_file)
    
    # attempt to find organism
    ORG = get_organism(path_to_file)
    
    # delete file from pwd
    file_PDB.clear()
    t_end = time()
    
    # print data to console
    text_output.insert(tk.END, 'UPDATE Successfully retrieved {}'.format(CODE) + '\n')
    text_output.insert(tk.END, 'UPDATE Processing time: {} s'.format(round(t_end - t_start, ROUND_T)) + '\n')
    text_output.insert(tk.END, 'RESULT EC classifier: {} \n'.format(EC))
    
    for org in ORG:
        text_output.insert(tk.END, 'RESULT Organism: {} \n'.format(org))
    for r in DATA:
        r_r = [str(round(i, 3)) for i in r[4:7]]
        str_out = ('RESULT ' + '{} '*7).format(*r[0:4], *r_r)
        pat = get_pattern()
        if bool(search(pat, str_out)) and pat != '':
            text_output.insert(tk.END, str_out + '\n')
        else:
            continue


def wrapper_over_data_passer():
    """
    A wrapper over my Met-aromatic pipeline implementation.
    """
    CODE_PDB = code_input.get().lower()
    DIST = dist_input.get()
    ANGLE = angle_input.get()
    METHOD = VAR_MOD.get()
    
    if CODE_PDB == STR_CODE:
        messagebox.showwarning('Warning', 'Input a PDB code!')
        return
    if DIST == STR_DIST:
        messagebox.showwarning('Warning', 'Input a cutoff distance!')
        return
    if ANGLE == STR_ANGL:
        messagebox.showwarning('Warning', 'Input a cutoff angle!')
        return
    
    text_output.delete('1.0', tk.END)
    text_output.insert(tk.END, 'HEADER Data for: {} \n'.format(CODE_PDB))
    text_output.insert(tk.END, 'HEADER Cutoff distance: {} Angstroms \n'.format(DIST))
    text_output.insert(tk.END, 'HEADER Cutoff angle: {} degrees \n'.format(ANGLE))
    pattern_aromatic = get_pattern()
    for p in pattern_aromatic.split('|'):
        text_output.insert(tk.END, 'HEADER {} included in this search \n'.format(p))     
    text_output.insert(tk.END, 'HEADER Interpolation method: {} \n'.format(DICT_MODEL.get(METHOD)[0]))
    
    try:
        pass_data_from_PDB_to_console(CODE=CODE_PDB, CHAIN='A', ANGLE=ANGLE, METHOD=METHOD, CUTOFF=DIST)
    except Exception as exception:
        text_output.insert(tk.END, 'UPDATE An exception has occurred! \n')
        text_output.insert(tk.END, 'UPDATE Here is the error: {}'.format(exception) + '\n')
        # file stays in pwd if an exception occurs - remove it
        get_path = path.join(getcwd(), 'pdb{}.ent'.format(CODE_PDB))
        if path.exists(get_path):
            remove(get_path)
        return
    else:
        text_output.insert(tk.END, 'END\n')


# go button       
go_input = tk.Button(frame_input, text='Go', font=FONT, command=wrapper_over_data_passer, bg='gray50')
go_input.pack(fill='x', padx=5, pady=(5, 1.5))

# display a legend showing what output means
def display_legend():
    text_output.insert(tk.END, 'UPDATE ' + '-' * 30 + '\n')
    text_output.insert(tk.END, 'UPDATE Here is a legend: \n')
    text_output.insert(tk.END, 'UPDATE TYR 122 MET 18 4.211 75.766 64.317  \n')
    text_output.insert(tk.END, 'UPDATE TYR -> The aromatic residue paired with MET \n')
    text_output.insert(tk.END, 'UPDATE 122 -> The position of the aromatic residue \n')
    text_output.insert(tk.END, 'UPDATE MET -> Methionine \n')
    text_output.insert(tk.END, 'UPDATE 18 -> The methionine position \n')
    text_output.insert(tk.END, 'UPDATE 4.211 -> The distance between MET SD and a midpoint (Angstroms) \n')
    text_output.insert(tk.END, 'UPDATE 75.766 -> Met-theta angle (degrees) \n')
    text_output.insert(tk.END, 'UPDATE 64.317 -> Met-phi angle (degrees) \n')
    text_output.insert(tk.END, 'UPDATE ' + '-' * 30 + '\n')


# print a legend button to console
handle_legend = tk.Button(frame_input, text='Legend', font=FONT, command=display_legend, bg='gray50')
handle_legend.pack(fill='x', padx=5, pady=1.5)


# save & exit stuff 
def output_save():
    DATA = text_output.get('1.0', tk.END)  # read from line '1', char '0'    
    spath = filedialog.asksaveasfilename(parent=frame_input, 
                                         title='Choose a save location', 
                                         filetypes=(('Text:', '*.txt'), ('CSV:', '*.csv')))   
                                    
    format_int = path.splitext(spath)[-1]   
    if format_int == '.txt':
    	 with open(spath, 'w') as f:
        	 f.write(DATA)         
    elif format_int == '.csv':
        DATA = DATA.split('\n')
        DATA = [i.split(' ') for i in DATA if 'RESULT' in i]
        write_to_csv(DATA, spath, HEADER)       
    else:  # exit if user does not select .txt or .csv as a file format
        text_output.insert(tk.END, 'Invalid file format. Valid formats: .csv, .txt\n')
        return
        
    text_output.insert(tk.END, 'UPDATE Data has been saved to: {}\n'.format(spath))  

# save button                                   
save_data = tk.Button(frame_input, text='Save data?', font=FONT, command=output_save, bg='gray50')
save_data.pack(fill='x', padx=5, pady=1.5)

# exit button
button_exit = tk.Button(frame_input, text="Exit", command=master.destroy, font=FONT, bg='gray50')
button_exit.pack(fill='x', padx=5, pady=1.5)


# output window
# ----------------------------------------------------------------------------
frame_output.pack_propagate(False)  # fixes resize issue when loading widgets
text_output = ScrolledText(frame_output, relief=tk.GROOVE, bd=1, font=FONT, bg='gray12', fg='yellow green')
text_output.pack(fill='both', expand=True, padx=5, pady=5)
text_output.insert(tk.END, '** Prompt **\n')
text_output.insert(tk.END, '** MetAromaticProgram - dsw7@sfu.ca - v{}'.format(CURR_VER) + ' ** \n')
text_output.insert(tk.END, '** Detected: {} **\n'.format(PLATFORM))
text_output.insert(tk.END, '** Results will display here **\n')


# main
# ----------------------------------------------------------------------------
tk.mainloop()
