from pyboy import PyBoy
from pyboy.utils import WindowEvent

class DNABoy(PyBoy):
    
    def __init__(self, ROM_PATH:str):
        super().__init__(ROM_PATH)
        self.n_moves = 0
        
        
    
    def execute_str(self, dna_seq:str, move_map:dict, n_steps:int | None = None) -> None:
        """
        Method to execute string of moves based on mapping

        Args:
            move_str (str): string of moves to execute
        """
        
        codon_list = [dna_seq[i:i+3].strip().upper() for i in range(0, len(dna_seq), 3)]
        for codon in codon_list:
            if n_steps is not None and self.n_moves >= n_steps:
                break
            action = move_map[codon]
            if action:
                self.n_moves += 1
                print(f"move {self.n_moves}: {codon}")
                action()
            else:
                pass
            
    
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
    # name character
    move_str = 'WWSWSAWAAAAAAAAAAAAAAAARRRADRALLLLUADDDDRRRRRRRRAW'
    
    # name rival
    move_str_1 = 'AAAAAAARRRRRRRRDALLLLALLLLUADDDDRRRRRRRRAAAAAAAAAAAAAAWW'
    
    dna_boy = DNABoy(ROM_PATH)
    dna_boy.execute_str(move_str)
    dna_boy.execute_str(move_str_1)
    while dna_boy.tick():
        dna_boy.tick()
    
    
    
if __name__ == '__main__':
    main()