# Write your code here
import json
import os.path
from io import StringIO
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--import_from')
parser.add_argument('--export_to')
args = parser.parse_args()


class FlashCard:
    list_of_flashcards = []
    mem_buffer = StringIO()

    def __init__(self, in_term, in_definition, in_mistakes=0):
        self.term = in_term
        self.definition = in_definition
        self.mistakes = in_mistakes

    def __str__(self):
        return f'Card:\t{self.term}\nDefinition:\t{self.definition}\nMistakes:\t{self.mistakes}'

    def check_answer(self, in_str):
        if in_str == self.definition:
            FlashCard.print_and_log('Correct!')
        else:
            self.mistakes += 1
            correct_term = FlashCard.search_correct_term(in_str)
            if correct_term:
                FlashCard.print_and_log(
                    f'Wrong. The right answer is "{self.definition}", but your definition is correct for "{correct_term}.')
            else:
                FlashCard.print_and_log(f'Wrong. The right answer is "{self.definition}".')

    @staticmethod
    def print_and_log(string):
        if string is not None:
            FlashCard.mem_buffer.read()
            FlashCard.mem_buffer.write(string + '\n')
        print(string)

    @staticmethod
    def input_and_log(string):
        FlashCard.print_and_log(string)
        in_input = input()
        FlashCard.mem_buffer.read()
        FlashCard.mem_buffer.write(in_input + '\n')
        return in_input

    @staticmethod
    def save_log(file_name):
        with open(file_name, 'w', encoding='utf-8') as log:
            for line in FlashCard.mem_buffer.getvalue():
                log.write(line)
        print('The log has been saved.')

    @staticmethod
    def search_correct_term(in_definition):
        for flashcard in FlashCard.list_of_flashcards:
            if flashcard.definition == in_definition:
                return flashcard.term
        return None

    @staticmethod
    def search(type_c, in_str):
        for flashcard in FlashCard.list_of_flashcards:
            if type_c == 't':
                if flashcard.term == in_str:
                    return flashcard.term
            elif type_c == 'd':
                if flashcard.definition == in_str:
                    return flashcard
        return None

    @staticmethod
    def search_hardest():
        higher = 0
        for flashcard in FlashCard.list_of_flashcards:
            if flashcard.mistakes > higher:
                higher = flashcard.mistakes
        if higher:
            hardest_card = [flashcard for flashcard in FlashCard.list_of_flashcards if flashcard.mistakes == higher]
            if len(hardest_card) > 1:
                hardest_list = [flashcard.term for flashcard in hardest_card]
                FlashCard.print_and_log(f'''The hardest cards are "{'", "'.join(hardest_list)}".''')
            else:
                FlashCard.print_and_log(
                    f'The hardest card is "{hardest_card[0].term}". You have {hardest_card[0].mistakes} errors answering it.')
        else:
            FlashCard.print_and_log('There are no cards with errors.')

    @staticmethod
    def reset_stats():
        for card in FlashCard.list_of_flashcards:
            card.mistakes = 0
        FlashCard.print_and_log('Card statistics have been reset.')

    @staticmethod
    def add():
        # number_of_flashcards = int(input('Input the number of cards:\n'))
        # for i in range(number_of_flashcards):
        card = FlashCard.input_and_log(f'The term for card:')
        while FlashCard.search('t', card):
            card = input(f'The term "{card}" already exists. Try again:')
        definition = FlashCard.input_and_log(f'The definition for card:')
        while FlashCard.search('d', definition):
            definition = FlashCard.input_and_log(f'The definition "{definition}" already exists. Try again:')
        flashcard = FlashCard(card, definition)
        FlashCard.list_of_flashcards.append(flashcard)
        FlashCard.print_and_log(FlashCard.save(flashcard, 'flashcards.json'))

    @staticmethod
    def remove(term):
        if FlashCard.search('t', term):
            for flashcard in FlashCard.list_of_flashcards:
                if flashcard.term == term:
                    FlashCard.list_of_flashcards.remove(flashcard)
                    FlashCard.print_and_log('The card has been removed.')
                    break
        else:
            FlashCard.print_and_log(f'Can\'t remove "{term}": there is no such card.')

    @staticmethod
    def load(file_name):
        if os.path.isfile(file_name):
            n_cards_loaded = 0
            with open(file_name, 'r') as file:
                data = json.load(file)
                for k, v in data['flashcards'].items():
                    if FlashCard.search('t', k):
                        FlashCard.search.definition = v['def']
                        FlashCard.search.mistakes = v['mistake_number']
                        n_cards_loaded += 1
                    else:
                        card = FlashCard(k, v['def'], v['mistake_number'])
                        FlashCard.list_of_flashcards.append(card)
                        n_cards_loaded += 1
            FlashCard.print_and_log(f'{n_cards_loaded} cards have been loaded')
        else:
            FlashCard.print_and_log('File not found.')

    @staticmethod
    def write_json(data, filename):
        with open(filename, 'w+') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def save(flashcard, file_name):
        data = {flashcard.term: {'def': flashcard.definition, 'mistake_number': flashcard.mistakes}}
        if not os.path.isfile(file_name):
            first_data = {'flashcards': data}
            FlashCard.write_json(first_data, file_name)
        else:
            with open(file_name, 'r') as json_file:
                data_from_file = json.load(json_file)
                temp = data_from_file.get('flashcards')
                temp.update(data)
            FlashCard.write_json(data_from_file, filename=file_name)
        return f'The pair ("{flashcard.term}":"{flashcard.definition}") has been added.'

    @staticmethod
    def export(file_name):
        saved_cards = 0
        for card in FlashCard.list_of_flashcards:
            FlashCard.save(card, file_name)
            saved_cards += 1
        FlashCard.print_and_log(f'{saved_cards} cards have been saved.')

    @staticmethod
    def ask():
        times = int(FlashCard.input_and_log('How many times to ask?'))
        i = 0
        index = 0
        while i < times:
            if index >= len(FlashCard.list_of_flashcards):
                index = 0
            FlashCard.print_and_log(f'Print the definition of "{FlashCard.list_of_flashcards[index].term}":')
            FlashCard.list_of_flashcards[index].check_answer(FlashCard.input_and_log(''))
            i += 1
            index += 1

    @staticmethod
    def menu():
        if args.import_from:
            FlashCard.load(args.import_from)
        action = ''
        while action != 'exit':
            action = FlashCard.input_and_log(
                'Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):')
            if action == 'add':
                FlashCard.add()
            if action == 'remove':
                FlashCard.remove(FlashCard.input_and_log('Which card?'))
            if action == 'import':
                if args.import_from:
                    FlashCard.load(args.import_from)
                else:
                    FlashCard.load(FlashCard.input_and_log('File name:'))
            if action == 'export':
                if args.export_to:
                    FlashCard.export(args.export_to)
                else:
                    FlashCard.export(FlashCard.input_and_log('File name:'))
            if action == 'ask':
                FlashCard.ask()
            if action == 'hardest card':
                FlashCard.search_hardest()
            if action == 'reset stats':
                FlashCard.reset_stats()
            if action == 'log':
                FlashCard.save_log(FlashCard.input_and_log('File name:'))
            if action == 'buffer':
                print(FlashCard.mem_buffer.getvalue())
            if action == 'exit':
                if args.export_to:
                    FlashCard.export(args.export_to)
        FlashCard.print_and_log('Bye bye!')


FlashCard.menu()


