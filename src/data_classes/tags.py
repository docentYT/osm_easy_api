class Tags(dict):
    # def __init__(self):
    #     super().__init__()

    def add(self, k:str, v:str):
        """Adds key=value tag to Tags list.

        Args:
            k (str): key
            v (str): value

        Raises:
            ValueError: "Tag already exist!" if Tags already contains k (key). 
        """
        if k in self: raise ValueError("Tag already exist!")
        tag = dict({k: v})
        self.update(tag)

    def set(self, k:str, v:str):
        """Sets value to key. If key does not exist it will add it.

        Args:
            k (str): key
            v (str): value
        """
        if not k in self: self.add(k, v)
        self[k] = v

    def remove(self, k:str):
        """Standard dict.pop() method.

        Args:
            k (str): key
        """
        self.pop(k)

    # def __getitem__(self, key):
    #     try:
    #         return dict.__getitem__(self, key)
    #     except KeyError:
    #         return None
