import pickle
from random import randint
from datetime import datetime

# TODO : Make sure the days stop rolling over

ALL_GAME_METAS = []
ALL_MOVES = []
ALL_DECKS = {}


def save_data(file_name="decks.dat"):
    with open(file_name, "wb+") as file:
        global ALL_GAME_METAS, ALL_MOVES, ALL_DECKS
        pickle.dump((ALL_GAME_METAS, ALL_MOVES, ALL_DECKS), file)


def load_data(file_name="decks.dat"):
    with open(file_name, "rb") as file:
        global ALL_GAME_METAS, ALL_MOVES, ALL_DECKS
        ALL_GAME_METAS, ALL_MOVES, ALL_DECKS = pickle.load(file)


class GameMeta:
    def __init__(self, tags={}):
        self.Tags = tags


class Move:
    def __init__(self, game_meta=None, move_num=0, player=False, previous_move=None, move_text="", comment="", next_=None):
        self.GameMeta = game_meta
        self.MoveNumber = move_num
        self.Player = player
        self.PreviousMove = previous_move
        self.MoveText = move_text
        self.Comment = comment
        self.Next = next_

    def add_move(self, new_move, insert_location=-1):
        if not self.Next:
            self.Next = [new_move]
        else:
            if insert_location == -1:
                insert_location = len(self.Next)
            self.Next.insert(insert_location, new_move)

    def quiz_line(self, opponent=False, comments=True):
        if self.GameMeta.Tags["RAV"] != "Main Line":
            sequence = self.GameMeta.Tags["RAV"].split(".")
        current_move = self
        while current_move and current_move.PreviousMove:
            current_move = current_move.PreviousMove

        i = 0

        if opponent:
            if current_move.MoveNumber == 0:
                if comments:
                    print(self.Comment)
                if self.GameMeta.Tags["RAV"] != "Main Line":
                    current_move = current_move.Next[int(sequence[i])]
                else:
                    current_move = current_move.Next[0]
            print(current_move.MoveNumber, current_move.MoveText)
            if comments:
                print(current_move.Comment)
            i += 1

        while (self.GameMeta.Tags["RAV"] == "Main Line" or i < len(sequence)) and current_move != self:
            while True:
                user_move = ""
                while not user_move:
                    if opponent:
                        user_move = input(str(current_move.MoveNumber) + "... ")
                    else:
                        user_move = input(str(current_move.MoveNumber + 1) + ". ")

                if user_move == "{{quit}}":
                    return -1

                if not current_move.Next:
                    print("Line Completed")
                    return 3

                if self.GameMeta.Tags["RAV"] != "Main Line" and current_move.Next[int(sequence[i])].MoveText == user_move:
                    break
                elif self.GameMeta.Tags["RAV"] == "Main Line" and current_move.Next[0].MoveText == user_move:
                    break
                else:
                    j = 0
                    while j < len(current_move.Next):
                        if current_move.Next[j].MoveText == user_move:
                            break
                        j += 1

                    if j < len(current_move.Next):
                        print("Move entered is in deck, but I'm look for a different one. Please try again.")
                        continue
                    else:
                        print("Move entered doesn't exist in deck.")
                        if self.GameMeta.Tags["RAV"] == "Main Line":
                            print("Expected Move:", current_move.Next[0].MoveText)
                        else:
                            print("Expected Move: ", current_move.Next[int(sequence[i])].MoveText)
                        return 0

            if self.GameMeta.Tags["RAV"] != "Main Line":
                current_move = current_move.Next[int(sequence[i])]
            else:
                current_move = current_move.Next[0]

            i += 1
            if comments:
                print(current_move.Comment)

            if current_move.Next and len(current_move.Next) > 0:
                if self.GameMeta.Tags["RAV"] != "Main Line":
                    current_move = current_move.Next[int(sequence[i])]
                else:
                    current_move = current_move.Next[0]
                i += 1
            else:
                print("Line Completed")
                return 3

            if current_move and current_move.Player:
                print(str(current_move.MoveNumber) + "... " + current_move.MoveText)
            else:
                print(str(current_move.MoveNumber) + ". " + current_move.MoveText)
            if comments:
                print(current_move.Comment)

            if not current_move.Next:
                print("Line Completed")
                return 3


