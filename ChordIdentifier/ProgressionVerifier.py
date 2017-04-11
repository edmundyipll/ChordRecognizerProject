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

	def __init__(self, inputList=[], keyList=[]):
		self._inputList = copy.deepcopy(inputList)
		self._keyList = keyList
		self._pBank = ProgressionBank()
		self._analyzingTool = ChordAnalyzingTool()
		while len(self._inputList[-1]) == 0:
			self._inputList.pop()


	def verify(self, featureList=[], barLimit=2):

		# handle featureList
		firstPriorityCnt = len([f for f in self.ProgressionFeatures.getFirstPriorityList() if f in featureList])
		if firstPriorityCnt != 1:
			# take PriorAllIntervalType as FIRST priority when no or multiple FIRST priority setting found,
			featureList = [self.ProgressionFeatures.PriorAllIntervalType] + [f for f in featureList if f not in self.ProgressionFeatures.getFirstPriorityList()]
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
			(startingPointIntervalList, touchEnd) = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=measureCnt, startInterval=0, barLimit=barLimit)
			measureCnt += barLimit
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
			# print "Starting Point Priority List: "
			# for matchTuple in matchTuplePriorityList:
			# 	print matchTuple
			# print ""
			# start progression
			for matchTuple in matchTuplePriorityList:
				if startingPoint in self._invalidResult and matchTuple in self._invalidResult[startingPoint]:
					continue
				recursiveResult = self.__recursiveProgression(startingInterval=startingPoint, startingMatch=matchTuple, featureList=featureList, barLimit=barLimit)
				if len(recursiveResult) == 0:
					if startingPoint not in self._invalidResult:
						self._invalidResult[startingPoint] = []
					self._invalidResult[startingPoint].append(matchTuple)
				else:
					resultList = recursiveResult
					break
		return resultList


	def __recursiveProgression(self, startingInterval, startingMatch, featureList, barLimit):

		intervalA = startingInterval
		matchTupleA = startingMatch
		# print "StartingMatch: ", matchTupleA

		targetTypeList = self.__getTargetTypeListFromFirstPriorityFeature(feature=featureList[0])
		matchTupleRomanIndex = self._analyzingTool.convertMatchTupleKeyToIndex('roman')
		matchTupleTonicIndex = self._analyzingTool.convertMatchTupleKeyToIndex('tonic')
		matchTupleCNameIndex = self._analyzingTool.convertMatchTupleKeyToIndex('cname')

		# check if current interval is the last PriorInterval, if no, progressionBarLimit=2, if yes, progressionBarLimit=3
		(targetIntervalWithinThisBar, touchEnd) = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=intervalA.measureNo, startInterval=intervalA.intervalNo+1, barLimit=1)
		if touchEnd and len(targetIntervalWithinThisBar) == 0:
			return [(intervalA, matchTupleA)]
		if len(targetIntervalWithinThisBar) == 0:
			progressionBarLimitA = barLimit+1
		else:
			progressionBarLimitA = barLimit

		(targetIntervalWithinBarLimitA, touchEndA) = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=intervalA.measureNo, startInterval=intervalA.intervalNo+1, barLimit=progressionBarLimitA)
		for i, intervalB in enumerate(targetIntervalWithinBarLimitA):
			# print "\tIntervalB: ", intervalB.measureNo, intervalB.intervalNo

			totalExactMatches = self.__getOrderedMatchesDict(interval=intervalB, totalMatch=True, exactMatch=True, possibleMatch=False)
			intervalBRomanVList = []
			for key in sorted(totalExactMatches.keys()):
				intervalBRomanVList += [matchTuple for matchTuple in totalExactMatches[key] if matchTuple[matchTupleRomanIndex] == 'V']

			# check if current interval is the last PriorInterval, if no, progressionBarLimit=2, if yes, progressionBarLimit=2
			if i+1 < len(targetIntervalWithinBarLimitA) and targetIntervalWithinBarLimitA[i+1].measureNo == intervalB.measureNo:
				progressionBarLimitB = barLimit
			else:
				progressionBarLimitB = barLimit+1

			(targetIntervalWithinBarLimitB, touchEndB) = self.__findAllIntervalByIntervalTypeWithLimit(targetIntervalType=targetTypeList, startMeasure=intervalB.measureNo, startInterval=intervalB.intervalNo+1, barLimit=progressionBarLimitB)
			for matchTupleB in intervalBRomanVList:
				(cnameB, chordTypeB, inverionB, romanB, tonicB, groupNoB) = matchTupleB
				for j, intervalC in enumerate(targetIntervalWithinBarLimitB):
					# print "\t\tIntervalC: ", intervalC.measureNo, intervalC.intervalNo

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
								beforeCName = matchTupleA[matchTupleCNameIndex]
								afterCName = eqvIntervalCinTonicA[0][matchTupleCNameIndex]
								if matchTupleA[matchTupleTonicIndex][-1] == 'm':
									verifyFunction = self._pBank.verifyMinor
								else:
									verifyFunction = self._pBank.verifyMajor
								if verifyFunction(before=beforeCName, after=afterCName) == "Yes" or beforeCName == afterCName:

									if not(intervalC in self._invalidResult and eqvIntervalCinTonicA[0] in self._invalidResult[intervalC]):
										# print "Going to next Level"

										# next progression with no tonic changed
										recursiveResult = self.__recursiveProgression(startingInterval=intervalC, startingMatch=eqvIntervalCinTonicA[0], featureList=featureList, barLimit=barLimit)

										if len(recursiveResult) == 0:
											if intervalC not in self._invalidResult:
												self._invalidResult[intervalC] = []
											self._invalidResult[intervalC].append(eqvIntervalCinTonicA[0])
										else:
											return [(intervalA, matchTupleA), (intervalB, matchTupleB)] + recursiveResult

							# examine intervalA to intervalB
							eqvIntervalBinTonicA = [matchTuple for matchTuple in intervalB.equivalentGroupDict[groupNoB] if matchTuple[matchTupleTonicIndex] == matchTupleA[matchTupleTonicIndex]]
							if len(eqvIntervalBinTonicA):
								beforeCName = matchTupleA[matchTupleCNameIndex]
								afterCName = eqvIntervalBinTonicA[0][matchTupleCNameIndex]
								if matchTupleA[matchTupleTonicIndex][-1] == 'm':
									verifyFunction = self._pBank.verifyMinor
								else:
									verifyFunction = self._pBank.verifyMajor
								if verifyFunction(before=beforeCName, after=afterCName) == "Yes" or beforeCName == afterCName:

									if not(intervalC in self._invalidResult and matchTupleC in self._invalidResult[intervalC]):
										# print "Going to next Level"

										# next progression with tonic changed
										recursiveResult = self.__recursiveProgression(startingInterval=intervalC, startingMatch=matchTupleC, featureList=featureList, barLimit=barLimit)

										if len(recursiveResult) == 0:
											if intervalC not in self._invalidResult:
												self._invalidResult[intervalC] = []
											self._invalidResult[intervalC].append(matchTupleC)
										else:
											return [(intervalA, matchTupleA), (intervalB, matchTupleB)] + recursiveResult

		# no result above, now first come first serve, with OnBeat interval
		(cnameA, chordTypeA, inverionA, romanA, tonicA, groupNoA) = matchTupleA
		(targetIntervalWithinBarLimitA, touchEnd) = self.__findAllIntervalByIntervalTypeWithLimit(targetTypeList, startMeasure=intervalA.measureNo, startInterval=intervalA.intervalNo+1, barLimit=barLimit)
		for i, intervalB in enumerate(targetIntervalWithinBarLimitA):
			allMatches = self.__getOrderedMatchesDict(interval=intervalB, totalMatch=True, exactMatch=True, possibleMatch=True)
			sameTonicList = []
			for key in sorted(allMatches.keys()):
				sameTonicList += [matchTuple for matchTuple in allMatches[key] if matchTuple[matchTupleTonicIndex] == tonicA ]
			for matchTupleB in sameTonicList:
				beforeCName = cnameA
				afterCName = matchTupleB[matchTupleCNameIndex]
				if tonicA[-1] == 'm':
					verifyFunction = self._pBank.verifyMinor
				else:
					verifyFunction = self._pBank.verifyMajor
				if verifyFunction(before=beforeCName, after=afterCName) == "Yes" or beforeCName == afterCName:

					if intervalB in self._invalidResult and matchTupleB in self._invalidResult[intervalB]:
						continue

					# print "Going to next Level by first come first serve"

					# next progression 
					recursiveResult = self.__recursiveProgression(startingInterval=intervalB, startingMatch=matchTupleB, featureList=featureList, barLimit=barLimit)

					if len(recursiveResult) == 0:
						if intervalB not in self._invalidResult:
							self._invalidResult[intervalB] = []
						self._invalidResult[intervalB].append(matchTupleB)
					else:
						return [(intervalA, matchTupleA)] + recursiveResult
		return []



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


	def __findAllIntervalByIntervalTypeWithLimit(self, targetIntervalType, startMeasure, startInterval, barLimit):
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