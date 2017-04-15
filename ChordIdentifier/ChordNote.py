import json
class ChordNote(object):

	@property
	def frequency(self):
		return self._frequency

	@property
	def name(self):
		return self._name

	@property
	def offset(self):
		return self._offset

	@property
	def endTime(self):
		return self._endTime

	@property
	def measure(self):
		return self._measure

	def __init__(self, name=None, frequency=None, offset=None, endTime=None, measure=None):
		self._name = name.replace("-", "b")
		self._frequency = frequency
		self._offset = offset
		self._endTime = endTime
		self._measure = measure

	def debugMessage(self):
		return str(self._name)