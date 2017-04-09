from ChordInterval import ChordInterval
from ProgressionBank import ProgressionBank
from ChordAnalyzingTool import ChordAnalyzingTool
import copy

class ProgressionVerifier(object):

	#simulate enum
	class ProgressionFeatures(object):

		PriorOnBeat, PriorAllIntervalType, PriorChangedBaseline, PriorDominantProgression, TonicChanging = range(5)
		@classmethod
		def toString(self, feature=0):
			fList = ['PriorOnBeat', 'PriorAllIntervalType', 'PriorChangedBaseline', 'PriorDominantProgression', 'TonicChanging']
			return fList[feature]

		@classmethod
		def getFirstPriorityList(self):
			return [self.PriorOnBeat, self.PriorAllIntervalType, self.PriorChangedBaseline]

		#PriorOnBeat				-	Select OnBeat Interval for FIRST priority

		#PriorAllIntervalType 			-	Select Interval of all IntervalType except Continuous for FIRST priority

		#PriorChangedBaseline		-	Select ChangedBaseline Interval for FIRST priority

		# the above features are mutually exclusive

		#PriorDominantProgression	-	Select Tonic -> Dominant / Dominant -> Tonic for SECOND priority

		#TonicChanging				-	Allow more tonic changing in progression

	def __init__(self, inputList=[]):
		self._inputList = copy.deepcopy(inputList)
		self._pBank = ProgressionBank()
		self._analyzingTool = ChordAnalyzingTool()
		while len(self._inputList[-1]) == 0:
			self._inputList.pop()


	def verify(self, featureList=[]):

		# handle featureList
		firstPriorityCnt = len([f for f in self.ProgressionFeatures.getFirstPriorityList() if f in featureList])
		if firstPriorityCnt != 1:
			# take PriorOnBeat as FIRST priority when no or multiple FIRST priority setting found,
			featureList = [self.ProgressionFeatures.PriorOnBeat] + [f for f in featureList if f not in self.ProgressionFeatures.getFirstPriorityList()]
		featureList.sort()

		# init
		self._invalidResult = {}
		resultList = []

		# find starting point interval
		targetTypeList = self.__getTargetTypeListFromFirstPriorityFeature(feature=featureList[0])		
		startingPointIntervalList = []
		touchEnd = False
		measureCnt = 0
		while len(startingPointIntervalList) == 0 and not touchEnd:
			(startingPointIntervalList, touchEnd) = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=measureCnt, startInterval=0, barLimit=2)
			measureCnt += 2
		# for interval in startingPointIntervalList:
		# 	interval.debug()
		# 	print ""
		if len(startingPointIntervalList) == 0:
			print "Could not find starting point in current mode: "+self.ProgressionFeatures.toString(feature[0])
		else:
			startingPoint = startingPointIntervalList[0]
			matchTupleRomanIndex = self._analyzingTool.convertMatchTupleKeyToIndex('roman')
			matchTuplePriorityList = []
			allMatches = self.__getOrderedMatchesDict(interval=startingPoint, totalMatch=True, exactMatch=True, possibleMatch=True)
			for key in sorted(allMatches.keys()):
				matchTuplePriorityList += [matchTuple for matchTuple in allMatches[key] if (matchTuple[matchTupleRomanIndex] == 'I' or matchTuple[matchTupleRomanIndex] == 'V')]
			for key in sorted(allMatches.keys()):
				matchTuplePriorityList += [matchTuple for matchTuple in allMatches[key] if matchTuple not in matchTuplePriorityList]

			# start progression
			for matchTuple in matchTuplePriorityList:
				if startingPoint in self._invalidResult and matchTuple in self._invalidResult[startingPoint]:
					continue
				recursiveResult = self.__recursiveProgression(startingInterval=startingPoint, startingMatch=matchTuple, featureList=featureList)
				if len(recursiveResult) == 0:
					if startingPoint not in self._invalidResult:
						self._invalidResult[startingPoint] = []
					self._invalidResult[startingPoint].append(matchTuple)
				else:
					resultList = recursiveResult
					break
		return resultList


	def __recursiveProgression(self, startingInterval, startingMatch, featureList):

		intervalA = startingInterval
		matchTupleA = startingMatch

		targetTypeList = self.__getTargetTypeListFromFirstPriorityFeature(feature=featureList[0])
		matchTupleRomanIndex = self._analyzingTool.convertMatchTupleKeyToIndex('roman')
		matchTupleTonicIndex = self._analyzingTool.convertMatchTupleKeyToIndex('tonic')

		# check if current interval is the last PriorInterval, if no, progressionBarLimit=2, if yes, progressionBarLimit=3
		targetIntervalWithinThisBar = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=intervalA.measureNo, startInterval=intervalA.intervalNo+1, barLimit=1)[0]
		if len(targetIntervalWithinThisBar) == 0:
			progressionBarLimitA = 3
		else:
			progressionBarLimitA = 2

		(targetIntervalInNextTwoBarsFromA, touchEndA) = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=intervalA.measureNo, startInterval=intervalA.intervalNo+1, barLimit=progressionBarLimitA)
		for i, intervalB in enumerate(targetIntervalInNextTwoBarsFromA):
			totalExactMatches = self.__getOrderedMatchesDict(interval=intervalB, totalMatch=True, exactMatch=True, possibleMatch=False)
			intervalBRomanVList = []
			for key in sorted(totalExactMatches.keys()):
				intervalBRomanVList += [matchTuple for matchTuple in totalExactMatches[key] if matchTuple[matchTupleRomanIndex] == 'V']

			# check if current interval is the last PriorInterval, if no, progressionBarLimit=2, if yes, progressionBarLimit=2
			if i+1 < len(targetIntervalInNextTwoBarsFromA) and targetIntervalInNextTwoBarsFromA[i+1].measureNo == intervalB.measureNo:
				progressionBarLimitB = 2
			else:
				progressionBarLimitB = 3

			(targetIntervalInNextTwoBarsFromB, touchEndB) = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=intervalB.measureNo, startInterval=intervalB.intervalNo+1, barLimit=progressionBarLimitB)
			for matchTupleB in intervalBRomanVList:
				(cnameB, chordTypeB, inverionB, romanB, tonicB, groupNoB) = matchTupleB
				for j, intervalC in enumerate(targetIntervalInNextTwoBarsFromB):
					allMatches = self.__getOrderedMatchesDict(interval=intervalC, totalMatch=True, exactMatch=True, possibleMatch=True)
					sameTonicRomanIList = []
					for key in sorted(allMatches.keys()):
						sameTonicRomanIList += [matchTuple for matchTuple in allMatches[key] if (matchTuple[matchTupleRomanIndex] == 'I' and matchTuple[matchTupleTonicIndex] == tonicB)]
					for matchTupleC in sameTonicRomanIList:
						(cnameC, chordTypeC, inversionC, romanC, tonicC, groupNoC) = matchTupleC
						if self.__isPerfectCadenceProgression(previousChordType=chordTypeB, afterChordType=chordTypeC):
							# examine intervalA to intervalC first
							eqvIntervalCinTonicA = [matchTuple for matchTuple in intervalC.equivalentGroupDict[groupNoC] if matchTuple[matchTupleTonicIndex] == matchTupleA[matchTupleTonicIndex]]
							if len(eqvIntervalCinTonicA):
								
								# next progression with no tonic changed
								recursiveResult = self.__recursiveProgression(startingInterval=intervalC, startingMatch=eqvIntervalCinTonicA[0], featureList=featureList)

								if len(recursiveResult) == 0:
									if intervalC not in self._invalidResult:
										self._invalidResult[intervalC]

							# examine intervalA to intervalB
							eqvIntervalBinTonicA = [matchTuple for matchTuple in intervalB.equivalentGroupDict[groupNoB] if matchTuple[matchTupleTonicIndex] == matchTupleA[matchTupleTonicIndex]]
							if len(eqvIntervalBinTonicA):

								# next progression with tonic changed
								recursiveResult = self.__recursiveProgression(startingInterval=intervalC, startingMatch=matchTupleC, featureList=featureList)

								if len(recursiveResult) == 0:
									if intervalC not in self._invalidResult:
										self._invalidResult[intervalC] = []
									self._invalidResult[intervalC].append(matchTupleC)
								else:
									return [(intervalB, eqvIntervalBinTonicA[0])] + recursiveResult



	def __isPerfectCadenceProgression(self, previousChordType, afterChordType):
		V7toI = previousChordType == "Major 7th" and afterChordType == "Major"
		VtoI = previousChordType == "Major" and afterChordType == "Major"
		vtoi = previousChordType == "Minor" and afterChordType == "Minor"
		vtoI7 = previousChordType == "Minor" and afterChordType == "Major 7th"
		return V7toI or VtoI or vtoi or vtoI7


	def __getOrderedMatchesDict(self, interval, totalMatch=True, exactMatch=True, possibleMatch=True):
		orderedMatchesDict = {}
		totalMatchList = []
		exactMatchList = []
		possibleMatchList = []
		for tonic in interval.recognizedResultDict.keys():
			totalMatchList += [match for match in interval.recognizedResultDict[tonic][0]]
			exactMatchList += [match for match in interval.recognizedResultDict[tonic][1]]
			possibleMatchList += [match for match in interval.recognizedResultDict[tonic][2]]
		if totalMatch:
			orderedMatchesDict['1-totalMatch'] = totalMatchList
		if exactMatch:
			orderedMatchesDict['2-exactMatch'] = exactMatchList
		if possibleMatch:
			orderedMatchesDict['3-possibleMatch'] = possibleMatchList
		return orderedMatchesDict


	def __getTargetTypeListFromFirstPriorityFeature(self, feature):
		targetTypeList = []
		if feature == self.ProgressionFeatures.PriorOnBeat:

			targetTypeList.append(ChordInterval.IntervalType.OnBeat)

		elif feature == self.ProgressionFeatures.PriorAllIntervalType:

			targetTypeList.append(ChordInterval.IntervalType.OnBeat)
			targetTypeList.append(ChordInterval.IntervalType.AfterBeat)
			targetTypeList.append(ChordInterval.IntervalType.ChangedBaseline)

		elif feature == self.ProgressionFeatures.PriorChangedBaseline:
			targetTypeList.append(ChordInterval.IntervalType.ChangedBaseline)
		return targetTypeList


	def __findAllIntervalByIntervalTypeWithLimit(self, targetIntervalType, startMeasure, startInterval, barLimit=2):
		(allIntervalWithLimit, touchEnd) = self.__findAllIntervalWithLimit(startMeasure=startMeasure, startInterval=startInterval, barLimit=barLimit)
		intervalList = []
		for interval in allIntervalWithLimit:
			for intervalType in interval.intervalType:
				if intervalType in targetIntervalType:
					intervalList.append(interval)
					break
		return (intervalList, touchEnd)


	def __findAllIntervalWithLimit(self, startMeasure, startInterval, barLimit):

		touchEnd = False
		if startMeasure + barLimit >= len(self._inputList):
			limit = len(self._inputList)
			touchEnd = True
		else:
			limit = startMeasure + barLimit

		intervalList = []
		for measureIndex in range(startMeasure, limit):
			for interval in self._inputList[measureIndex]:
				if measureIndex == startMeasure and interval.intervalNo < startInterval:
					continue
				intervalList.append(interval)
		return (intervalList, touchEnd)