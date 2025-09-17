import random
import time
import json
import os

class Config:
    json_indent = 2 # json indent level

    player_data = { # player data dictionary
        "Id": None, 
        "Name": None,
        "High Scores": {
            "Easy": None,
            "Medium": None,
            "Hard": None
        },
        "Games Played": 0,
        "Total Time Played": 0.0
    } 

    starttext = "\nWelcome to the Number Guessing Game!\n" \
    "I'm thinking of a number between 1 and 100.\n" \
    "You have to guess the number. Easy right?\n"
    
    difftext = "\nPlease select the difficulty level:\n" \
    "1. Easy (10 chances)\n" \
    "2. Medium (5 chances)\n" \
    "3. Hard (3 chances)\n"

    task_path = 'playerdata.json' # path to player data
    if not os.path.exists(task_path): # create file if it doesn't exist
        with open(task_path, 'w') as f:
            json.dump({"Players": []}, f, indent=json_indent)


class Game:
    def __init__(self, player): # game with object
        self.player = player
        self.rng = random.randint(1, 100) # random number generator
        self.chances = 0 
        self.diff = None 
        self.attempts = 0
        self.timer = None
        self.duration = 0.0
        self.won = False

    def rng_reset(self):
        self.rng = random.randint(1, 100) # reset rng

    def countdown(self):
        print("Game will start in 3") # countdown
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1\n")
        time.sleep(1)
        input("Press ENTER to start...") # anticipate spamming
        self.timer = time.time() # start timer

    def difficulty(self):
        print(Config.difftext) # print difficulty text
        while True:
            try:    
                user_input = int(input("Enter difficulty (1,2 or 3): ")) # get user input
                if user_input == 1: 
                    self.diff = 'Easy'
                    self.chances = 10
                    print("\nYou have selected Easy difficulty!")
                    self.countdown()
                    break
                elif user_input == 2:
                    self.diff = 'Medium'
                    self.chances = 5
                    print("\nYou have selected Medium difficulty!")
                    self.countdown()
                    break
                elif user_input == 3:
                    self.diff = 'Hard'
                    self.chances = 3
                    print("\nYou have selected Hard difficulty!")
                    self.countdown()
                    break
                else:
                    print("Invalid input.\n") # handle out of range input
            except (ValueError): 
                print("Invalid input. Please enter a valid number.") # handle non-integer input

    def play(self):
        while self.chances > 0:
            try:
                guess = int(input("Enter your guess: "))
            except (ValueError):
                print("Invalid input.") # handle non-integer input
                continue

            if self.check_number(guess): #stop when number is correct
                self.won = True
                break
            self.attempts += 1 ## add attempt count
            self.chances -= 1 ## decrease chances

    def check_number(self, guess):
        if guess == self.rng: # check if guess is correct
            return True
        elif guess > self.rng: # give hint
            print(f"Incorrect! The number is less than {guess}.")
            return False
        elif guess < self.rng: # give hint
            print(f"Incorrect! The number is greater than {guess}.")    
            return False

    def end_game(self):
        self.duration = round(time.time() - self.timer, 2) # calculate duration
        self.player.highscore_update(self.diff, self.attempts + 1, self.duration, self.won) # update high score
        if self.won: 
            print(f"\nCongratulations! You guessed the correct number!") # win message
            print(f"Attempts: {self.attempts + 1}")
            print(f"Time: {self.duration}\n")
        else:
            print(f"\nYou've lost! The number was {self.rng}.") # lose message
            print(f"Time: {self.duration}\n")


class Player:
    def __init__(self, name):
        self.name = name 
        self.high_scores = {"Easy": None, "Medium": None, "Hard": None} # high scores for each difficulty
        self.games_played = 0
        self.total_time_played = 0.0
        self.id = None
        if not self.player_check(): # check if player exists
            self.register_player() # register player if not exists
        else:
            self.load_player() # load player data if exists
        
    def __str__(self):
        return f"Player {self.name} (ID: {self.id}) | Games: {self.games_played}, Time: {self.total_time_played:.2f}s"

    def player_check(self):
        with open(Config.task_path, 'r') as f:
            players = json.load(f)["Players"] # load player data
        players = [player["Name"] for player in players] # get list of player names
        if self.name in players:
            return True # player exists
        else:
            return False # player does not exist

    def register_player(self): # register new player
        with open(Config.task_path, 'r') as f:
            data = json.load(f) # load player data
        self.id = len(data["Players"]) # assign new ID
        new_player = Config.player_data.copy() # create new player data
        new_player["Id"] = self.id
        new_player["Name"] = self.name 
        data["Players"].append(new_player) # add new player to data
        with open(Config.task_path, 'w') as f:
            json.dump(data, f, indent=Config.json_indent) # save player data
        print(f"Player {self.name} registered with ID {self.id}.") 
    
    def load_player(self): # load existing player data
        with open(Config.task_path, 'r') as f:
            data = json.load(f) # load player data
        for player in data["Players"]:
            if player["Name"] == self.name:
                self.id = player["Id"] 
                self.high_scores = player["High Scores"]
                self.games_played = player["Games Played"]
                self.total_time_played = player["Total Time Played"]
                print(f"Welcome back, {self.name}! Your ID is {self.id}.")
                break

    def highscore_update(self, difficulty, attempts, timer, won): 
        self.games_played += 1 # add games played
        self.total_time_played += timer # add total time played
        if won:
            if self.high_scores[difficulty] is None or attempts < self.high_scores[difficulty]:
                self.high_scores[difficulty] = attempts # update high score
                print(f"New high score for {difficulty} difficulty: {attempts} attempts!")
        with open(Config.task_path, 'r') as f:
            data = json.load(f) # load player data
        for player in data["Players"]:
            if player["Id"] == self.id: # find player by ID
                player["High Scores"] = self.high_scores # update high score
                player["Games Played"] = self.games_played # update games played
                player["Total Time Played"] = self.total_time_played # update total time played
                break
        with open(Config.task_path, 'w') as f:
            json.dump(data, f, indent=Config.json_indent) # save player data

    def stats(self):
        print(f"\nPlayer: {self.name} (ID: {self.id})") # print player stats
        print(f"Games Played: {self.games_played}") 
        print(f"Total Time Played: {self.total_time_played} seconds")
        print("High Scores:")
        for difficulty, score in self.high_scores.items(): # print high scores
            if score is not None:
                print(f"  {difficulty}: {score} attempts")
            else:
                print(f"  {difficulty}: No high score yet")
        print() # newline


class Run:
    @staticmethod
    def start():
        print(Config.starttext) # print start text
        
        while True:
            name = input("Enter your name: ").strip() # get player name
            if name:
                player = Player(name) # create player object
                break
            else:
                print("Name cannot be empty. Please enter your name.")

        while True:
            game = Game(player) # create game object
            game.difficulty() 
            game.play() 
            game.end_game()
            game.rng_reset()

            choice = input("Play again? (y/n): ").lower() # ask to play again
            if choice == 'n':
                print("Thanks for playing!")
                player.stats()
                break
            elif choice != 'y':
                print("Invalid input. Exiting game.")
                player.stats()
                break

if __name__ == "__main__":
    Run.start() # start the game
