# all the different api calls will go here
import requests

from . import databases as db

class Twitch:
	'interacting with the twitch api'
	def __init__(self):
		self.clientid='guulhcvqo9djhuyhb2vi56wqnglc351'

	def checkuserexists(self, username):
		pass

	def getfollows(self, username):
		api_url='https://api.twitch.tv/kraken/users/'+username+'/follows/channels?client_id='+self.clientid+'&limit=100'
		r = requests.get(api_url)
		j = r.json()
		data = []
		try:
			for s in j['follows']:
				c = s['channel']
				stream = {
					'name'  : c['display_name'],
					'game'  : c['game'],
					'status': c['status'],
					'url'   : c['url']
					}
				data.append(stream)
			return(data)
		except KeyError:
			return(data)

if __name__ == '__main__':
	l = Twitch()
	data = l.getfollows('rsgloryandgold')
	print(data)
	db.save(data, 'asdf')
