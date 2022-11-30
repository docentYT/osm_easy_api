class Tags(dict):
    # def __init__(self):
    #     super().__init__()

    def add(self, k:str, v:str):
        if k in self: raise ValueError("Tag already exist!")
        tag = dict({k: v})
        self.update(tag)

    def set(self, k:str, v:str):
        if not k in self: self.add(k, v)
        self[k] = v

    def remove(self, k:str):
        self.pop(k)

    # def __getitem__(self, key):
    #     try:
    #         return dict.__getitem__(self, key)
    #     except KeyError:
    #         return None