class FlashCard:
    def __init__(self, value):
        self.RepetitionNumber = 0
        self.Correct = 0
        self.Incorrect = 0
        self.Graduated = False
        self.EasinessFactor = 2.5
        self.Interval = 0
        self.LastQuizzed = datetime.now()
        self.Created = datetime.now()
        self.Value = value

    def sm2(self, q):
        # q = user grade
        # n = repetition number
        # ef = easiness factor
        # i = interval

        if q >= 3:
            if self.RepetitionNumber == 0:
                self.Interval = 24*60*60
            elif self.RepetitionNumber == 1:
                self.Interval = 26*60*60*6
            else:
                self.Interval = self.Interval * self.EasinessFactor

            self.EasinessFactor = self.EasinessFactor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

            if self.EasinessFactor < 1.3:
                self.EasinessFactor = 1.3

            self.RepetitionNumber += 1

        else:
            self.RepetitionNumber = 0
            self.Interval = 0

    def quiz_card(self):
        q = self.Value.quiz_line()
        if q == -1:
            return -1
        self.LastQuizzed = datetime.now()
        if self.Graduated:
            if q >= 3:
                self.Correct += 1
            else:
                self.Incorrect += 1
            self.sm2(q)
        else:
            if q >= 3:
                self.Correct += 1
                self.RepetitionNumber += 1
            else:
                self.Incorrect += 1
                self.RepetitionNumber = 0
            if q == 5 or self.RepetitionNumber >= 4:
                print("Card Graduated: Interval =  1 Day")
                self.Graduated = True
                self.RepetitionNumber = 0
                self.sm2(q)
            elif self.RepetitionNumber == 3:
                print("Almost Learned: Interval = 1 hour")
                self.Interval = 3600
            elif self.RepetitionNumber == 2:
                print("Getting There: Interval = 10 Minutes")
                self.Interval = 600
            elif self.RepetitionNumber == 1:
                print("Just Starting Out: Interval = 1 Minute")
                self.Interval = 60
            else:
                print("Try Again")
                self.Interval = 0
        return q


class FlashCardDeck:
    def __init__(self, cards=None):
        if not cards:
            self.Cards = []
        else:
            self.Cards = cards

    def add_to_deck(self, card):
        self.Cards.insert(0, card)

    def check_for_cards_due(self):
        cards_due = []
        current_time = datetime.now()
        for card in self.Cards:
            seconds_elapsed = (current_time - card.LastQuizzed).days * 86400 + (current_time - card.LastQuizzed).seconds
            if seconds_elapsed > card.Interval:
                cards_due.append(card)
        return cards_due


def parse_game_tags(game_tags):
    tag_start = 0
    tags = {}
    while tag_start < len(game_tags):
        if game_tags[tag_start] == "[":
            tag_end = tag_start
            while tag_end < len(game_tags) and game_tags[tag_end] != ']':
                tag_end += 1
            if tag_end >= len(game_tags):
                return
            tag_start += 1
            key_end = tag_start
            while game_tags[key_end] != '"':
                key_end += 1
            key = game_tags[tag_start:key_end - 1]
            key_end += 1
            tag_start = key_end
            while game_tags[key_end] != '"':
                key_end += 1
            value = game_tags[tag_start: key_end]
            tags.setdefault(key, value)
        else:
            tag_start += 1

    tags.setdefault("RAV", "Main Line")
    return tags


def get_move_rav(move):
    last_move = move
    current_move = move.PreviousMove
    sequence = []

    while current_move and current_move.PreviousMove:
        i = 0
        while i < len(current_move.Next) and current_move.Next[i] != last_move:
            i += 1
        sequence.insert(0, i)
        last_move = current_move
        current_move = current_move.PreviousMove

    sequence.insert(0, 0)
    non_zeros = 0

    for i in sequence:
        if i != 0:
            non_zeros += 1
            break

    if non_zeros == 0:
        return "Main Line"

    else:
        sequence_text = ""
        for i in sequence:
            sequence_text += str(i) + "."
        return sequence_text[0: len(sequence_text) - 1]



def get_comment(move_text, starting_i):
    if move_text[starting_i] != '{':
        return None, starting_i

    ending_i = starting_i

    while ending_i < len(move_text) and move_text[ending_i] != "}":
        ending_i += 1

    return [move_text[starting_i + 1: ending_i], ending_i + 1]


def print_move (move):
    if not move.Player:
        print(move.MoveNumber, ". ", move.MoveText)
    else:
        print(move.MoveNumber, "... ", move.MoveText)


def print_line(tail):
    moves = []
    current = tail
    while current.PreviousMove:
        moves.insert(0, current)
        current = current.PreviousMove

    for move in moves:
        print_move(move)


