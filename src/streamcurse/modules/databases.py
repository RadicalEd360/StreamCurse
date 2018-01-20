import pickle
import os

#	'Streamlink-curses functions for interacting with its databases'

""" db.create(filename)
creates an empty database """
def create(dbfile):
	data = []
	with open(dbfile, 'wb') as handle:
		pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
	return(True)

""" data = db.load(filename)
takes a filename, unpickles the data and returns it """
def load(dbfile):
	with open(dbfile, 'rb') as handle:
		data = pickle.load(handle)
	return(data)

""" db.save(dict, filename)
takes a dictionary and a filename and pickles it to file """
def save(dick, dbfile):
	with open(dbfile, 'wb') as handle:
		pickle.dump(dick, handle, protocol=pickle.HIGHEST_PROTOCOL)

""" db.addto(dict, filename)
takes a dict, and appends it to database """
def addto(dick, dbfile):
	with open(dbfile, 'rb') as handle:
		database = pickle.load(handle)

	for v in dick:
		database.append(v)

	with open(dbfile, 'wb') as handle:
		pickle.dump(database, handle, protocol=pickle.HIGHEST_PROTOCOL)

""" db.delfrom(dict, filename)
takes a dict of streams, for each stream, if its in the database remove it """
def delfrom(dick, dbfile):
	data = load(dbfile)
	retva = 0
	if data:
		for stream in dick:
			try:
				data.remove(stream)
				print('deleting: {0}'.format(stream))
			except:
				retva += 1
				print('was not in db: {0}'.format(stream))
	data = save(data, dbfile)
	return(retva)

def rmdb(dbfile):
	if os.path.exists(dbfile):
		os.remove(dbfile)

# delete all streams with a value matching ?

""" exportdata = db.exporting(filename, type)
exports the database as type, returns the content """
def exporting(dbfile, type):
	pass

""" db.importing(filename, type, data)
opposite of exporting """
def importing(dbfile, type, data):
	pass

if __name__ == "__main__":
	exit()
