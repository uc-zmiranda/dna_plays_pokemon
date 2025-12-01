from dna_boy import DNABoy
import multiprocessing as mp
import itertools as it
import random
from pyboy.utils import WindowEvent
from tqdm import tqdm
from PIL import Image, ImageOps
import math
import pickle


PLAYER_Y_ADDR = 0xD361
PLAYER_X_ADDR = 0xD362
MENU_MASK_ADDR = 0xCC29  
BATTLE_TYPE_ADDR = 0xD057


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
            
        return results
    
    
    def find_fitness(self, ctrl_cfg:list, dna_seq:str, n_steps:int, headless:bool = True, record_frames:bool = False):
        
        frames = []
        boy = DNABoy(self.ROM_PATH, headless = headless)
        GeneticAlgo._load_start_state(boy)
        x0, y0 = self._get_location(boy)
        
        if record_frames:
            frames = boy.execute_str(dna_seq, ctrl_cfg, n_steps, True, False)
        else:
            boy.execute_str(dna_seq, ctrl_cfg, n_steps)
        
        x1, y1 = self._get_location(boy)
        
        fitness = self._calc_fitness(x0, y0, x1, y1)
        
        return (ctrl_cfg, fitness, frames)
    
    
    def viz_best_n_cfgs(self, results:list, n:int, dna_str:str, n_steps:int, out_path:str):
        
        all_frames = self._record_top_n_runs(n, results, dna_str, n_steps, True)
        rows, cols = self._calc_grid_shape(n)
        
        # Normalize sequence lengths
        max_len = max(len(seq) for seq in all_frames)
        for seq in all_frames:
            if seq:
                last = seq[-1]
                while len(seq) < max_len:
                    seq.append(last)

        
        sample_frame = self._add_border(all_frames[0][0])
        cell_w, cell_h = sample_frame.size

        grid_frames = []
        for t in range(max_len):
            grid_img = Image.new("RGB", (cols * cell_w, rows * cell_h))

            for idx, seq in enumerate(all_frames):
                r = idx // cols
                c = idx % cols
                frame = self._add_border(seq[t])
                grid_img.paste(frame, (c * cell_w, r * cell_h))
            
            grid_frames.append(grid_img)

        # Save to GIF
        grid_frames[0].save(
            out_path,
            save_all=True,
            append_images=grid_frames[1:],
            duration=200,
            loop=0
        )
        
    
    
    def _record_top_n_runs(self, n:int, results:list, dna_str:str, n_steps:int, headless = True):
        
        top_i = [idx for idx, _ in results[:n]]
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
        _, _, frames = self.find_fitness(cfg, dna_str, n_steps, True, True)

        return frames
    
    @staticmethod
    def _add_border(img, border_size=3, color=(255, 0, 0)):
        return ImageOps.expand(img, border=border_size, fill=color)
            
               
    def _worker(self, args):        
        idx, cfg, dna_str, n_steps, rom_path, headless = args
        
        boy = DNABoy(rom_path, headless = headless)
        GeneticAlgo._load_start_state(boy)
        x0, y0 = GeneticAlgo._get_location(boy)
        boy.execute_str(dna_str, cfg, n_steps, False, False)
        x1, y1 = GeneticAlgo._get_location(boy)
        fitness = self._calc_fitness(x0, y0, x1, y1)
        
        
        
        return idx, fitness, cfg
                                
    @staticmethod
    def _calc_fitness(x0:int, y0:int, x1:int, y1:int, stuck_dist = 20 , stuck_penalty:int = -50):
        
        dx = x1 - x0
        dy = y1 - y0
        
        dist = abs(dx) + abs(dy)
        
        north = -dy * 1.40
        
        
        if dist < stuck_dist:
            dist = dist - stuck_penalty
            
        fitness = dist + north
        
        return fitness
            
        
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
            #(WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START),            
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
        with open('/home/zac/Desktop/uchicago/science_computing/final_project/algo_test.state', 'rb') as game_state:
            boy.load_state(game_state)
            
            
    @staticmethod
    def _calc_grid_shape(k: int):
        if k <= 0:
            return (0, 0)
        if k == 1:
            return (1, 1)

        # Start with the square root
        root = int(math.sqrt(k))

        # Try root × root
        if root * root == k:
            return (root, root)

        # Otherwise grow columns first
        rows = root
        cols = root

        while rows * cols < k:
            cols += 1
            if rows * cols >= k:
                break
            rows += 1

        return (rows, cols)
        
    
def main():
    
    
    def iter_fasta(path:str):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('>'):
                    continue
                yield line.upper()
                
                
    def load_prefix_bases(path: str, max_bases: int) -> str:
        pieces = []
        total = 0
        for chunk in iter_fasta(path):
            if total + len(chunk) >= max_bases:
                need = max_bases - total
                pieces.append(chunk[:need])
                break
            else:
                pieces.append(chunk)
                total += len(chunk)
        return "".join(pieces)
                    
        
    n_steps = 500
    n_cfgs = 300
    n_threads = 8
    n_viz = 16
    
    ROM_PATH = '/home/zac/Desktop/uchicago/science_computing/final_project/pokemon_red.gb'
    
    dna_str = load_prefix_bases('/home/zac/Desktop/uchicago/science_computing/final_project/lung_fish_data/GCA_040581445.1_ASM4058144v1_genomic.fna', n_steps)    
    
    
    algo = GeneticAlgo(ROM_PATH, n_cfgs = n_cfgs)    
    
    results = algo.find_best_cfg(dna_str, n_steps, n_threads)
    
    #algo.viz_best_n_cfgs(results, n_viz, dna_str, n_steps, './top_16_viz.gif')
    
    best_cfg = results[0][2]
        
    with open('/home/zac/Desktop/uchicago/science_computing/final_project/best_cfg.pkl', 'wb') as f:
        pickle.dump(best_cfg, f)
    
    

if __name__ == '__main__':
    main()

    
        
        
        
    
    