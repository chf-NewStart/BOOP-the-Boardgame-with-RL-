import numpy as np
import random
import tkinter as tk
from tkinter import messagebox

class BoopGame:
    def __init__(self, master=None):
        # 4-layer board: [P1 kittens, P1 cats, P2 kittens, P2 cats]
        self.board = np.zeros((4, 6, 6), dtype=int)
        self.pools = {
            1: {"kittens": 8, "cats": 0},
            2: {"kittens": 8, "cats": 0}
        }
        self.current_player = 1
        self.selected_piece_type = "kitten"  # Default to kitten placement
        self.winner = None
        
        if master:
            self.master = master
            self.setup_gui()
    
    def setup_gui(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack()
        
        # Piece type selection
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack()
        self.piece_var = tk.StringVar(value="kitten")
        tk.Radiobutton(self.control_frame, text="Kitten", variable=self.piece_var, 
                      value="kitten").pack(side=tk.LEFT)
        tk.Radiobutton(self.control_frame, text="Cat", variable=self.piece_var, 
                      value="cat").pack(side=tk.LEFT)
        
        # Game board
        self.buttons = [[tk.Button(self.frame, height=3, width=6, bg='white',
                                 command=lambda i=i, j=j: self.place_piece(i, j))
                        for j in range(6)] for i in range(6)]
        for i in range(6):
            for j in range(6):
                self.buttons[i][j].grid(row=i, column=j)
        
        self.reset_button = tk.Button(self.master, text="New Game", command=self.reset)
        self.reset_button.pack()
        self.update_gui()
    
    def place_piece(self, x, y):
        if self.winner:
            return
            
        piece_type = self.piece_var.get()
        player = self.current_player
        layer = 0 if piece_type == "kitten" else 1
        
        # Validate move
        if not self.is_valid_placement(x, y, player, piece_type):
            return
        
        # Place piece
        self.board[player*2 - 2 + layer, x, y] = 1
        self.pools[player][piece_type + "s"] -= 1
        
        # Apply booping rules
        self.apply_boop(x, y, player, piece_type == "cat")
        
        # Check for graduation
        self.check_graduation(player)
        
        # Check win conditions
        if self.check_win_conditions(player):
            self.winner = player
            messagebox.showinfo("Game Over", f"Player {player} wins!")
            return
            
        # Switch players
        self.current_player = 3 - player
        self.update_gui()
    
    def is_valid_placement(self, x, y, player, piece_type):
        # Check pool availability and empty space
        if self.pools[player][piece_type + "s"] <= 0:
            return False
        if np.sum(self.board[:, x, y]) > 0:
            return False
        return True
    
    def apply_boop(self, x, y, player, is_cat):
        # Get all 8 adjacent positions
        directions = [(-1,-1), (-1,0), (-1,1),
                     (0,-1),          (0,1),
                     (1,-1),  (1,0), (1,1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 6 and 0 <= ny < 6:
                # Check all layers for pieces to boop
                for layer in range(4):
                    if self.board[layer, nx, ny] == 1:
                        # Check booping rules
                        booper_is_cat = (layer % 2 == 1)
                        boopee_is_cat = (layer % 2 == 1)
                        
                        if is_cat or (not boopee_is_cat):
                            # Calculate new position
                            new_x = nx + dx
                            new_y = ny + dy
                            
                            if 0 <= new_x < 6 and 0 <= new_y < 6:
                                # Move piece
                                self.board[layer, new_x, new_y] = 1
                            else:
                                # Return to pool
                                owner = 1 if layer < 2 else 2
                                piece_type = "cat" if layer % 2 == 1 else "kitten"
                                self.pools[owner][piece_type + "s"] += 1
                                
                            self.board[layer, nx, ny] = 0
    
    def check_graduation(self, player):
        # Check for 3-in-a-row kittens
        kitten_layer = 0 if player == 1 else 2
        for x in range(6):
            for y in range(6):
                # Check all directions
                if self.check_line(x, y, 1, 0, kitten_layer) or \
                   self.check_line(x, y, 0, 1, kitten_layer) or \
                   self.check_line(x, y, 1, 1, kitten_layer) or \
                   self.check_line(x, y, 1, -1, kitten_layer):
                    # Remove kittens and add cats
                    self.pools[player]["cats"] += 3
                    self.pools[player]["kittens"] -= 3
                    self.board[kitten_layer, x:x+3, y] = 0  # Simplified for demo
    
    def check_line(self, x, y, dx, dy, layer):
        # Check if 3 consecutive pieces exist
        try:
            return all(self.board[layer, x+i*dx, y+i*dy] == 1 for i in range(3))
        except IndexError:
            return False
    
    def check_win_conditions(self, player):
        # Check for 3 cats in a row
        cat_layer = 1 if player == 1 else 3
        for x in range(6):
            for y in range(6):
                if self.check_line(x, y, 1, 0, cat_layer) or \
                   self.check_line(x, y, 0, 1, cat_layer) or \
                   self.check_line(x, y, 1, 1, cat_layer) or \
                   self.check_line(x, y, 1, -1, cat_layer):
                    return True
        # Check all cats placed
        if np.sum(self.board[cat_layer]) == 8:
            return True
        return False
    
    def update_gui(self):
        colors = {
            (0,0): 'white',   # Empty
            (1,0): 'orange',  # P1 kitten
            (1,1): 'dark orange',  # P1 cat
            (2,0): 'gray',    # P2 kitten
            (2,1): 'dark gray'  # P2 cat
        }
        
        for i in range(6):
            for j in range(6):
                cell = ""
                bg_color = 'white'
                for layer in range(4):
                    if self.board[layer, i, j] == 1:
                        player = 1 if layer < 2 else 2
                        piece_type = "kitten" if layer % 2 == 0 else "cat"
                        cell = "K" if piece_type == "kitten" else "C"
                        bg_color = colors[(player, layer%2)]
                self.buttons[i][j].config(text=cell, bg=bg_color)
        
        # Update pool display
        self.master.title(f"Player {self.current_player}'s Turn | "
                         f"P1 Kittens: {self.pools[1]['kittens']} Cats: {self.pools[1]['cats']} | "
                         f"P2 Kittens: {self.pools[2]['kittens']} Cats: {self.pools[2]['cats']}")
    
    def reset(self):
        self.board = np.zeros((4, 6, 6), dtype=int)
        self.pools = {
            1: {"kittens": 8, "cats": 0},
            2: {"kittens": 8, "cats": 0}
        }
        self.current_player = 1
        self.winner = None
        self.update_gui()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Boop! Board Game")
    game = BoopGame(root)
    root.mainloop()