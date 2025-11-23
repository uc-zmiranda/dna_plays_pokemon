from dna_boy import DNABoy
import multiprocessing as mp
import itertools as it
import random
from pyboy.utils import WindowEvent

PLAYER_Y_ADDR = 0xD361
PLAYER_X_ADDR = 0xD362


class GeneticAlgo(DNABoy):
    def __init__(self, ROM_PATH:str):
        self.ROM_PATH = ROM_PATH

    
    def find_best_cfg(self, n_jobs:int = 3):
        mp.set_start_method('spawn', force = True)
        
        tasks = [(cfg, i) for i, cfg in enumerate(self.controller_configs)]
        
        with mp.Pool(processes = n_jobs) as pool:
            results = pool.map(self._worker, tasks)
            
        results.sort(key = lambda x: x[0])
        fitness = [f for _, f in results]
        
        for i, fit in enumerate(fitness):
            print(f"controller {i}: fitness = {fit}")
            
               
    def _worker(self, args):
        cfg , idx = args
        fitness = self._run_fitness(cfg, self.ROM_PATH)
        return idx, fitness
                                
        
    def _run_fitness(self, ctrl_cfg:list, codon_list:list, n_steps:int):
        boy = DNABoy(self.ROM_PATH)
        ctrl_dict = self._make_cfg_dict(ctrl_cfg, boy)
        x0, y0 = self._get_location(boy)
        
        boy.execute_str(codon_list, ctrl_dict, n_steps)
            
        x1, y1 = self._get_location(boy)
        fitness = (x1-x0, y1-y0)
        
        return (ctrl_dict, fitness)
        

    @staticmethod
    def _get_location(boy):
        x = boy.memory[PLAYER_X_ADDR]
        y = boy.memory[PLAYER_Y_ADDR]
        
        return x,y
    
    @staticmethod
    def _calc_ctrl_cfgs(n_configs = 300):
        moves = [
            (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
            (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
            (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
            (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
            (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
            (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B),
            (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START),            
        ]
        
                
        codon_perms = [''.join(p) for p in it.product(['A', 'T', 'C', 'G'], repeat = 3)]
        configs = []
        for _ in range(n_configs):
            cfg = []
            for codon in codon_perms:
                macro = random.choice(moves)
                cfg.append((codon, macro))
            configs.append(cfg)
        
        return configs
        

    @staticmethod
    def _make_cfg_dict(ctrl_cfg:tuple, boy):
        map_dict = {}
        for map in ctrl_cfg:
            codon, (press, release) = map
            map_dict[codon] = (lambda p = press, r = release, b=boy: boy._tap(p,r))
        
        return map_dict
            
        
    
    
    
def main():
    
    dna_str = "TTCCCAACCCCTAGACTTCCCCTGTACCTATGGTTCACTGGATGCCCCAAGGATACCTGATACTCATGTTAG"            
    algo = GeneticAlgo('/home/zac/Desktop/uchicago/science_computing/final_project/pokemon_red.gb')
    ctrl_cfg = algo._calc_ctrl_cfgs()[0]
    fitness = algo._run_fitness(ctrl_cfg, dna_str, 10)
    breakpoint()
    

if __name__ == '__main__':
    main()

    
        
        
        
    
    