def parse_move_text_to_deck(game_meta, move_text, file_name=""):
    head = Move(game_meta, comment=file_name)
    ALL_MOVES.append(head)
    deck = FlashCardDeck()
    move_stack = [head]

    i = 0

    while i < len(move_text):
        # Skipping white space

        comment, i = get_comment(move_text, i)
        if comment:
            move_stack[-1].Comment = comment

        while i < len(move_text) and move_text[i] == ' ':
            i += 1
        if move_text[i:i + len(game_meta.Tags["Result"])] == game_meta.Tags["Result"]:
            while move_stack:
                deck.add_to_deck(FlashCard(move_stack[-1]))
                move_stack.pop()
            return head, deck
        comment, i = get_comment(move_text, i)
        if comment:
            move_stack[-1].Comment = comment

        if move_text[i] == '(':
            i += 1
            move_stack.append(move_stack[-1].PreviousMove)
            continue

        j = i

        new_move = Move(move_stack[-1].GameMeta,
                        previous_move=move_stack[-1])

        ALL_MOVES.append(new_move)
        move_stack[-1].add_move(new_move)
        move_stack.pop()

        rav = get_move_rav(new_move)


        if rav != new_move.GameMeta.Tags["RAV"]:
            new_meta = GameMeta()
            new_meta.Tags = game_meta.Tags.copy()
            new_meta.Tags["RAV"] = rav
            new_move.GameMeta = new_meta
            ALL_GAME_METAS.append(new_meta)

        move_stack.append(new_move)

        if move_text[i] == '(':
            i += 1
            move_stack.append(move_stack[-1].PreviousMove)
            continue

        while j < len(move_text) and move_text[j].isdigit():
            j += 1

        move_stack[-1].MoveNumber = int(move_text[i:j])

        i = j

        period_count = 0

        while move_text[i] == '.':
            period_count += 1
            i += 1

        if period_count <= 1:
            move_stack[-1].Player = False
        else:
            move_stack[-1].Player = True

        comment, i = get_comment(move_text, i)
        if comment:
            move_stack[-1].Comment = comment

        while i < len(move_text) and move_text[i] == ' ':
            i += 1

        j = i
        while j < len(move_text) and move_text[j] != ' ':
            if move_text[j] == ')':
                move_stack[-1].MoveText = move_text[i:j]
                deck.add_to_deck(FlashCard(move_stack[-1]))
                move_stack.pop()
                break
            else:
                j += 1
        if move_text[j] == ')':
            i = j + 1
            while move_text[i] == ')':
                move_stack.pop()
                i += 1
            continue
        move_stack[-1].MoveText = move_text[i:j]
        i = j + 1
        comment, i = get_comment(move_text, i)
        if comment:
            move_stack[-1].Comment = comment

        while i < len(move_text) and move_text[i] == ' ':
            i += 1

        if move_text[i] == '(':
            i += 1
            move_stack.append(move_stack[-1].PreviousMove)
            continue

        if move_text[i] == ')':
            i += 1
            deck.add_to_deck(FlashCard(move_stack[-1]))
            move_stack.pop()
            continue

        elif not move_text[i].isdigit():
            new_move = Move(move_stack[-1].GameMeta,
                 move_stack[-1].MoveNumber,
                 player=True,
                 previous_move=move_stack[-1])

            ALL_MOVES.append(new_move)

            move_stack[-1].add_move(new_move)
            move_stack.pop()

            move_stack.append(new_move)

            j = i
            while j < len(move_text) and move_text[j] != ' ':
                j += 1

            move_stack[-1].MoveText = move_text[i:j]
            i = j + 1
            comment, i = get_comment(move_text, i)
            if comment:
                move_stack[-1].Comment = comment

            while i < len(move_text) and move_text[i] == ' ':
                i += 1

            if i >= len(move_text):
                while move_stack:
                    deck.add_to_deck(FlashCard(move_stack[-1]))
                    move_stack.pop()
                return head, deck
            if move_text[i] == '(':
                i += 1
                move_stack.append(move_stack[-1].PreviousMove)
                continue

            if move_text[i] == ')':
                i += 1
                deck.add_to_deck(FlashCard(move_stack[-1]))
                move_stack.pop()
                continue

    while move_stack:
        deck.add_to_deck(FlashCard(move_stack[-1]))
        move_stack.pop()
    return head, deck


def load_game_from_file(file_name):
    games = []

    tag = True
    started = False

    with open(file_name, "r", encoding='utf-8-sig') as pgn_file:
        line = pgn_file.readline()
        while line:
            if not tag:
                if line and line[0] == '[' and line[1] != '%':
                    tag = True
                    started = False
                else:
                    games[-1][1] += line.replace('\n', ' ')
            else:
                if line == "\n":
                    tag = False
                    started = False
                else:
                    if not started:
                        games.append([line.strip("\n"), ""])
                        started = True
                    else:
                        games[-1][0] += line.strip("\n")
            line = pgn_file.readline()
    return games

