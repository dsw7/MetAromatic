"""
dsw7@sfu.ca

Old, poorly written code from when I was younger and more inexperienced.
I have ported this code in 2019 to generate a benchmark dataset that I will
run tests against. I prettified this code a bit to enhance readability.

The benchmark dataset is named: 483OutputA3-3-M-Benchmark.csv
"""


# dependencies
# ------------------------------------------------------
import numpy as np
import urllib.request
import os
import pandas as pd


# constants
# ------------------------------------------------------
ANGSTROMS = 4.9
ANGLE = 109.5
COUNTER = 0
CHAIN = 'A'

lista = ['PRO', 'MET', 'PHE', 'TYR', 'TRP']

atom_type = [['C', 'N', 'CB', 'CA'], ['CG', 'SD', 'CE'], [
    'CG',
    'CD1',
    'CE1',
    'CZ',
    'CE2',
    'CD2',
    ], [
    'CG',
    'CD1',
    'CE1',
    'CZ',
    'CE2',
    'CD2',
    ], [
    'CD2',
    'CE3',
    'CZ2',
    'CH2',
    'CZ3',
    'CE2',
    ]]

tok = [
    [['CG-CD2'], ['CG', 'CD2']],
    [['CD2-CE2'], ['CD2', 'CE2']],
    [['CE2-CZ'], ['CE2', 'CZ']],
    [['CZ-CE1'], ['CZ', 'CE1']],
    [['CE1-CD1'], ['CE1', 'CD1']],
    [['CD1-CG'], ['CD1', 'CG']],
    ]

tok2 = [
    [['CD2-CE2'], ['CD2', 'CE2']],
    [['CE2-CZ2'], ['CE2', 'CZ2']],
    [['CZ2-CH2'], ['CZ2', 'CH2']],
    [['CH2-CZ3'], ['CH2', 'CZ3']],
    [['CZ3-CE3'], ['CZ3', 'CE3']],
    [['CE3-CD2'], ['CE3', 'CD2']],
    ]


# functions
# ------------------------------------------------------
def midpoint(a, b):
    midpoint = 0.5 * (a[6] + b[6])
    return midpoint


def fnorm(vec1, vec2):
    fnorm = np.linalg.norm(vec1 - vec2)
    return fnorm


def unitvec(vec1):
    norm = np.linalg.norm(vec1)
    unitvec = []
    for element in range(0, 3):
        unitvec.append(vec1[element] / norm)
    return np.array(unitvec)


def vecangle(vec1, vec2):
    a = np.dot(vec1, vec2)
    b = np.linalg.norm(vec1)
    c = np.linalg.norm(vec2)
    return np.degrees(np.arccos(a / (b * c)))


# main
# ------------------------------------------------------
codelist = []
with open('randomized_pdb_codes.csv') as inputfile:
    for line in inputfile:
        codelist.append(line.strip())


