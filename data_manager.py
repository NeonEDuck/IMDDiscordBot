from replit import db
from typing import Union, List, Tuple, Dict, Any
import json
import os
import re
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
        def get_vote(self, title:str, guild_id:Union[str, int]) -> dict:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            return json.loads(db[f'vote_{guild_id}_{title}']) if f'vote_{guild_id}_{title}' in db else None

        @classmethod
        def set_vote(self, title:str, vote_info: dict, guild_id:Union[str, int]) -> None:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            if type(vote_info) != dict:
                raise ValueError
            
            db[f'vote_{guild_id}_{title}'] = json.dumps(vote_info, separators=(',', ':'))

        @classmethod
        def delete_vote(self, title:str, guild_id:Union[str, int]) -> None:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            del db[f'vote_{guild_id}_{title}']

        @classmethod
        def vote_keys(self, guild_id:Union[str, int]) -> List[str]:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            return [re.sub('vote_\d*_', '', title) for title in db.keys() if title.startswith(f'vote_{guild_id}_')]

        @classmethod
        def vote_all_keys(self) -> Tuple[str, List[str]]:
            return [(re.search('vote_(\d*)_.*', title)[1], re.sub('vote_\d*_', '', title)) for title in db.keys() if title.startswith(f'vote_')]

    else:
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            __vote = json.loads(f.read())

        @classmethod
        def get_vote(self, title:str, guild_id:Union[str, int]) -> dict:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            return self.__vote[f'{guild_id}_{title}'] if f'{guild_id}_{title}' in self.__vote else None

        @classmethod
        def set_vote(self, title:str, vote_info: dict, guild_id:Union[str, int]) -> None:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            if type(vote_info) != dict:
                raise ValueError
            
            self.__vote[f'{guild_id}_{title}'] = vote_info
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__vote, indent=4, separators=(',', ':')))

        @classmethod
        def delete_vote(self, title:str, guild_id:Union[str, int]) -> None:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            del self.__vote[f'{guild_id}_{title}']
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__vote, indent=4, separators=(',', ':')))

        @classmethod
        def vote_keys(self, guild_id:Union[str, int]) -> List[str]:
            if type(guild_id) == int:
                guild_id = str(guild_id)
            return [re.sub('\d*_', '', title) for title in self.__vote.keys() if title.startswith(f'{guild_id}_')]

        @classmethod
        def vote_all_keys(self) -> Tuple[str, List[str]]:
            return [(re.search('(\d*)_.*', title)[1], re.sub('\d*_', '', title)) for title in self.__vote.keys()]