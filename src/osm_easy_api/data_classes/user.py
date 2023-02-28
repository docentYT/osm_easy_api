from typing import Dict

class User():
    def __init__(self,
                id: int | None = None,
                display_name: str | None = None,
                account_created_at: str | None = None,
                description: str | None = None,
                contributor_terms_agreed: bool | None = None,
                img_url: str | None = None,
                roles: list[str] | None = None,
                changesets_count: int | None = None,
                traces_count: int | None = None,
                blocks: Dict[str, Dict[str, int]] | None = None
                # = {
                #     "received": {
                #         "count": 0,
                #         "active": 0
                #     },
                #     "issued": {
                #         "count": 0,
                #         "active": 0
                #     }
                # }
        ):
        self.id = id
        self.display_name = display_name
        self.account_created_at = account_created_at
        self.description = description
        self.contributor_terms_agreed = contributor_terms_agreed
        self.img_url = img_url
        self.roles = roles
        self.changesets_count = changesets_count
        self.traces_count = traces_count
        self.blocks = blocks

    def __str__(self):
        temp = f"{self.__class__.__name__}("
        for k in self.__dict__:
            temp += f"{k} = {getattr(self, k)}, "
        temp += ")"
        return temp
        