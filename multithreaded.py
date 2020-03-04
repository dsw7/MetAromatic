from itertools import chain
from numpy import array_split
from concurrent import futures
from src import met_aromatic


class RunBatchJob:
    def __init__(self, batch_file, num_threads=30, cutoff_distance=4.9, cutoff_angle=109.5, chain='A', model='cp'):
        self.batch_file = batch_file
        self.num_threads = num_threads
        self.cutoff_distance = cutoff_distance
        self.cutoff_angle = cutoff_angle
        self.chain = chain
        self.model = model

    def open_batch_file(self):
        try:
            with open(self.batch_file) as f:
                data = [line.split(', ') for line in f]
        except FileNotFoundError:
            return None
        else:
            return list(chain(*data))

    def met_aromatic_thread(self, list_codes):
        for code in list_codes:
            print(code)
            results = met_aromatic.MetAromatic(
                code=code,
                cutoff_distance=self.cutoff_distance,
                cutoff_angle=self.cutoff_angle,
                chain=self.chain,
                model=self.model
            ).get_met_aromatic_interactions()
            print(results)

    def run_batch_job(self):
        pdb_codes = self.open_batch_file()
        if not pdb_codes:
            return None    # TODO: create custom exception

        batch_pdb_codes = array_split(pdb_codes, self.num_threads)
        
        with futures.ThreadPoolExecutor() as executor:
            for index in range(0, self.num_threads):
                executor.submit(self.met_aromatic_thread, batch_pdb_codes[index])    


RunBatchJob(batch_file=r'C:\Users\David\Desktop\pdb_codes.txt').run_batch_job()
