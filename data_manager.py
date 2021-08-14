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

    if not os.path.isfile('data/permission.json'):
        with open('data/permission.json', 'w', encoding='utf-8') as f:
            f.write('{}')

class DataManager:
    if REPLIT:
        @classmethod
        def get_vote(self, title:str, guild_id:Union[str, int]) -> dict:
            return json.loads(db[f'vote_{guild_id}_{title}']) if f'vote_{guild_id}_{title}' in db else None

        @classmethod
        def set_vote(self, title:str, vote_info:dict, guild_id:Union[str, int]) -> None:
            if type(vote_info) != dict:
                raise ValueError
            
            db[f'vote_{guild_id}_{title}'] = json.dumps(vote_info, separators=(',', ':'))

        @classmethod
        def delete_vote(self, title:str, guild_id:Union[str, int]) -> None:
            del db[f'vote_{guild_id}_{title}']

        @classmethod
        def vote_keys(self, guild_id:Union[str, int]) -> List[str]:
            return [re.sub('vote_\d*_', '', title) for title in db.keys() if title.startswith(f'vote_{guild_id}_')]

        @classmethod
        def vote_all_keys(self) -> Tuple[str, List[str]]:
            return [(re.search('vote_(\d*)_.*', title)[1], re.sub('vote_\d*_', '', title)) for title in db.keys() if title.startswith(f'vote_')]

        # Permission

        @classmethod
        def get_permission(self, guild_id:Union[str, int]) -> dict:
            return json.loads(db[f'perm_{guild_id}']) if f'perm_{guild_id}' in db else None

        @classmethod
        def set_permission(self, perm_info:dict, guild_id:Union[str, int]) -> None:
            if type(perm_info) != dict:
                raise ValueError
            
            db[f'perm_{guild_id}'] = json.dumps(perm_info, separators=(',', ':'))

        @classmethod
        def delete_permission(self, guild_id:Union[str, int]) -> None:
            del db[f'perm_{guild_id}']

    else:
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            __vote = json.loads(f.read())

        @classmethod
        def get_vote(self, title:str, guild_id:Union[str, int]) -> dict:
            return self.__vote.get(f'{guild_id}_{title}', None)

        @classmethod
        def set_vote(self, title:str, vote_info: dict, guild_id:Union[str, int]) -> None:
            if type(vote_info) != dict:
                raise ValueError
            
            self.__vote[f'{guild_id}_{title}'] = vote_info
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__vote, indent=4, separators=(',', ':')))

        @classmethod
        def delete_vote(self, title:str, guild_id:Union[str, int]) -> None:
            del self.__vote[f'{guild_id}_{title}']
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__vote, indent=4, separators=(',', ':')))

        @classmethod
        def vote_keys(self, guild_id:Union[str, int]) -> List[str]:
            return [re.sub('\d*_', '', title) for title in self.__vote.keys() if title.startswith(f'{guild_id}_')]

        @classmethod
        def vote_all_keys(self) -> Tuple[str, List[str]]:
            return [(re.search('(\d*)_.*', title)[1], re.sub('\d*_', '', title)) for title in self.__vote.keys()]

        # Permission

        with open('data/permission.json', 'r', encoding='utf-8') as f:
            __perm = json.loads(f.read())

        @classmethod
        def get_permission(self, guild_id:Union[str, int]) -> dict:
            return self.__perm.get(str(guild_id), None)

        @classmethod
        def set_permission(self, perm_info:dict, guild_id:Union[str, int]) -> None:
            if type(perm_info) != dict:
                raise ValueError
            
            self.__perm[str(guild_id)] = perm_info
            with open('data/permission.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__perm, indent=4, separators=(',', ':')))

        @classmethod
        def delete_permission(self, guild_id:Union[str, int]) -> None:
            if str(guild_id) in self.__perm:
                del self.__perm[str(guild_id)]
            with open('data/permission.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.__perm, indent=4, separators=(',', ':')))