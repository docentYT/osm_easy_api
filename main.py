from src import Api

api = Api()
print(api.misc.versions())
print(api.misc.capabilities())

api_master = Api("https://api.openstreetmap.org")
api_master.misc.get_map_in_bbox(21.104935, 52.245671, 21.106024, 52.246393)