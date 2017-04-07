import re

class ChordInterval(object):

	#simulate enum
	class IntervalType(object):
		OnBeat, AfterBeat, Continuous, Normal = range(4)

	def __init__(self, noteList=[], intervalNo=None, offset=None, endTime=None):
		self._noteList = list(noteList)
		self._intervalType = self.IntervalType.Normal
		if len(self._noteList):
			self._exactOffset = offset
			self._exactEndTime = endTime
			self._measureNo = self._noteList[0].measure
			self._intervalNo = intervalNo
		else:
			self._exactOffset = None
			self._exactEndTime = None
			self._measureNo = None
			self._intervalNo = None
		self._recognizedResultDict = {}
		self._equivalentGroupDict = {}
		self._weightedTonicDict = {}
		self.__updateStartEndTime()

	# notes in this interval
	# [note1, note2, note3, ...]
	@property
	def noteList(self):
		return self._noteList

	@property
	def measureNo(self):
		return self._measureNo

	@property
	def intervalNo(self):
		return self._intervalNo

	@property
	def exactOffset(self):
		return self._exactOffset

	@property
	def exactEndTime(self):
		return self._exactEndTime

	@property
	def intervalType(self):
		return self._intervalType

	# Result Dictionary from chord recognizer
	# {tonic: ([totalmatch, ...], [exactmatch, ...], [possiblematch, ... )}
	#
	# totalmatch / exactmatch / possiblematch structure: tuple of (cname, chordType, inversion, roman, tonic, groupNo)         
	@property
	def recognizedResultDict(self):
		return self._recognizedResultDict

	# Equivalent Chord Group Dictionary
	# {groupNo: [(cname, chordType, inversion, roman, tonic, groupNo), ...]}
	# priority: TotalMatch -> ExactMatch -> PossibleMatch
	@property
	def equivalentGroupDict(self):
		return self._equivalentGroupDict

	# Weighted Interval Tonic
	# {tonic 1: ([exact weighted 1, exact weighted 2, (weightedType, cname), ...], [possible weighted 1, possible weighted 2, ... ]), tonic 2, tonic 3, ... }
	@property
	def weightedTonicDict(self):
		return self._weightedTonicDict

	# deprecated
	@property
	def startOffset(self):
		return self._startOffset

	# decprecated
	@property
	def endEndTime(self):
		return self._endEndTime

	def debug(self):
		print "Measure: ", self._measureNo, " Interval: ", self._intervalNo
		print "\tStart at ", self._exactOffset, "End at ", self._exactEndTime
		if self._intervalType == self.IntervalType.OnBeat:
			print "\tType: OnBeat"
		elif self._intervalType == self.IntervalType.AfterBeat:
			print "\tType: AfterBeat"
		elif self._intervalType == self.IntervalType.Continuous:
			print "\tType: Continuous"
		elif self._intervalType == self.IntervalType.Normal:
			print "\tType: Normal"
		print ""

		noteStrList = [chordNote.debugMessage() for chordNote in self._noteList]
		print "\tNote List: ", noteStrList
		print ""

		result = self._recognizedResultDict

		# first print exact match
		print "\tTotal match chords are: "
		for tonic in result.keys():
			if len(result[tonic][0]) > 0:
				cnameList = [tup[0] for tup in result[tonic][0]]
				print "\t", tonic, ": ", cnameList
		print ""
		# first print exact match
		print "\tExact match chords are: "
		for tonic in result.keys():
			if len(result[tonic][1]) > 0:
				cnameList = [tup[0] for tup in result[tonic][1]]
				print "\t", tonic, ": ", cnameList
		print ""

		# then print possible match
		print "\tPossible match chords are: "
		for tonic in result.keys():
			if len(result[tonic][2]) > 0:
				cnameList = [tup[0] for tup in result[tonic][2]]
				print "\t", tonic, ": ", cnameList
		print ""

		print "\tEquivalent Chord: "
		for groupNo in self._equivalentGroupDict.keys():
			strList = [str(tup[4]+' '+tup[0]) for tup in self._equivalentGroupDict[groupNo]]
			print "\t", groupNo, ": ", strList
		print ""

	def addNote(self, chordNote=None):
		if chordNote is not None:
			self._noteList.append(chordNote)
			self.__updateStartEndTime()

	def replaceNote(self, originalNote=None, newNote=None):
		if originalNote is not None and newNote is not None:
			try:
				replaceIndex = self._noteList.index(originalNote)
				self._noteList.remove(originalNote)
				self._noteList.insert(replaceIndex, newNote)
			except ValueError:
				self._noteList.append(newNote)

	def getChordRecognizerInputFormat(self):
		inputDict = {}
		for chordNote in self._noteList:
			inputDict[chordNote.name] = chordNote.frequency
		return inputDict

	def isWeighted(self):
		return len(self._weightedTonicDict.keys()) > 0

	def setExactEndTime(self, endTime=None):
		self._exactEndTime = endTime

	def setIntervalType(self, intervalType=None):
		self._intervalType = intervalType

	def setRecognizedResultDict(self, d={}):
		self._recognizedResultDict = d

	def setEquivalentGroupDict(self, d={}):
		self._equivalentGroupDict = d

	def setWeightedTonicDict(self, d={}):
		self._weightedTonicDict = d

	def analyzeEquivalentChord(self):
		resultDict = self._recognizedResultDict
		groupDict = {}
		groupCounter = 0
		for tonic in resultDict.keys():
			#total
			for i, item in enumerate(resultDict[tonic][0]):
				if groupCounter == 0:
					newTuple = (item[0], item[1], item[2], item[3], item[4], groupCounter)
					groupDict[groupCounter] = [tuple(newTuple)]
					self._recognizedResultDict[tonic][0][i] = tuple(newTuple)
					groupCounter += 1
				else:
					for groupNo in groupDict.keys():
						if self.__chkEquivalent(tonic, item[0], groupDict[groupNo][0][4], groupDict[groupNo][0][0]):
							newTuple = (item[0], item[1], item[2], item[3], item[4], groupNo)
							groupDict[groupNo].append(tuple(newTuple))
							self._recognizedResultDict[tonic][0][i] = tuple(newTuple)
							item = self._recognizedResultDict[tonic][0][i]
							break
					if item[5] is None:
						newTuple = (item[0], item[1], item[2], item[3], item[4], groupCounter)
						groupDict[groupCounter] = [tuple(newTuple)]
						self._recognizedResultDict[tonic][0][i] = tuple(newTuple)
						groupCounter += 1
			#exact
			for i, item in enumerate(resultDict[tonic][1]):
				if groupCounter == 0:
					newTuple = (item[0], item[1], item[2], item[3], item[4], groupCounter)
					groupDict[groupCounter] = [tuple(newTuple)]
					self._recognizedResultDict[tonic][1][i] = tuple(newTuple)
					groupCounter += 1
				else:
					for groupNo in groupDict.keys():
						if self.__chkEquivalent(tonic, item[0], groupDict[groupNo][0][4], groupDict[groupNo][0][0]):
							newTuple = (item[0], item[1], item[2], item[3], item[4], groupNo)
							groupDict[groupNo].append(tuple(newTuple))
							self._recognizedResultDict[tonic][1][i] = tuple(newTuple)
							item = self._recognizedResultDict[tonic][1][i]
							break
					if item[5] is None:
						newTuple = (item[0], item[1], item[2], item[3], item[4], groupCounter)
						groupDict[groupCounter] = [tuple(newTuple)]
						self._recognizedResultDict[tonic][1][i] = tuple(newTuple)
						groupCounter += 1
			#possible
			for i, item in enumerate(resultDict[tonic][2]):
				if groupCounter == 0:
					newTuple = (item[0], item[1], item[2], item[3], item[4], groupCounter)
					groupDict[groupCounter] = [tuple(newTuple)]
					self._recognizedResultDict[tonic][2][i] = tuple(newTuple)
					groupCounter += 1
				else:
					for groupNo in groupDict.keys():
						if self.__chkEquivalent(tonic, item[0], groupDict[groupNo][0][4], groupDict[groupNo][0][0]):
							newTuple = (item[0], item[1], item[2], item[3], item[4], groupNo)
							groupDict[groupNo].append(tuple(newTuple))
							self._recognizedResultDict[tonic][2][i] = tuple(newTuple)
							item = self._recognizedResultDict[tonic][2][i]
							break
					if item[5] is None:
						newTuple = (item[0], item[1], item[2], item[3], item[4], groupCounter)
						groupDict[groupCounter] = [tuple(newTuple)]
						self._recognizedResultDict[tonic][2][i] = tuple(newTuple)
						groupCounter += 1
		self._equivalentGroupDict = groupDict

	def __chkEquivalent(self, targetTonic, targetChord, compareTonic, compareChord):
		noteDict = {
			'C':1, 'C#':2, 'Db':2,
			'D':3, 'D#':4, 'Eb':4, 'E':5, 'F':6,
			'F#':7, 'Gb':7, 'G':8, 'G#':9, 'Ab':9,
			'A':10, 'A#':11, 'Bb':11, 'B':12, 'Cb':12
		}
		romanDict = {
			'I':1, 'i':1,
			'bII':2, 'ii':3,
			'bIII':4, 'iii':5,
			'IV':6, 'iv':6,
			'V':8, 'v':8,
			'bVI':9, 'VI':9, 'vi':10,
			'bVII':11, 'vii':12
		}
		targetCtype = None
		compareCtype = None
		targetRoman = None
		compareRoman = None

		if "half-dim " in targetChord or "full-dim " in targetChord or "German" in targetChord or "Italian" in targetChord or "French" in targetChord or "dim " in targetChord:
			splitResult = re.split("(half-dim |full-dim |German|Italian|French|dim )+", targetChord)
			Ctype = re.split(splitResult[2], targetChord)
			targetCtype = Ctype[0]
			targetChord = splitResult[2]

		if "7" in targetChord or "6" in targetChord or "4" in targetChord:
			splitResult = re.split("[0-9]+", targetChord)
			Ctype = re.split(splitResult[0], targetChord)
			if targetCtype == None:
				if "7" in Ctype or "65" in Ctype or "43" in Ctype or "42" in Ctype:
					targetCtype = "7th"
				else:
					targetCtype = "Triad"
			targetRoman = splitResult[0]
		else:
			targetRoman = targetChord
			if targetCtype == None:
				targetCtype = "Triad"

		if "7th" in targetCtype or "Triad" in targetCtype:
			if re.match("[A-Za-z]*[A-Z]+", targetRoman):
				if targetCtype == "7th":
					targetCtype = "Major 7th"
				else:
					targetCtype = "Major Triad"
			else:
				if targetCtype == "7th":
					targetCtype = "Minor 7th"
				else:
					targetCtype = "Minor Triad"

		if "half-dim " in compareChord or "full-dim " in compareChord or "German" in compareChord or "Italian" in compareChord or "French" in compareChord or "dim " in compareChord:
			splitResult = re.split("(half-dim |full-dim |German|Italian|French|dim )+", compareChord)
			Ctype = re.split(splitResult[2], compareChord)
			compareCtype = Ctype[0]
			compareChord = splitResult[2]

		if "7" in compareChord or "6" in compareChord or "4" in compareChord:
			splitResult = re.split("[0-9]+", compareChord)
			Ctype = re.split(splitResult[0], compareChord)
			if compareCtype == None:
				if "7" in Ctype or "65" in Ctype or "43" in Ctype or "42" in Ctype:
					compareCtype = "7th"
				else:
					compareCtype = "Triad"
			compareRoman = splitResult[0]
		else:
			compareRoman = compareChord
			if compareCtype == None:
				compareCtype = "Triad"

		if "7th" in compareCtype or "Triad" in compareCtype:
			if re.match("[A-Za-z]*[A-Z]+", compareRoman):
				if compareCtype == "7th":
					compareCtype = "Major 7th"
				else:
					compareCtype = "Major Triad"
			else:
				if compareCtype == "7th":
					compareCtype = "Minor 7th"
				else:
					compareCtype = "Minor Triad"

		if not targetCtype == compareCtype:
			return False
		targetSum = (noteDict[targetTonic] + romanDict[targetRoman])%12
		compareSum = (noteDict[compareTonic] + romanDict[compareRoman])%12
		if not targetSum == compareSum:
			return False
		return True


	# deprecated
	def __updateStartEndTime(self):
		self._startOffset = None
		self._endEndTime = None
		if len(self._noteList):
			self._startOffset = self._noteList[0].offset
			self._endEndTime = self._noteList[-1].endTime
			for chordNote in self._noteList:
				if chordNote.offset < self._startOffset:
					self._startOffset = chordNote.offset
				if chordNote.endTime > self._endEndTime:
					self._endEndTime = chordNote.endTime

