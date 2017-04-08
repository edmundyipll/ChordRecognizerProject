from ChordInterval import ChordInterval
from ProgressionBank import ProgressionBank
from ChordAnalyzingTool import ChordAnalyzingTool
import copy

class ProgressionVerifier(object):

	#simulate enum
	class ProgressionFeatures(object):

		PriorOnBeat, PriorAllChordType, PriorChangedBaseline, PriorDominantProgression, TonicChanging = range(5)
		@staticmethod
		def toString(feature=0):
			fList = ['PriorOnBeat', 'PriorAllChordType', 'PriorChangedBaseline', 'PriorDominantProgression', 'TonicChanging']
			return fList[feature]

		#PriorOnBeat				-	Select OnBeat Interval for FIRST priority

		#PriorAllChordType 			-	Select Interval of all IntervalType except Continuous for FIRST priority

		#PriorChangedBaseline		-	Select ChangedBaseline Interval for FIRST priority

		# the above features are mutually exclusive

		#PriorDominantProgression	-	Select Tonic -> Dominant / Dominant -> Tonic for SECOND priority

		#TonicChanging				-	Allow more tonic changing in progression

	def __init__(self, inputList=[]):
		self._inputList = copy.deepcopy(inputList)
		self._pBank = ProgressionBank()
		while len(self._inputList[-1]) == 0:
			self._inputList.pop()

	def verify(self, featureList=[]):

		# handle featureList
		mutuallyExclusiveList = [self.ProgressionFeatures.PriorOnBeat, self.ProgressionFeatures.PriorAllChordType, self.ProgressionFeatures.PriorChangedBaseline]
		if [f in featureList for f in mutuallyExclusiveList].count(True) > 1:
			# take PriorOnBeat as FIRST priority when multiple FIRST priority setting found,
			featureList = [self.ProgressionFeatures.PriorOnBeat] + [f for f in featureList if f not in mutuallyExclusiveList]
		featureList.sort()

		print [self.ProgressionFeatures.toString(f) for f in featureList]

		# init
		self._invalidResult = {}

		# find starting point interval
		for interval in self.__findAllIntervalByIntervalType(targetIntervalType=[ChordInterval.IntervalType.OnBeat, ChordInterval.IntervalType.AfterBeat, ChordInterval.IntervalType.ChangedBaseline], currentMeasure=0, currentInterval=0):
			interval.debug()
			print ""

	def __recursiveProgression(self, currentMeasure, currentInterval, featureList):

		pass


	def __findAllIntervalByIntervalType(self, targetIntervalType, currentMeasure, currentInterval):
		allIntervalWithLimit = self.__findAllIntervalWithLimit(currentMeasure=currentMeasure, currentInterval=currentInterval)
		intervalList = []
		for interval in allIntervalWithLimit:
			for intervalType in interval.intervalType:
				if intervalType in targetIntervalType:
					intervalList.append(interval)
					break
		return intervalList


	def __findAllIntervalWithLimit(self, currentMeasure, currentInterval, barLimit=2):
		if currentMeasure + barLimit > len(self._inputList)-1:
			limit = len(self._inputList)
		elif currentInterval == len(self._inputList[currentMeasure]) - 1:
			# last interval of current measure
			limit = currentMeasure + 3
		else:
			limit = currentMeasure + 2

		intervalList = []
		for measureIndex in range(currentMeasure, limit):
			for interval in self._inputList[measureIndex]:
				if measureIndex == currentMeasure and interval.intervalNo <= currentInterval:
					continue
				intervalList.append(interval)
		return intervalList