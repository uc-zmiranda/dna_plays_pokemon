from pyboy import PyBoy
import warnings

warnings.filterwarnings('ignore')


class DNABoy(PyBoy):
    
    def __init__(self, ROM_PATH:str, SAVE_STATE_PATH:str|None=None, headless:bool = False):
        if headless is False:
            super().__init__(ROM_PATH)
        else:
            super().__init__(ROM_PATH, window = "null")
        
        if SAVE_STATE_PATH is not None:
            self.load_state(SAVE_STATE_PATH)
            
        self.n_moves = 0
        
    
    def execute_str(self, dna_seq:str, move_map:dict, n_steps:int | None = None, record_frames:bool = False, print_steps:bool = True) -> None:
        """
        Method to execute string of moves based on mapping

        Args:
            move_str (str): string of moves to execute
        """
        
        if record_frames:
            frames = []
            
        codon_list = [dna_seq[i:i+3].strip().upper() for i in range(0, len(dna_seq), 3)]
        for codon in codon_list:
            if n_steps is not None and self.n_moves >= n_steps:
                break
            action = move_map[codon]
            if action:
                self.n_moves += 1
                
                if print_steps is True:
                    print(f"move {self.n_moves}: {codon}")
                    
                action()
                
                if record_frames:
                    frame =self.screen.image.copy()
                    frames.append(frame)
                                
            else:
                pass
            
        if record_frames:
            return frames
                        
    
    def _tap(self, action_start, action_end, wait:int=150):
        self.send_input(action_start)
        self.tick()
        self.send_input(action_end)
        if wait:
            for _ in range(wait):
                self.tick()
                
                    
    def _wait(self, wait:int = 500):
        for _ in range(wait):
            self.tick()
            
            
    def _close(self):
        self.close()
        

def main():    
    ROM_PATH = '/home/zac/Desktop/uchicago/science_computing/final_project/pokemon_red.gb'
    
    dna_boy = DNABoy(ROM_PATH)
    with open('/home/zac/Desktop/uchicago/science_computing/final_project/game_start.state', 'rb') as game_state:
        dna_boy.load_state(game_state)
        
    while dna_boy.tick():
        dna_boy.tick()


    
    
if __name__ == '__main__':
    main()