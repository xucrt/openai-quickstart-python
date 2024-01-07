
import requests

r = requests.get('https://www.chess.com/game/95905322610')
# print(r.text)
print(r.cookies)
print(r.encoding)

