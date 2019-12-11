* David *

Contents
---------

- BENCHMARK DATA -
./controls/test_randomized_pdb_codes.csv                  <- A randomized list of PDB codes
./controls/test_pdb_File_Reading_Module_v4_0.py           <- Used to generate ./test_483OutputA3-3-M-Benchmark.csv
./controls/test_483OutputA3-3-M-Benchmark.csv             <- Benchmark used in ./test_ma.py      
./controls/test_n_3_bridges_no_ang_limit_6_angstroms.json <- A 3-bridge control dataset
./controls/test_dataset_ec_codes.csv                      <- Control EC code dataset

- TESTS -
./test_ma.py                                              <- Formal test framework for met-aromatic

- LEGACY -
./legacy/
./test_ma_lowlevel_from_grad_school.py                    <- Met-aromatic code from grad school
./test_ma.py                                              <- Test current Met-aromatic against ./test_483OutputA3-3-M-Benchmark.csv benchmark
./test_ma_against_grad_school_work.py                     <- Test current Met-aromatic against grad school code
./test_ma_protein_identity_getter.py                      <- Tests that Met-aromatic can return proper protein identity
./test_ma_bridges.py                                      <- Tests that Met-aromatic can return 3-bridges
./test_ma2.py                                             <- Formal unit test for non-cascaded ma
./test_ma2_bridges.py                                     <- Formal unit test for non-cascaded ma bridge finder
./test_ma2_ec_codes.py                                    <- Formal unit test for EC code parsing