for code in codelist[1:]:
    COUNTER += 1
    print(COUNTER, code)
    try:
        # Get file from pdb
        base1 = 'http://files.rcsb.org/download/{}.pdb'.format(code)
        base2 = code + '.pdb'
        path = urllib.request.urlretrieve(base1, base2)
        coord = []
        for line in open(path[0]):
            ist = line.split()
            if ist[0] == 'ATOM':
                for k in range(0, 5):
                    if ist[3] == lista[k]:
                        coord.append(ist[:6] + [np.array(ist[6:9],
                                     dtype=float)])
            elif ist[0] == 'ENDMDL':
                break
        os.remove(path[0])
        
        
        # 2019 patch - Selection of only A chain
        coord_intermediate = []
        for c in coord:
            if c[4] == CHAIN:
                coord_intermediate.append(c)
            else:
                pass
        coord = coord_intermediate
        
        
        # Primary sorting
        listoflists = [listP, listM, listF, listY, listW] = ([], [], [], [], [])
        for j in range(0, len(listoflists)):
            for i in range(0, len(coord)):
                if coord[i][3] == lista[j]:
                    for k in range(0, len(atom_type[j])):
                        if coord[i][2] == atom_type[j][k]:
                            listoflists[j].append(coord[i])
        mol_ser = []
        for i in range(0, len(listoflists)):
            mols = []
            for k in range(0, len(listoflists[i])):
                if listoflists[i][k][5] not in mols:
                    mols.append(listoflists[i][k][5])
            mol_ser.append(mols)
        e = []
        for j in range(0, len(listoflists)):
            d = []
            for k in range(0, len(mol_ser[j])):
                (c, chain) = ([], [])
                for i in range(0, len(listoflists[j])):
                    if listoflists[j][i][5] == mol_ser[j][k]:
                        if listoflists[j][i][4] not in chain:
                            chain.append(listoflists[j][i][4])
                        c.append(listoflists[j][i])
                d.append([chain, c])
            e.append(d)


        # Secondary sorting
        f = []
        for j in range(0, len(e)):
            dprime = []
            for k in range(0, len(e[j])):
                d = []
                for chain in range(0, len(e[j][k][0])):
                    c = []
                    for i in range(0, len(e[j][k][1])):
                        if e[j][k][1][i][4] == e[j][k][0][chain]:
                            c.append(e[j][k][1][i])
                    d.append(c)
                dprime.append(d)
            f.append(dprime)
        listoflists = [listP, listM, listF, listY, listW] = ([], [], [], [], [])
        for j in range(0, 5):
            for i in range(0, len(f[j])):
                for k in range(0, len(f[j][i])):
                    listoflists[j].append(f[j][i][k])
        
        
        # Computation of aromatic midpoints
        lmid = [midF, midY, midW] = ([], [], [])
        dlist = [[listF, tok], [listY, tok], [listW, tok2]]
        for p in range(0, 3):
            for i in range(0, len(dlist[p][0])):
                u = []
                for j in range(0, len(dlist[p][1])):
                    for k in range(0, len(dlist[p][0][i])):
                        if dlist[p][0][i][k][2] == dlist[p][1][j][1][0]:
                            a = dlist[p][0][i][k]
                    for k in range(0, len(dlist[p][0][i])):
                        if dlist[p][0][i][k][2] == dlist[p][1][j][1][1]:
                            b = dlist[p][0][i][k]
                    u.append([dlist[p][0][i][0][5], dlist[p][1][j][0],
                             midpoint(a, b)])
                lmid[p].append(u)


        # Interaction-specific distance based exclusion          
        listint=[PF_interaction,PY_interaction,PW_interaction,
                 MF_interaction,MY_interaction,MW_interaction]=[],[],[],[],[],[]
        listmid=[[midF,'PHE',listP],[midY,'TYR',listP],
                 [midW,'TRP',listP],[midF,'PHE',listM],
                 [midY,'TYR',listM],[midW,'TRP',listM]]
        for j in range(0, 6):
            for k1 in range(0, len(listmid[j][0])):
                for k2 in range(0, len(listmid[j][0][k1])):
                    vec2 = listmid[j][0][k1][k2][2]
                    for i in range(0, len(listmid[j][2])):
                        vec1 = listmid[j][2][i][1][6]
                        if fnorm(vec1, vec2) <= ANGSTROMS:
                            listint[j].append([listmid[j][2][i], ':',
                                    listmid[j][1], listmid[j][0][k1][k2],
                                    np.linalg.norm(vec2 - vec1)])

        
        # Algorithm PA-1-483
        for a1 in range(0, 3):
            for a2 in range(0, len(listint[a1])):
                tvec = []  # CA --> Origin
                for e1 in range(0, 4):
                    s = listint[a1][a2][0][e1][6] - listint[a1][a2][0][1][6]
                    tvec.append([(listint[a1][a2][0][e1])[:6], s])
        
                tvec2 = []  # Vector normal to CB-C-N plane (hydrogen vector)
                for e2 in range(0, 4):
                    if tvec[e2][0][2] == 'N' or tvec[e2][0][2] == 'C' \
                        or tvec[e2][0][2] == 'CB':
                        tvec2.append([tvec[e2][0], unitvec(tvec[e2][1])])
                crossvec1 = tvec2[1][1] - tvec2[0][1]
                crossvec2 = tvec2[2][1] - tvec2[0][1]
                hydrogen_vector = unitvec(np.cross(crossvec2, crossvec1))
        
                vec1 = unitvec(listint[a1][a2][3][2] - listint[a1][a2][0][1][6])
                vec2 = hydrogen_vector
                theta = vecangle(vec1, vec2)
                listint[a1][a2] = listint[a1][a2] + [[theta]]

          
        # Algorithm MA-2-483
        for a1 in range(3, 6):
            for a2 in range(0, len(listint[a1])):
                t2vec = []  # SD --> Origin
                for e1 in range(0, 3):
                    s2 = listint[a1][a2][0][e1][6] - listint[a1][a2][0][1][6]
                    t2vec.append([(listint[a1][a2][0][e1])[:6], s2])
        
                t2vec2 = []  # CG, CE unit vectors
                for e2 in range(0, 3):
                    if t2vec[e2][0][2] == 'CG' or t2vec[e2][0][2] == 'CE':
                        t2vec2.append([t2vec[e2][0], unitvec(t2vec[e2][1])])
                comp_elements = [2 ** 0.5 * unitvec(np.cross(t2vec2[0][1],
                                 t2vec2[1][1])), 2 ** 0.5
                                 * unitvec(np.cross(t2vec2[1][1],
                                 t2vec2[0][1])), unitvec(-0.5 * (t2vec2[0][1]
                                 + t2vec2[1][1]))]
                lp = [comp_elements[0] + comp_elements[2], comp_elements[1]
                      + comp_elements[2]]  # Lone pair vectors
        
                vec1 = unitvec(listint[a1][a2][3][2] - listint[a1][a2][0][1][6])
                vec2 = lp[0]  # Alpha lone pair
                a_theta = vecangle(vec1, vec2)
                vec1 = unitvec(listint[a1][a2][3][2] - listint[a1][a2][0][1][6])
                vec2 = lp[1]  # Gamma lone pair
                g_theta = vecangle(vec1, vec2)
                listint[a1][a2] = listint[a1][a2] + [[a_theta, g_theta]]
              
            
        # Information bank
        reflistint = []
        for j1 in range(0, 6):
            for j2 in range(0, len(listint[j1])):
                reflistint.append([(listint[j1][j2][0][1])[1:6],
                                  [listint[j1][j2][2]]
                                  + [listint[j1][j2][3][0]]
                                  + listint[j1][j2][3][1], listint[j1][j2][4],
                                  listint[j1][j2][5]])
        
        
        # 2019 porting....
        reflistint = [line for line in reflistint if line[0][2] == 'MET']
        reflistint = [i[0] + i[1] + [i[2]] + i[3] for i in reflistint]
        if reflistint == []:
            pass
        else:
            df = pd.DataFrame(reflistint)
            df = df.drop([0, 1, 7], axis=1)
            df.columns = [
                'MET',
                'CHAIN',
                'MET RES',
                'ARO',
                'ARO RES',
                'NORM',
                'MET-THETA',
                'MET-PHI',
                ]
            df['PDBCODE'] = [code[0:4]] * df.shape[0]
            df = df[df.CHAIN == CHAIN]
            df = df.drop('CHAIN', axis=1)
            # df = df[df.NORM <= ANGSTROMS]
            df = df[(df['MET-THETA'] <= ANGLE) | (df['MET-PHI'] <= ANGLE)]
            df = df.sort_values(by='NORM')
            df = df.reset_index(drop=True)
            df = df.reindex(sorted(df.columns), axis=1)
            with open('483OutputA3-3-M-Benchmark.csv', 'a') as f:
                df.to_csv(f, header=False)

            
    except Exception as exception:
        print(exception)
        if os.path.exists(path[0]):
            os.remove(path[0])
        pass

