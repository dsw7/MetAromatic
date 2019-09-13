# delete this eventually
# test that data from non-OO met-aromatic matches newer OO version
# time

from sys import path as PATH; PATH.extend(['../utils', '../utilsLegacy'])  
from time import time                                 
from ma_lowlevel import met_aromatic                          
from PDB_filegetter import PDBFile                              
from ma import MetAromatic
from re import sub
from pandas import DataFrame, testing


CHAIN = "A"
CUTOFF = 4.9
ANGLE = 109.5

codes = """
10GS,11GS,121P,12CA,12GS,133L,134L,13GS,14GS,16GS,
17GS,18GS,19GS,1A00,1A01,1A02,1A07,1A08,1A09,1A0L,
1A0N,1A0U,1A0Z,1A12,1A15,1A17,1A1A,1A1B,1A1C,1A1E,
1A1M,1A1N,1A1O,1A1U,1A1W,1A1X,1A1Z,1A22,1A27,1A28,
1A2B,1A2C,1A31,1A35,1A36,1A3B,1A3E,1A3K,1A3N,1A3O,
1A3Q,1A3S,1A42,1A46,1A4I,1A4P,1A4R,1A4V,1A4W,1A4Y,
1A52,1A5E,1A5G,1A5H,1A5R,1A5Y,1A61,1A66,1A6A,1A6Q,
1A6Y,1A6Z,1A7A,1A7C,1A7F,1A7X,1A81,1A85,1A86,
1A8E,1A8F,1A8J,1A8M,1A93,1A9B,1A9E,1A9N,1A9U,1A9W,
1AA2,1AA9,1AAP,1AAX,1AB2,1ABI,1ABJ,1ABN,1ABW,1ABY
"""


def test_old_ma(code):
    t_start = time()
    file_PDB = PDBFile(code)
    path_to_file = file_PDB.fetch_from_PDB()
    data = met_aromatic(filepath=path_to_file, CHAIN=CHAIN, CUTOFF=CUTOFF, ANGLE=ANGLE, MODEL="cp")
    file_PDB.clear()
    return data, round(time() - t_start, 4)


def test_new_ma(code):
    t_start = time()
    data = MetAromatic(code, CHAIN, CUTOFF, ANGLE).met_aromatic()
    return data, round(time() - t_start, 4)


if __name__ == '__main__':
    codes = sub('\n', '', codes).split(',')
    for code in codes:
        data_new, time_new = test_new_ma(code=code)
        data_old, time_old = test_old_ma(code=code)
        print('Code: {}, New time: {} s, Old time: {} s'.format(code, time_new, time_old))
        
        if data_new == [] and data_old == []:
            pass
        else:
            df_new = DataFrame(data_new).sort_values(4).reset_index(drop=True)
            df_old = DataFrame(data_old).sort_values(4).reset_index(drop=True)

            testing.assert_frame_equal(df_new, df_old)
