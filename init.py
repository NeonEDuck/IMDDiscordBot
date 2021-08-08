import os

def run():
    if not os.path.isdir('data'):
        os.mkdir('data')

    if not os.path.isfile('data/vote.json'):
        with open('data/vote.json', 'w', encoding='utf-8') as f:
            f.write('{}')