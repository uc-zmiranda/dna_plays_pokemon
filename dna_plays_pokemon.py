from dna_boy import DNABoy
import pickle


def iter_fasta(path:str):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('>'):
                continue
            yield line.upper()
            

# loading best cfg
with open('/home/zac/Desktop/uchicago/science_computing/final_project/best_cfg.pkl', 'rb') as f_in:
    best_cfg = pickle.load(f_in)
    
# loading data
dna_gen = iter_fasta('/home/zac/Desktop/uchicago/science_computing/final_project/lung_fish_data/GCA_040581445.1_ASM4058144v1_genomic.fna')
    
# starting DNABoy
boy = DNABoy('/home/zac/Desktop/uchicago/science_computing/final_project/pokemon_red.gb', '/home/zac/Desktop/uchicago/science_computing/final_project/game_start.state')

# execute code
for line in dna_gen:
    boy.execute_str(line, best_cfg, None, False, True)
