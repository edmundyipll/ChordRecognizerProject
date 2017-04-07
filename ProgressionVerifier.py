from ProgressionBank import ProgressionBank

class ProgressionVerifier(object):
	# maybe implement equivalent chord here


	def __init__(self, resultList=[], weightedResult=[], weightedDict=[]):
		self._resultList = list(resultList)
		self._weightedResult = weightedResult
		self._weightedDict = weightedDict
		self._pBank = ProgressionBank()
		while len(self._resultList[-1]) == 0:
			self._resultList.pop()
		self.__produceNextWeightedIntervalDict()

	def __transformStructure(self, bar=None, interval=None):
		# transform result structure to the following
		# {tonic 1, tonic 2, tonic: [exact 1, exact 2, "V", ..., last exact, poss 1, poss 2, "V", ..., last possible], tonic 4, ...}
		#                    ^                         ^                                     ^
		#                 tonic 3                 third exact cname                       third poss cname
		if bar is None or interval is None:
			return None
		newStructure = {}
		if len(self._resultList) <= bar or len(self._resultList[bar]) <= interval:
			return None
		tonicList = self._resultList[bar][interval].keys()
		for tonic in tonicList:
			newStructure[tonic] = []
			for cname in self._resultList[bar][interval][tonic][0]:
				#exact first
				newStructure[tonic].append(cname)
			for cname in self._resultList[bar][interval][tonic][1]:
				#possible after
				newStructure[tonic].append(cname)
		return newStructure

	def __produceNextWeightedIntervalDict(self):
		# produce a new dict structure like the following
		# {tonic 1, tonic 2, tonic: {bar 1, bar 2, bar: {interval1, interval2, interval: {'bar', 'interval', 'weightedInterval', 'target'}, interval 4, ... }, bar 4, ... }, tonic 4, ...}
		#                           ^                   ^                                ^         
		#                       tonic 3              bar 3                            interval 3                          
		nextWeightedIntervalDict = {}		
		for tonic in self._resultList[0][0].keys():
			nextWeightedIntervalDict[tonic] = {}
		for weightedInterval in self._weightedResult:
			tonicList = [tonic for tonic in weightedInterval.keys() if tonic is not 'bar' and tonic is not 'interval']
			for tonic in tonicList:
				if len(nextWeightedIntervalDict[tonic].keys()) > 0:
					lastBarIndex = sorted(nextWeightedIntervalDict[tonic].keys())[-1]
				else:
					lastBarIndex = 0
				for barIndex in range(lastBarIndex, weightedInterval['bar']+1):
					if barIndex not in nextWeightedIntervalDict[tonic]:
						nextWeightedIntervalDict[tonic][barIndex] = {}
					if len(nextWeightedIntervalDict[tonic][barIndex].keys()) > 0:
						lastIntervalIndex = sorted(nextWeightedIntervalDict[tonic][barIndex].keys())[-1]
					else:
						lastIntervalIndex = 0
					if barIndex == weightedInterval['bar']:
						intervalLimit = weightedInterval['interval'] + 1
					else:
						intervalLimit = len(self._resultList[barIndex])
					for intervalIndex in range(lastIntervalIndex, intervalLimit):
						(exact, poss) = weightedInterval[tonic]
						tmpList = []
						for chord in exact:
							tmpList.append(chord['cname'])
						for chord in poss:
							tmpList.append(chord['cname'])
						nextWeightedIntervalDict[tonic][barIndex][intervalIndex] = {'bar': weightedInterval['bar'], 'interval': weightedInterval['interval'], 'weightedInterval': True, 'target': tmpList}
		for tonic in self._resultList[0][0].keys():
			if len(nextWeightedIntervalDict[tonic].keys()) > 0:
				lastBarIndex = sorted(nextWeightedIntervalDict[tonic].keys())[-1]
			else:
				lastBarIndex = 0
			for barIndex in range(lastBarIndex, len(self._resultList)):
				if barIndex not in nextWeightedIntervalDict[tonic]:
					nextWeightedIntervalDict[tonic][barIndex] = {}
				if len(nextWeightedIntervalDict[tonic][barIndex].keys()) > 0:
					lastIntervalIndex = sorted(nextWeightedIntervalDict[tonic][barIndex].keys())[-1]
				else:
					lastIntervalIndex = 0
				for intervalIndex in range(lastIntervalIndex, len(self._resultList[barIndex])):
					lastBar = len(self._resultList)-1
					lastInterval = len(self._resultList[lastBar])-1
					nextWeightedIntervalDict[tonic][barIndex][intervalIndex] = {'bar': lastBar, 'interval': lastInterval, 'weightedInterval': False, 'target': self.__transformStructure(bar=lastBar, interval=lastInterval)[tonic]}

		self._nextWeightedIntervalDict = nextWeightedIntervalDict
		
		# for tonic in self._resultList[0][0].keys():
		# 	print "Tonic: ", tonic
		# 	for barIndex in nextWeightedIntervalDict[tonic].keys():
		# 		print "\tBar: ", barIndex
		# 		for intervalIndex in nextWeightedIntervalDict[tonic][barIndex].keys():
		# 			print "\t\tInterval: ", intervalIndex
		# 			print "\t\t", nextWeightedIntervalDict[tonic][barIndex][intervalIndex]



	def __nextWeightedInterval(self, bar=None, interval=None, tonic=None):
		# return the next weighted interval for the specific tonic
		if bar is None or interval is None or tonic is None:
			return None
		if tonic in self._nextWeightedIntervalDict and bar in self._nextWeightedIntervalDict[tonic] and interval in self._nextWeightedIntervalDict[tonic][bar]:
			return self._nextWeightedIntervalDict[tonic][bar][interval]
		else:
			return None

	def __verifyNext(self, resultDict=None, inputList=[], currentBar=None, currentInterval=None, previous=None, barLimit=1):
		if currentBar is None or currentInterval is None or inputList == [] or resultDict is None:
			return False
		if currentBar + barLimit < len(self._resultList):
			barRange = barLimit
		else:
			return True
		for inputIndex, (tonic, cname) in enumerate(inputList):
			searched = False
			barLoopList = list(reversed(range(barRange+1)))
			# print 'looping at inputList'
			for i in barLoopList:
				if i == 0:
					intervalMin = currentInterval+1
				else:
					intervalMin = 0
				if len(self._resultList[currentBar+i]) - intervalMin <= 0:
					continue
				# print 'looping at barLoop at bar', currentBar+i, ' currentBar is ', currentBar, ' i is ', i
				intervalLoopList = list(reversed(range(len(self._resultList[currentBar+i]) - intervalMin)))
				for j in intervalLoopList:
					interval = self.__transformStructure(bar=currentBar+i, interval=intervalMin+j)
					if interval is None:
						continue
					# print 'looping at intervalLoop at interval', intervalMin+j, ' intervalMin is ', intervalMin, ' j is ', j, ' intervalLoopList: ', intervalLoopList
					for targetCName in interval[tonic]:
						progressionResult = self._pBank.verify(before=cname, after=targetCName)
						# print 'looping at intervalTonic'
						if progressionResult == "Yes" or cname == targetCName:
							nextChord = {}
							nextChord['bar'] = currentBar+i
							nextChord['interval'] = j + intervalMin
							nextChord['previous'] = previous[inputIndex]
							nextChord['tonic'] = tonic
							nextChord['cname'] = targetCName
							if not currentBar+i in resultDict:
								resultDict[currentBar+i] = {}
							if not j + intervalMin in resultDict[currentBar+i]:
								resultDict[currentBar+i][j + intervalMin] = []
							resultDict[currentBar+i][j + intervalMin].append(nextChord)
							# print 'Now Going into next level, currentBar is ', currentBar+i, ' currentInterval is ', j+intervalMin, ' j is ', j
							searched = self.__verifyNext(resultDict=resultDict, inputList=[(tonic, targetCName)], currentBar = currentBar+i, currentInterval = j + intervalMin, previous=[nextChord])
							if searched is not True:
								resultDict[currentBar+i][j + intervalMin].remove(nextChord)
								if len(resultDict[currentBar+i][j + intervalMin]) == 0:
									resultDict[currentBar+i].pop(j + intervalMin)
								if len(resultDict[currentBar+i].keys()) == 0:
									resultDict.pop(currentBar+i)
							else:
								break
					if searched is True:
						break
				if searched is True:
					break
		return searched

	def __verifyWithLimit(self, resultDict=None, inputChord=None, currentBar=None, currentInterval=None, previous=None, limit=None):
		if currentBar is None or currentInterval is None or inputChord == None or resultDict is None or limit is None:
			return False
		(tonic, cname) = inputChord
		barLimit = limit['bar']
		intervalLimit = limit['interval']
		searched = False
		for i in range(currentBar, barLimit+1):
			if i == currentBar:
				intervalRange = range(currentInterval+1, len(self._resultList[i])+1)
			else:
				intervalRange = range(len(self._resultList[i]))
			for j in intervalRange:
				interval = self.__transformStructure(bar=i, interval=j)
				if interval is None:
					continue
				# print 'looping at intervalLoop at interval', intervalMin+j, ' intervalMin is ', intervalMin, ' j is ', j, ' intervalLoopList: ', intervalLoopList
				successAtLimit = False
				for targetCName in interval[tonic]:
					progressionResult = self._pBank.verify(before=cname, after=targetCName)
					# print 'looping at intervalTonic'
					if progressionResult == "Yes" or cname == targetCName:
						if i == barLimit and j == intervalLimit and limit['weightedInterval'] and targetCName not in limit['target']:
							# not i v I V
							continue
						nextChord = {}
						nextChord['bar'] = i
						nextChord['interval'] = j
						nextChord['previous'] = previous
						nextChord['tonic'] = tonic
						nextChord['cname'] = targetCName
						if not i in resultDict:
							resultDict[i] = {}
						if not j in resultDict[i]:
							resultDict[i][j] = []
						resultDict[i][j].append(nextChord)

						if i == barLimit and j == intervalLimit:
							successAtLimit = True
							continue

						# print 'Now Going into next level, currentBar is ', currentBar+i, ' currentInterval is ', j+intervalMin, ' j is ', j
						searched = self.__verifyWithLimit(resultDict=resultDict, inputChord=(tonic, targetCName), currentBar = i, currentInterval = j, previous=nextChord, limit=limit)
						
						if not searched:
							resultDict[i][j].remove(nextChord)
							if len(resultDict[i][j]) == 0:
								resultDict[i].pop(j)
							if len(resultDict[i].keys()) == 0:
								resultDict.pop(i)
				if successAtLimit:
					return True
			# 			else:
			# 				break
			# 	if searched:
			# 		break
			# if searched:
			# 	break
		return searched


	def verify(self):		
		inputList = []
		newStructure = self.__transformStructure(bar=0, interval=0)
		tonicList = newStructure.keys()
		resultDict={}
		resultDict[0]={}
		resultDict[0][0] = []
		for tonic in tonicList:
			for cname in newStructure[tonic]:
				inputList.append((tonic, cname))
				firstChord = {}
				firstChord['bar'] = 0
				firstChord['interval'] = 0
				firstChord['previous'] = None
				firstChord['tonic'] = tonic
				firstChord['cname'] = cname
				resultDict[0][0].append(firstChord)
		self.__verifyNext(resultDict = resultDict, inputList = inputList, currentBar = 0, currentInterval = 0, previous=resultDict[0][0])
		return resultDict
	
	def verify2(self, safeBarLimit=5, safeWeightedIntervalLimit=10):
		newStructure = self.__transformStructure(bar=0, interval=0)
		tonicList = newStructure.keys()
		resultProgressionList = []
		for tonic in tonicList:
			for cname in newStructure[tonic]:
				# for each different starting point
				sectorResult = []
				currentBar = 0
				currentInterval = 0
				previousCName = cname
				extendLimit = 0
				reachEnd = False
				while True:
					resultDict={}
					resultDict[currentBar]={}
					resultDict[currentBar][currentInterval] = []
					firstChord = {}
					firstChord['bar'] = currentBar
					firstChord['interval'] = currentInterval
					firstChord['previous'] = None
					firstChord['tonic'] = tonic
					firstChord['cname'] = previousCName
					resultDict[currentBar][currentInterval].append(firstChord)
					limit = self.__nextWeightedInterval(tonic=tonic, bar=currentBar, interval=currentInterval)
					for i in range(extendLimit):
						limit = self.__nextWeightedInterval(tonic=tonic, bar=limit['bar'], interval=limit['interval'])
					# print "limit: ", limit['bar'], limit['interval'], "current: ",currentBar, currentInterval
					# safe bar limit
					if limit['bar'] - currentBar >= safeBarLimit:
						sectorResult = []
						break
					if not limit['weightedInterval']:
						reachEnd = True
					self.__verifyWithLimit(resultDict=resultDict, inputChord=(tonic, previousCName), currentBar=currentBar, currentInterval=currentInterval, previous=firstChord, limit=limit)
					lastBar = sorted(resultDict.keys())[-1]
					lastInterval = sorted(resultDict[lastBar].keys())[-1]
					progressionList = []
					for chord in resultDict[lastBar][lastInterval]:
						progression = []
						progression.insert(0, chord)
						prevChord = chord['previous']
						while prevChord is not None:
							progression.insert(0, prevChord)
							prevChord = prevChord['previous']

						if len(progression) > 1:
							progressionList.append(progression)
					# for j, progression in enumerate(progressionList):
					# 	print "\tProgression ", j
					# 	for chord in progression:
					# 		displayChord = dict(chord)
					# 		displayChord.pop('previous')
					# 		print "\t\t", displayChord
					if len(progressionList) > 0:
						extendLimit = 0
						sectorResult.append(progressionList)
						currentBar = lastBar
						currentInterval = lastInterval
						# pick the longest progression 
						previousCName = max(progressionList, key=len)[-1]['cname']
					else:
						extendLimit = extendLimit + 1
					
					# safe weightedInterval limit
					if extendLimit > safeWeightedIntervalLimit:
						sectorResult = []
						break
					
					# if lastBar ==  self._weightedResult[-1]['bar'] and lastInterval == self._weightedResult[-1]['interval']:
					# 	break
					if reachEnd:
						break
				# for i, progressionList in enumerate(sectorResult):
				# 	print "Sector ",i
				# 	for j, progression in enumerate(progressionList):
				# 		print "\tProgression ", j
				# 		for chord in progression:
				# 			displayChord = dict(chord)
				# 			displayChord.pop('previous')
				# 			print "\t\t", displayChord
				print "Tonic: ", tonic, ", Starting point: ", cname
				finalizedProgression = []
				for i, progressionList in enumerate(sectorResult):				
					# pick the longest progression
					longest = max(progressionList, key=len)
					for j, chord in enumerate(longest):
						displayChord = dict(chord)
						displayChord.pop('previous')
						if i < len(sectorResult)-1 and j == len(longest)-1:
							continue
						finalizedProgression.append(displayChord)
						print "\t", displayChord
				resultProgressionList.append({"tonic":tonic, "start":cname, "progression":finalizedProgression})
		return resultProgressionList