def main():
    print("Welcome to the PGN Teacher")
    file_name = "decks.dat"
    current_deck = None
    while True:
        try:
            with open("decks.dat", "rb") as file:
                load_data()
                break
        except FileNotFoundError:
            ui = input("'" + file_name + "' doesn't exist, would you like to load another save file: (y)es/(n)o")
            if ui[0] == 'n':
                break
            else:
                file_name = input("Enter name of other file: ")

    while True:
        ui = input("Enter a command (use 'commands' to see your options): ")
        if ui == "commands":
            print("The following commands are available: ")
            print("'ND' or 'New Deck': To create a new deck from provided pgn file")
            print("'LiD' or 'List Decks': To list existing decks")
            print("'Sel' or 'Select Deck': To select a deck")
            print("'SD' or 'Study Deck': To study current deck")
            print("'DI' or 'Deck Information': To see information on deck")
            print("'S' or 'Save': Save all current data")
            print("'Q' or 'Quit': Quit program")

        if ui == "ND" or ui == "New Deck":
            file_name = input("Enter File Name: ")
            games = load_game_from_file(file_name)
            for game in games:
                meta_tags = parse_game_tags(game[0])
                head, deck = parse_move_text_to_deck(GameMeta(meta_tags), game[1], file_name)
                ui = input("Enter Deck Name for: " + head.GameMeta.Tags["White"] + " v " + head.GameMeta.Tags["Black"] +
                           " (or enter '{{skip}}' to skip game): ")
                if ui != "{{skip}}":
                    ALL_DECKS[ui] = deck
                head = None
                deck = None

        if ui == "LiD" or ui == "List Decks":
            for key in ALL_DECKS.keys():
                print(key)

        if ui == "Sel" or ui == "Select Deck":
            ui = input("Enter deck name: ")
            if ui in ALL_DECKS.keys():
                current_deck = ALL_DECKS[ui]
                print(current_deck)
            else:
                print("Deck given doesn't exist")

        if ui == "SD" or ui == "Study Deck":
            print(current_deck)
            if not current_deck:
                print("Please select a deck first")
            else:
                cards_due = current_deck.check_for_cards_due()
                if not cards_due:
                    print("No cards need to be studied now")
                else:
                    while cards_due:
                        for card in cards_due:
                            print("Graduated:", card.Graduated)
                            print("Interval:", card.Interval)
                            curr_time = datetime.now()
                            print((curr_time - card.LastQuizzed).seconds)
                            flag = card.quiz_card()
                            print("Flag:", flag)
                            if 3 > flag > -1:
                                ui = input("Would you like to try again? (y/n): ")
                                while ui == "y":
                                    flag = card.quiz_card()
                                    print("Flag:", flag)
                                    if 3 > flag > -1:
                                        ui = input("Would you like to try again? (y/n): ")
                                    else:
                                        ui = ""
                            if flag == -1:
                                cards_due = None
                                break
                            cards_due = current_deck.check_for_cards_due()

        if ui == "S" or ui == "Save":
            print("Saving Data")
            save_data()

        if ui == "Q" or ui == "Quit":
            ui = input("Would you like to save first?: y/n")
            if ui == "y":
                print("Saving Data")
                save_data()
            quit()

        if ui == "DI" or ui == "Deck Information":
            if not current_deck:
                print("Please select a deck first")
            else:
                deck_len = len(current_deck.Cards)
                cards_graduated = 0
                worst_card = current_deck.Cards[0]
                worst_card_stats = 1
                cards_due = len(current_deck.check_for_cards_due())

                for card in current_deck.Cards:
                    print(card.Value.GameMeta.Tags["RAV"])
                    print("Card Graduated:", card.Graduated)
                    print("Card Interval:", card.Interval)
                    if card.Graduated:
                        cards_graduated += 1

                    if card.Incorrect and card.Correct/(card.Correct + card.Incorrect) < worst_card_stats:
                        worst_card = card
                        worst_card_stats = card.Correct/(card.Correct + card.Incorrect)

                print("Size of Deck:", deck_len)
                if not cards_graduated:
                    per_graduated = 0
                else:
                    per_graduated = cards_graduated/deck_len * 100
                print("% Graduated: ", per_graduated)
                print("Worst Card:", worst_card.Value.GameMeta.Tags["RAV"], "Correct %:", worst_card_stats * 100, "of",
                      worst_card.Correct + worst_card.Incorrect, " attempts")

if __name__ == '__main__':
    main()
