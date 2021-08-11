from replit import db
import json
import os
from variable import REPLIT

if not REPLIT:
    if not os.path.isdir('data'):
        os.mkdir('data')

    if not os.path.isfile('data/vote.json'):
        with open('data/vote.json', 'w', encoding='utf-8') as f:
            f.write('{}')

class DataManager:
    if REPLIT:
        @classmethod
        def get_vote(self, title:str) -> dict:
            return json.loads(db[f'vote_{title}']) if f'vote_{title}' in db else None

        @classmethod
        def set_vote(self, title:str, vote_info: dict):
            if type(vote_info) != dict:
                raise ValueError
            
            db[f'vote_{title}'] = json.dumps(vote_info, separators=(',', ':'))

        @classmethod
        def delete_vote(self, title:str):
            del db[f'vote_{title}']

        @classmethod
        def vote_keys(self) -> list:
            return [title[5:] for title in db.keys()]

    else:
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            __vote = json.loads(f.read())

        @classmethod
        def get_vote(self, title:str) -> dict:
            return self.__vote[title] if title in self.__vote else None

        @classmethod
        def set_vote(self, title:str, vote_info: dict):
            if type(vote_info) != dict:
                raise ValueError
            
            self.__vote[title] = vote_info
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__vote, indent=4, separators=(',', ':')))

        @classmethod
        def delete_vote(self, title:str):
            del self.__vote[title]
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__vote, indent=4, separators=(',', ':')))

        @classmethod
        def vote_keys(self) -> list:
            return self.__vote.keys()