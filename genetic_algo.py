from dna_boy import DNABoy
import multiprocessing as mp
import itertools as it
import random
from pyboy.utils import WindowEvent
from tqdm import tqdm



PLAYER_Y_ADDR = 0xD361
PLAYER_X_ADDR = 0xD362


class GeneticAlgo(DNABoy):
    def __init__(self, ROM_PATH:str, n_cfgs:int = 300):
        self.ROM_PATH = ROM_PATH
        self.cfgs = self._calc_ctrl_cfgs(n_cfgs)
        
    
    def find_best_cfg(self, dna_str:str, n_steps:int = 250, n_jobs:int = 3, headless:bool = True):
        mp.set_start_method('spawn', force = True)
        
        tasks = [
            (i, cfg, dna_str, n_steps, self.ROM_PATH, headless)
            for i, cfg in enumerate(self.cfgs)
            ]
        
        results = []
        with mp.Pool(processes = n_jobs) as pool:
            for res in tqdm(pool.imap_unordered(self._worker, tasks), total=len(tasks), desc="Evaluating configs"):
                results.append(res)
            
        results.sort(key = lambda x: x[1], reverse = True)
        
        for i, fit in enumerate(results):
            print(f"controller {i}: fitness = {fit}")
            
        return results
    
    
    def find_fitness(self, ctrl_cfg:list, dna_seq:str, n_steps:int, headless:bool = True, record_frames:bool = False):
        
        frames = []
        boy = DNABoy(self.ROM_PATH, headless = headless)
        ctrl_dict = self._make_cfg_dict(ctrl_cfg, boy)
        x0, y0 = self._get_location(boy)
        
        if record_frames:
            frames = boy.execute_str(dna_seq, ctrl_dict, n_steps, True)
        else:
            boy.execute_str(codon_list, ctrl_dict, n_steps)
        
        x1, y1 = self._get_location(boy)
        fitness = (x1-x0, y1-y0)
        
        return (ctrl_dict, fitness, frames)
    
    
    def viz_best_n_cfgs(self, results:list, n:int, dna_str:str, n_steps:int, out_path:str):
        
        all_frames = self._record_top_n_runs(n, results, dna_str, n_steps, True)
        
        # Normalize sequence lengths
        max_len = max(len(seq) for seq in all_frames)
        for seq in all_frames:
            if seq:
                last = seq[-1]
                while len(seq) < max_len:
                    seq.append(last)

        # Image size (each cell)
        cell_w, cell_h = all_frames[0][0].size

        grid_frames = []
        for t in range(max_len):
            grid_img = Image.new("RGB", (cols * cell_w, rows * cell_h))

            for idx, seq in enumerate(frame_sequences):
                r = idx // cols
                c = idx % cols
                frame = seq[t]
                grid_img.paste(frame, (c * cell_w, r * cell_h))

            grid_frames.append(grid_img)

        # Save to GIF
        grid_frames[0].save(
            out_path,
            save_all=True,
            append_images=grid_frames[1:],
            duration=100,
            loop=0
        )
        
        
    
    def _record_top_n_runs(self, n:int, results:list, dna_str:str, n_steps:int, headless = True):
        
        top_i = [idx for idx, _ in results[:k]]
        top_cfgs = [self.cfgs[i] for i in top_i]

        all_frames = []
        
        boy = DNABoy(self.ROM_PATH, headless=headless)
        GeneticAlgo._load_start_state(boy)
        
        for cfg in top_cfgs:
            frames = self._record_run(cfg, dna_str, n_steps, True)
            all_frames.append(frames)
        
    
        return all_frames
    
    
    
    def _record_run(self, cfg:list, dna_str:str, n_steps:int, headless = True):
        
        boy = DNABoy(self.ROM_PATH, headless=headless)
        GeneticAlgo._load_start_state(boy)
        frames = self.find_fitness(cfg, dna_str, n_steps, True, True)

        return frames
            
               
    def _worker(self, args):        
        idx, cfg, dna_str, n_steps, rom_path, headless = args
        
        boy = DNABoy(rom_path, headless = headless)
        GeneticAlgo._load_start_state(boy)
        ctrl_dict = GeneticAlgo._make_cfg_dict(cfg, boy)
        x0, y0 = GeneticAlgo._get_location(boy)
        boy.execute_str(dna_str, ctrl_dict, n_steps, False)
        x1, y1 = GeneticAlgo._get_location(boy)
        fitness = (x1 - x0, y1 - y0)
        
        return idx, fitness
                                
            
    
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
            map_dict[codon] = (lambda p = press, r = release, b=boy: b._tap(p,r))
        
        return map_dict
    
    @staticmethod
    def _load_start_state(boy):  
        with open('/home/zac/Desktop/uchicago/science_computing/final_project/game_start.state', 'rb') as game_state:
            boy.load_state(game_state)
        
    
    
    
def main():
    
    dna_str = "TTCCCAACCCCTAGACTTCCCCTGTACCTATGGTTCACTGGATGCCCCAAGGATACCTGATACTCATGTTAG"            
    algo = GeneticAlgo('/home/zac/Desktop/uchicago/science_computing/final_project/pokemon_red.gb', n_cfgs = 10)
    results = algo.find_best_cfg(dna_str, 25)
    breakpoint()
    best_cfg = algo.cfgs[results[0][0]]
    frames = algo._record_run(best_cfg, dna_str, 25)
    
    
    breakpoint()
    
    

if __name__ == '__main__':
    main()

    
        
        
        
    
    