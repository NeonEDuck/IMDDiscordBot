import json

class DataManager:
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