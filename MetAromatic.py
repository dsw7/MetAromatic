# Written by David Weber
# dsw7@sfu.ca

# dependencies
# ----------------------------------------------------------------------------
import tkinter as tk
from sys                    import path as PATH; PATH.append('./utils')  # built in
from os                     import path, getcwd, remove                  # built in
from csv                    import DictWriter, writer, QUOTE_MINIMAL     # built in
from platform               import platform                              # built in
from time                   import time                                  # built in
from tkinter.scrolledtext   import ScrolledText                          # built in
from tkinter                import messagebox, filedialog                # built in
from ma                     import MetAromatic                           # local
from get_commit_count       import get_commit_count                      # local
from traceback              import format_exc                            # built in
from argparse               import ArgumentParser                        # built in


# top level setup
# ----------------------------------------------------------------------------
master = tk.Tk()


# constants
# ----------------------------------------------------------------------------
CURR_VER = get_commit_count()
PLATFORM = platform()
HEIGHT_OVERALL = 470
WIDTH_OVERALL = 1300
STR_CODE = 'Enter a PDB code here (ex. 1rcy)'
STR_DIST = 'Enter a cutoff distance here (Angstroms) (ex. 4.9)'
STR_ANGL = 'Enter a cutoff angle here (degrees) (ex. 109.5)'
HEADER = ['RECORD', 'AROMATIC', 'ARO POS', 'MET', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
DICT_MODEL = {}
DICT_MODEL[1] = ('Cross product', 'cp')
DICT_MODEL[2] = ('Rodrigues', 'rm')
CHAIN = 'A'
FONT = ('Consolas', 9)
FILETYPES = (('Text:', '*.txt'), ('CSV:', '*.csv'))
CP_INT = 'Cross product interpolation'
RM_INT = 'Rodrigues method interpolation'
BUILD = 'MetAromaticWrapper - dsw7@sfu.ca - v1.{}'.format(CURR_VER)

VAR_PHE = tk.IntVar()
VAR_TYR = tk.IntVar()
VAR_TRP = tk.IntVar()
VAR_MOD = tk.IntVar()

VAR_PHE.set(1)
VAR_TYR.set(1)
VAR_TRP.set(1)
VAR_MOD.set(1)


# CLI args
# ----------------------------------------------------------------------------
# pass cmd args for displaying full traceback for debugging purposes
# this is important for debugging string crashes, AMET/MET, etc.
parser = ArgumentParser()
parser.add_argument('--debug', default=False, action='store_true')
debug = parser.parse_args().debug


# helper functions
# ----------------------------------------------------------------------------
def get_aromatic_pattern(var_phe={}, var_tyr={}, var_trp={}):
    # function needed for getting PHE, TYR, TRP pattern from checkboxes
    dict_aromatics = {
        'PHE': var_phe.get(), 
        'TYR': var_tyr.get(), 
        'TRP': var_trp.get()
    }
    list_aromatics = [d for d in ['PHE', 'TYR', 'TRP'] if dict_aromatics.get(d) == True]
    return '|'.join(list_aromatics)


def display_legend():
    # display a legend showing what output means
    text_output.delete('1.0', tk.END)
    text_output.insert(tk.END, 'UPDATE ' + '-' * 30 + '\n')
    text_output.insert(tk.END, 'UPDATE Here is a legend: \n')
    text_output.insert(tk.END, 'UPDATE TYR 122 MET 18 4.211 75.766 64.317  \n')
    text_output.insert(tk.END, 'UPDATE TYR    -> The aromatic residue paired with MET \n')
    text_output.insert(tk.END, 'UPDATE 122    -> The position of the aromatic residue \n')
    text_output.insert(tk.END, 'UPDATE MET    -> Methionine \n')
    text_output.insert(tk.END, 'UPDATE 18     -> The methionine position \n')
    text_output.insert(tk.END, 'UPDATE 4.211  -> The distance between MET SD and a midpoint (Angstroms) \n')
    text_output.insert(tk.END, 'UPDATE 75.766 -> Met-theta angle (degrees) \n')
    text_output.insert(tk.END, 'UPDATE 64.317 -> Met-phi angle (degrees) \n')
    text_output.insert(tk.END, 'UPDATE ' + '-' * 30 + '\n')


def print_header(pdbcode, distance, angle, method):
    # print a basic header into terminal
    pattern = get_aromatic_pattern(var_phe=VAR_PHE, var_tyr=VAR_TYR, var_trp=VAR_TRP)
    text_output.insert(tk.END, 'HEADER Data for: {} \n'.format(pdbcode))
    text_output.insert(tk.END, 'HEADER Cutoff distance: {} Angstroms \n'.format(distance))
    text_output.insert(tk.END, 'HEADER Cutoff angle: {} degrees \n'.format(angle))
    for p in pattern.split('|'):
        text_output.insert(tk.END, 'HEADER {} included in this search \n'.format(p))     
    text_output.insert(tk.END, 'HEADER Interpolation method: {} \n'.format(method))
    

def print_raw_data(pdbcode, data):
    # print data directly from Met-aromatic algorithm results to terminal
    pattern = get_aromatic_pattern(var_phe=VAR_PHE, var_tyr=VAR_TYR, var_trp=VAR_TRP)
    text_output.insert(tk.END, 'UPDATE Successfully retrieved {}'.format(pdbcode) + '\n')
    for row in data:
        if row[0] in pattern:
            rounded_row = [str(round(i, 3)) for i in row[4:7]]
            str_out = ('RESULT ' + '{} '*7).format(*row[0:4], *rounded_row)
            text_output.insert(tk.END, str_out + '\n')
        else:
            continue


def print_main():
    # print header + Met-aromatic output to terminal
    pdbcode = code_input.get().lower()
    distance = dist_input.get()
    angle = angle_input.get()
    method = VAR_MOD.get()
    
    if pdbcode == STR_CODE.lower():
        messagebox.showwarning('Warning', 'Input a PDB code!'); return
    if distance == STR_DIST:
        messagebox.showwarning('Warning', 'Input a cutoff distance!'); return
    if angle == STR_ANGL:
        messagebox.showwarning('Warning', 'Input a cutoff angle!'); return
        
    # clear terminal for every query
    text_output.delete('1.0', tk.END)    
        
    try:
        model = DICT_MODEL.get(method)[1]
        t_start = time()
        data = MetAromatic(
                code=pdbcode, chain=CHAIN, cutoff=float(distance),
                angle=float(angle), model=model
        ).met_aromatic()
        print_header(pdbcode=pdbcode, distance=distance, angle=angle, method=model)
        text_output.insert(tk.END, 'UPDATE Total execution time: {} s\n'.format(time() - t_start))
        print_raw_data(pdbcode=pdbcode, data=data)
    except Exception as exception:
        text_output.insert(tk.END, 'ERROR An exception has occurred: \n')
        if debug:
            tb = format_exc()
            text_output.insert(tk.END, '{}\n'.format(tb))
        else:
            text_output.insert(tk.END, '{}\n'.format(exception))
    else:
        text_output.insert(tk.END, 'END\n')
        

def write_to_csv(data, path, header):
    with open(path, mode='w', newline='') as f:
        obj_header = DictWriter(f, fieldnames=header)
        obj_header.writeheader()         
        obj_writer = writer(f, delimiter=',', quotechar='"', quoting=QUOTE_MINIMAL)
        for item in data:
            obj_writer.writerow(item)
            

def write_to_txt(data, path):
    with open(path, 'w') as f:
        f.write(data)


def output_save():
    # saves data from terminal into a .txt or .csv file
    data = text_output.get('1.0', tk.END)  # read from line '1', char '0'    
    spath = filedialog.asksaveasfilename(parent=frame_go, title='Choose a save location', filetypes=FILETYPES)   
    extension = path.splitext(spath)[-1]
    
    if extension == '.txt':
        write_to_txt(data, spath)     
    elif extension == '.csv':
        data = [i.split(' ') for i in data.split('\n') if 'RESULT' in i]
        write_to_csv(data, spath, HEADER)       
    else:
        text_output.insert(tk.END, 'ERROR Invalid file format. Valid formats: .csv, .txt\n'); return
        
    text_output.insert(tk.END, 'UPDATE Data has been saved to: {}\n'.format(spath))  
    
    
# master panel setup
# ----------------------------------------------------------------------------
master.iconbitmap('./img/icon_gaJ_icon.ico')
master.geometry('{}x{}'.format(WIDTH_OVERALL, HEIGHT_OVERALL))
master.winfo_toplevel().title(BUILD)


# set up all frames
# ----------------------------------------------------------------------------
frame_input = tk.LabelFrame(master, relief=tk.GROOVE, bd=1, text='Input', font=FONT)
frame_input.pack(side='left', fill='both', expand=True, padx=5, pady=5)

frame_output = tk.LabelFrame(master, relief=tk.GROOVE, bd=1, text='Output', font=FONT)
frame_output.pack(side='right', fill='both', expand=True, padx=5, pady=5)

frame_pdb_code = tk.LabelFrame(frame_input, relief=tk.GROOVE, bd=1, text='Enter search conditions', font=FONT)
frame_pdb_code.pack(side='top', fill='both', expand=True, padx=5, pady=5)

frame_aromatics = tk.LabelFrame(frame_input, relief=tk.GROOVE, bd=1, text='Select aromatics', font=FONT)
frame_aromatics.pack(side='top', fill='both', expand=True, padx=5, pady=5)

frame_model = tk.LabelFrame(frame_input, relief=tk.GROOVE, bd=1, text='Select model', font=FONT)
frame_model.pack(side='top', fill='both', expand=True, padx=5, pady=5)

frame_go = tk.Frame(frame_input, relief=tk.GROOVE, bd=1)
frame_go.pack(side='top', fill='both', expand=True, padx=5, pady=5)

frame_input.pack_propagate(False)  # fixes resize issue when loading widgets
frame_output.pack_propagate(False)


# input window
# ----------------------------------------------------------------------------

# input pdb code
code_input = tk.Entry(frame_pdb_code, relief=tk.GROOVE, bd=1, font=FONT)
code_input.pack(fill='x', padx=5, pady=5)
code_input.insert(0, STR_CODE)

# input cutoff distance for distance condition
dist_input = tk.Entry(frame_pdb_code, relief=tk.GROOVE, bd=1, font=FONT)
dist_input.pack(fill='x', padx=5, pady=5)
dist_input.insert(0, STR_DIST)

# input cutoff angle for distance condition
angle_input = tk.Entry(frame_pdb_code, relief=tk.GROOVE, bd=1, font=FONT)
angle_input.pack(fill='x', padx=5, pady=5)
angle_input.insert(0, STR_ANGL)

# checkbuttons for aromatic residues
checkbutton_phe = tk.Checkbutton(frame_aromatics, text='Phenylalanine', variable=VAR_PHE, font=FONT)
checkbutton_phe.pack(side='top', anchor='w')
checkbutton_tyr = tk.Checkbutton(frame_aromatics, text='Tyrosine', variable=VAR_TYR, font=FONT)
checkbutton_tyr.pack(side='top', anchor='w')
checkbutton_trp = tk.Checkbutton(frame_aromatics, text='Tryptophan', variable=VAR_TRP, font=FONT)
checkbutton_trp.pack(side='top', anchor='w')

# lone pair interpolation model radio buttons
cp_rad = tk.Radiobutton(frame_model, text=CP_INT, font=FONT, indicatoron=0, variable=VAR_MOD, value=1)
cp_rad.pack(side='top', fill='x', padx=35, pady=5)
rm_rad = tk.Radiobutton(frame_model, text=RM_INT, font=FONT, indicatoron=0, variable=VAR_MOD, value=2)
rm_rad.pack(side='top', fill='x', padx=35, pady=5)

# go button       
button_go = tk.Button(frame_go, text='Go', font=FONT, command=print_main, bg='gray50')
button_go.pack(fill='x', padx=5, pady=(5, 1.5))

# print a legend button to console
handle_legend = tk.Button(frame_go, text='Legend', font=FONT, command=display_legend, bg='gray50')
handle_legend.pack(fill='x', padx=5, pady=1.5)

# save button                                   
save_data = tk.Button(frame_go, text='Save data?', font=FONT, command=output_save, bg='gray50')
save_data.pack(fill='x', padx=5, pady=1.5)

# exit button
button_exit = tk.Button(frame_go, text="Exit", command=master.destroy, font=FONT, bg='gray50')
button_exit.pack(fill='x', padx=5, pady=1.5)


# output window
# ----------------------------------------------------------------------------
text_output = ScrolledText(frame_output, relief=tk.GROOVE, bd=1, font=FONT, bg='gray12', fg='yellow green')
text_output.pack(fill='both', expand=True, padx=5, pady=5)
text_output.insert(tk.END, '** Prompt **\n')
text_output.insert(tk.END, '** {} ** \n'.format(BUILD))
text_output.insert(tk.END, '** Detected: {} **\n'.format(PLATFORM))
text_output.insert(tk.END, '** Results will display here **\n')
if debug: text_output.insert(tk.END, '** Running in DEBUG mode **\n')
    

# main
# ----------------------------------------------------------------------------
tk.mainloop()
