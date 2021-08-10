import json

class DataManager:
    __vote = None

    @classmethod
    def get_vote(self):
        if not self.__vote:
            with open('data/vote.json', 'r', encoding='utf-8') as f:
                self.__vote = json.loads(f.read())
        return self.__vote

    @classmethod
    def set_vote(self, value: dict):
        if type(value) != dict:
            raise ValueError
            
        self.__vote = value
        with open('data/vote.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.__vote, indent=4, separators=(',', ':')))