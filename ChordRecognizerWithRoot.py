
class ChordRecognizer(object):

	@property
	def tonic(self):
		return self._tonic

	#dictionary storing notes with same pitch
	calculatedDict = {
		1: ['C', 'B#', 'Dbb'],
		2: ['C#', 'Db', 'B##'],
		3: ['D', 'Ebb', 'C##'],
		4: ['D#', 'Eb', 'Fbb'],
		5: ['E', 'Fb', 'D##'],
		6: ['F', 'E#', 'Gbb'],
		7: ['F#', 'Gb', 'E##'],
		8: ['G', 'Abb', 'F##'],
		9: ['G#', 'Ab', 'Ab'],
		10: ['A', 'Bbb', 'G##'],
		11: ['A#', 'Bb', 'Cbb'],
		12: ['B', 'Cb', 'A##'],
	}

	#storing common chord names
	cname = [
		'I', 'I7', 'i',
		'bII', 'ii', 'ii7', 'dim ii', 'half-dim ii7',
		'iii', 'iii7', 'bIII',
		'IV', 'IV7', 'iv',
		'V', 'V7', 'v',
		'bVI', 'GermanVI', 'FrenchVI', 'ItalianVI', 'vi', 'vi7',
		'dim vii', 'half-dim vii7', 'full-dim vii7', 'bVII'
	]

	duplicatedChord = [0, 4, 6, 8, 11, 14, 20, 23]
	generalDuplicatedChord = [0, 4, 6, 8, 11, 14]
	normal7thChord = [1, 5, 7, 9, 12, 15]

	# calculating useful intervals
	# m stands for minor, M for major, P for perfect, A for augmented
	# ie. m3 stands for minor 3rd and A4 stands for augmented 4th
	def __interval_cal(self):

		notes = self._notes
		mapDict = self._mapDict
		tonic = self._tonic

		notes.clear()
		notes['P1'] = tonic
		notes['m2'] = self.__decideNote(tonic, 2, (mapDict[tonic] + 1) % 12)
		notes['M2'] = self.__decideNote(tonic, 2, (mapDict[tonic] + 2) % 12)
		notes['m3'] = self.__decideNote(tonic, 3, (mapDict[tonic] + 3) % 12)
		notes['M3'] = self.__decideNote(tonic, 3, (mapDict[tonic] + 4) % 12)
		notes['P4'] = self.__decideNote(tonic, 4, (mapDict[tonic] + 5) % 12)
		notes['A4'] = self.__decideNote(tonic, 4, (mapDict[tonic] + 6) % 12)
		notes['P5'] = self.__decideNote(tonic, 5, (mapDict[tonic] + 7) % 12)
		notes['m6'] = self.__decideNote(tonic, 6, (mapDict[tonic] + 8) % 12)
		notes['M6'] = self.__decideNote(tonic, 6, (mapDict[tonic] + 9) % 12)
		notes['m7'] = self.__decideNote(tonic, 7, (mapDict[tonic] + 10) % 12)
		notes['M7'] = self.__decideNote(tonic, 7, (mapDict[tonic] + 11) % 12)

	# chosing suitable note from all notes having same pitch
	def __decideNote(self, firstNote, targetNote, num):
		if(num == 0):
			num = 12
		choice = ChordRecognizer.calculatedDict[num]
		for x in choice:
			diff = ord(x[0]) - ord(firstNote[0])
			if(diff < 0):
				diff += 7
			if (diff == targetNote - 1):
				return x
		return "Error"

	#calculating common chords' notes name
	def __chord_cal(self):

		chord = self._chord
		notes = self._notes
		cname = ChordRecognizer.cname

		chord.clear()
		chord[cname[0]] = (notes['P1'], notes['M3'], notes['P5'])
		chord[cname[1]] = (notes['P1'], notes['M3'], notes['P5'], notes['M7'])
		chord[cname[2]] = (notes['P1'], notes['m3'], notes['P5'])

		chord[cname[3]] = (notes['m2'], notes['P4'], notes['m6'])
		chord[cname[4]] = (notes['M2'], notes['P4'], notes['M6'])
		chord[cname[5]] = (notes['M2'], notes['P4'], notes['M6'], notes['P1'])
		chord[cname[6]] = (notes['M2'], notes['P4'], notes['m6'])
		chord[cname[7]] = (notes['M2'], notes['P4'], notes['m6'], notes['P1'])

		chord[cname[8]] = (notes['M3'], notes['P5'], notes['M7'])
		chord[cname[9]] = (notes['M3'], notes['P5'], notes['M7'], notes['M2'])
		chord[cname[10]] = (notes['m3'], notes['P5'], notes['m7'])

		chord[cname[11]] = (notes['P4'], notes['M6'], notes['P1'])
		chord[cname[12]] = (notes['P4'], notes['M6'], notes['P1'], notes['M3'])
		chord[cname[13]] = (notes['P4'], notes['m6'], notes['P1'])

		chord[cname[14]] = (notes['P5'], notes['M7'], notes['M2'])
		chord[cname[15]] = (notes['P5'], notes['M7'], notes['M2'], notes['P4'])
		chord[cname[16]] = (notes['P5'], notes['m7'], notes['M2'])

		chord[cname[17]] = (notes['m6'], notes['P1'], notes['m3'])
		chord[cname[18]] = (notes['m6'], notes['P1'], notes['m3'], notes['A4'])
		chord[cname[19]] = (notes['m6'], notes['P1'], notes['M2'], notes['A4'])
		chord[cname[20]] = (notes['m6'], notes['P1'], notes['A4'])
		chord[cname[21]] = (notes['M6'], notes['P1'], notes['M3'])
		chord[cname[22]] = (notes['M6'], notes['P1'], notes['M3'], notes['P5'])

		chord[cname[23]] = (notes['M7'], notes['M2'], notes['P4'])
		chord[cname[24]] = (notes['M7'], notes['M2'], notes['P4'], notes['M6'])
		chord[cname[25]] = (notes['M7'], notes['M2'], notes['P4'], notes['m6'])
		chord[cname[26]] = (notes['m7'], notes['M2'], notes['P4'])

	def __chord_note(self):

		notemap = self._notemap
		notes = self._notes

		notemap.clear()
		notemap[notes['P1']] = [0, 1, 2, 5, 7, 11, 12, 13, 17, 18, 19, 20, 21, 22]
		notemap[notes['m2']] = [3]
		notemap[notes['M2']] = [4, 5, 6, 7, 9, 14, 15, 16, 19, 23, 24, 25, 26]
		notemap[notes['m3']] = [2, 10, 17, 18]
		notemap[notes['M3']] = [0, 1, 8, 9, 12, 21, 22]
		notemap[notes['P4']] = [3, 4, 5, 6, 7, 11, 12, 13, 15, 23, 24, 25, 26]
		notemap[notes['A4']] = [18, 19, 20]
		notemap[notes['P5']] = [0, 1, 2, 8, 9, 10, 14, 15, 16, 22]
		notemap[notes['m6']] = [3, 6, 7, 13, 17, 18, 19, 20, 25]
		notemap[notes['M6']] = [4, 5, 11, 12, 21, 22, 24]
		notemap[notes['m7']] = [10, 16, 26]
		notemap[notes['M7']] = [1, 8, 9, 14, 15, 23, 24, 25]

	def __checkInversion(self, chordNo, inputs):
		cname = ChordRecognizer.cname
		chord = self._chord
		if chordNo in range(18, 21):
			return cname[chordNo]
		targetChord = chord[cname[chordNo]]
		is3 = len(targetChord) == 3
		inputSubset = {}
		for i in range(len(inputs.keys())):
			if inputs.keys()[i] in targetChord:
				inputSubset[inputs.keys()[i]] = inputs.values()[i]
		if len(inputSubset.keys()) < 2:
			return 'error'
		baseNote = inputSubset.keys()[inputSubset.values().index(min(inputSubset.values()))]
		if targetChord.index(baseNote) == 0:
			return cname[chordNo]
		elif targetChord.index(baseNote) == 1:
			if is3:
				return cname[chordNo] + '6'
			else:
				return cname[chordNo][:-1] + '65'
		elif targetChord.index(baseNote) == 2:
			if is3:
				return cname[chordNo] + '64'
			else:
				return cname[chordNo][:-1] + '43'
		elif targetChord.index(baseNote) == 3:
			#len(chord) must be four
			return cname[chordNo][:-1] + '42'


	def __init__(self, tonic, verbose = False):

		self._chord = {}
		self._mapDict = {}
		self._notes = {}
		self._notemap = {}
		self._tonic = tonic


		#generate dict for mapping ##########
		#i.e. mapDict['C'] = 1
		#     mapDict['B#'] = 1
		mapDict = self._mapDict
		dictList = ChordRecognizer.calculatedDict.items()
		for pair in dictList:
			(key, value) = pair
			mapDict[value[0]] = key
			mapDict[value[1]] = key
			if(not value[2] in mapDict):
				mapDict[value[2]] = key

		self.__interval_cal()
		self.__chord_cal()
		self.__chord_note()

		cname = ChordRecognizer.cname
		chord = self._chord
		if(verbose is True):
			print tonic, ' Major:'
			print cname[0], ':', chord[cname[0]]
			print cname[1], ':', chord[cname[1]]
			print cname[3], ':', chord[cname[3]]
			print cname[4], ':', chord[cname[4]]
			print cname[5], ':', chord[cname[5]]
			print cname[8], ':', chord[cname[8]]
			print cname[9], ':', chord[cname[9]]
			print cname[11], ':', chord[cname[11]]
			print cname[12], ':', chord[cname[12]]
			print cname[14], ':', chord[cname[14]]
			print cname[15], ':', chord[cname[15]]
			print cname[17], ':', chord[cname[17]]
			print cname[18], ':', chord[cname[18]]
			print cname[19], ':', chord[cname[19]]
			print cname[20], ':', chord[cname[20]]
			print cname[21], ':', chord[cname[21]]
			print cname[22], ':', chord[cname[22]]
			print cname[23], ':', chord[cname[23]]
			print cname[24], ':', chord[cname[24]]
			print cname[25], ':', chord[cname[25]]
			print tonic, ' Minor:'
			print cname[0], ':', chord[cname[0]]
			print cname[2], ':', chord[cname[2]]
			print cname[3], ':', chord[cname[3]]
			print cname[6], ':', chord[cname[6]]
			print cname[7], ':', chord[cname[7]]
			print cname[10], ':', chord[cname[10]]
			print cname[11], ':', chord[cname[11]]
			print cname[13], ':', chord[cname[13]]
			print cname[14], ':', chord[cname[14]]
			print cname[15], ':', chord[cname[15]]
			print cname[16], ':', chord[cname[16]]
			print cname[17], ':', chord[cname[17]]
			print cname[18], ':', chord[cname[18]]
			print cname[19], ':', chord[cname[19]]
			print cname[20], ':', chord[cname[20]]
			print cname[23], ':', chord[cname[23]]
			print cname[25], ':', chord[cname[25]]
			print cname[26], ':', chord[cname[26]]


	# input structure
	# {cname: frequency, cname: frequency, ... }
	def recognize(self, inputDict):

		#init
		notemap = self._notemap
		chord = self._chord
		mapDict = self._mapDict
		notes = self._notes
		tonic = self._tonic
		cname = ChordRecognizer.cname
		duplicatedChord = ChordRecognizer.duplicatedChord
		generalDuplicatedChord = ChordRecognizer.generalDuplicatedChord
		normal7thChord = ChordRecognizer.normal7thChord
		exactMatch = []
		possibleMatch = []
		chordCount = [0] * 27
		occur = [0] * 27
		chordroot = [0] * 27
		cnote = inputDict.keys()
		if len(cnote) == 1:
			if tonic == cnote[0]:
				return ([cname[0]], [])
			else:
				return ([], [])
		for x in cnote:
			if x == notes['P1']:
				for i in range(0, 3):
					chordroot[i] = 1
			elif x == notes['m2']:
				chordroot[3] = 1
			elif x == notes['M2']:
				for i in range(4, 8):
					chordroot[i] = 1
			elif x == notes['M3']:
				for i in range(8, 10):
					chordroot[i] = 1
			elif x == notes['m3']:
				chordroot[10] = 1
			elif x == notes['P4']:
				for i in range(11, 14):
					chordroot[i] = 1
			elif x == notes['P5']:
				for i in range(14, 17):
					chordroot[i] = 1
			elif x == notes['m6']:
				for i in range(17, 21):
					chordroot[i] = 1
			elif x == notes['M6']:
				for i in range(21, 23):
					chordroot[i] = 1
			elif x == notes['M7']:
				for i in range(23, 26):
					chordroot[i] = 1
			elif x == notes['m7']:
				chordroot[26] = 1
			try:
			 	for y in notemap[x]:
			 		chordCount[y] += 1
			except KeyError:
				pass
		#Exact match chords
		for x in range(27):
			if len(chord[cname[x]]) == 4 and chordCount[x] == 4:
				occur[x] = 1
		for x in range(27):
			if not len(chord[cname[x]]) == 4 and chordCount[x] == 3:
				if x not in duplicatedChord:
					occur[x] = 1
				elif x in generalDuplicatedChord and occur[x+1] == 0:
					occur[x] = 1
				elif x == 20 and occur[18] == 0 and occur[19] == 0:
					occur[x] = 1
				elif x == 23 and occur[24] == 0 and occur[25] == 0:
					occur[x] = 1
		for x in range(27):
			if occur[x] == 1 and chordroot[x] == 1:
				exactMatch.append(self.__checkInversion(x, inputDict))
				occur[x] = occur[x] + 1
		#Possible match chords
		for x in range(27):
			if len(chord[cname[x]]) == 4 and chordCount[x] == 3 and occur[x] == 0:
				if x in normal7thChord and occur[x-1] == 0:
					occur[x] = 1
				elif (x == 18 or x == 19) and occur[20] == 0:
					occur[x] = 1
				elif (x == 24 or x == 25) and occur[23] == 0:
					occur[x] = 1
		for x in range(27):
			if not len(chord[cname[x]]) == 4 and chordCount[x] == 2 and occur[x] == 0:
				if x not in duplicatedChord:
					occur[x] = 1
				elif x in generalDuplicatedChord and occur[x+1] == 0:
					occur[x] = 1
				elif x == 20 and occur[18] == 0 and occur[19] == 0:
					occur[x] = 1
				elif x == 23 and occur[24] == 0 and occur[25] == 0:
					occur[x] = 1
		for x in range(27):
			if occur[x] == 1 and chordroot[x] == 1:
				possibleMatch.append(self.__checkInversion(x, inputDict))
				occur[x] = occur[x] + 1
		return (exactMatch, possibleMatch)

	@classmethod
	def getAllRecognizers(self):
		recognizers = []
		possibleTonic = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C#', 'Cb', 'D#', 'Db', 'Eb', 'F#', 'G#', 'Gb', 'A#', 'Ab', 'Bb']
		for x in possibleTonic:
			recognizers.append(ChordRecognizer(x, False))
		return recognizers

	@classmethod
	def getRecognizersByTonic(self, tonicArr):
		recognizers = []
		for x in tonicArr:
			recognizers.append(ChordRecognizer(x, False))
		return recognizers