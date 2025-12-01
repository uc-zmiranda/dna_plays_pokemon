from pyboy import PyBoy
from pyboy.utils import WindowEvent
import warnings


warnings.filterwarnings('ignore')


class DNABoy(PyBoy):
    
    def __init__(self, ROM_PATH:str, LOAD_STATE_PATH:str|None=None, headless:bool = False):
        if headless is False:
            super().__init__(ROM_PATH)
        else:
            super().__init__(ROM_PATH, window = "null")
        
        if LOAD_STATE_PATH is not None:
            with open(LOAD_STATE_PATH, 'rb') as f_in:
                self.load_state(f_in)
            
        self.n_moves = 0
        self._viz_moves = self._viz_move_dict()
        
    
    def execute_str(self, dna_seq:str, move_map:list, n_steps:int | None = None, record_frames:bool = False, print_steps:bool = True) -> None:
        """
        Method to execute string of moves based on mapping

        Args:
            move_str (str): string of moves to execute
        """
        
        if record_frames:
            frames = []
        
        move_dict = self._cfg_to_dict(move_map)
            
        codon_list = [dna_seq[i:i+3].strip().upper() for i in range(0, len(dna_seq), 3)]
        for codon in codon_list:
            if n_steps is not None and self.n_moves >= n_steps:
                break
            
            if codon in move_dict.keys():
                action, viz = move_dict[codon]
                if action:
                    self.n_moves += 1
                    
                    if print_steps is True:
                        
                        print(f"move {self.n_moves}: {codon}: {viz}")
                        
                    action()
                    
                    if record_frames:
                        frame = self.screen.image.copy()
                        frames.append(frame)
                else:
                    continue                                
            else:
                continue
            
        if record_frames:
            return frames
        
        
    
    def _cfg_to_dict(self, ctrl_cfg:list):
        map_dict = {}
        for map in ctrl_cfg:
            codon, (press, release) = map
            map_dict[codon] = ((lambda p = press, r = release, b=self: b._tap(p,r)), self._viz_moves[(press,release)])
        
        return map_dict
    
    
    def _viz_move_dict(self):
        viz_moves = {
            (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT): '\u2192',
            (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT): '\u2190',
            (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP): '\u2191',
            (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN): '\u2193',
            (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A): 'A',
            (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B): 'B',
            (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START): "Start",           
        }
        
        return viz_moves
        
                        
    
    def _tap(self, action_start, action_end, wait:int=150):
        self.send_input(action_start)
        
        for _ in range(0,8):
            self.tick()
            
        self.send_input(action_end)
        
        if wait:
            for _ in range(wait):
                self.tick()


def main():    
    ROM_PATH = '/home/zac/Desktop/uchicago/science_computing/final_project/pokemon_red.gb'
    
    dna_boy = DNABoy(ROM_PATH)
    # with open('/home/zac/Desktop/uchicago/science_computing/final_project/algo_test.state', 'rb') as game_state:
    #     dna_boy.load_state(game_state)
        
    while dna_boy.tick():
        dna_boy.tick()
        
    with open('/home/zac/Desktop/uchicago/science_computing/final_project/game_start.state', 'wb') as game_state:
        dna_boy.save_state(game_state)
        
    


    
    
if __name__ == '__main__':
    main()