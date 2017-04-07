import csv
class ProgressionBank(object):

	_source = "progression.csv"
	def __readCSV(self):
		self._bank = {}
		with open(self._source, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			for row in reader:
				if row[0] == "KEY":
					self._keys = list(row)
				else:
					self._bank[row[0]] = list(row)

	def verify(self, before=None, after=None):
		if before is None or after is None or before == "" or after == "":
			return "NULL"
		if before in self._bank:
			try:
				index = self._keys.index(after)
			except ValueError:
				index = self._keys.index(before)
			return self._bank[before][index]
		return "NULL"

	def printAllKeys(self):
		for ind, key in enumerate(self._keys):
			if ind is not 0:
				print key

	def possibleNext(self, before=None):
		if before is None or before == "":
			return []
		if before in self._bank:
			indexes = [i for i, key in enumerate(self._bank[before]) if key == 'Yes']
			return [key for i, key in enumerate(self._keys) if i in indexes ]
		return []

	def __init__(self):
		self.__readCSV()
