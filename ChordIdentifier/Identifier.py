from ChordAnalyzingTool import ChordAnalyzingTool
from ProgressionVerifier import ProgressionVerifier
from ChordNote import ChordNote
from ChordInterval import ChordInterval
import music21
import copy
import os

class Identifier(object):

	#_preparedScoreInput structure
	#[measure 1, measure 2, [ interval 1, interval 2, interval Object, interval 4, ... ], measure 4, ... ]
	#                       ^                         ^                
	#                   in measure 3            in interval 3  

	def __init__(self, score):
		self._score = score
		self._chordifiedScore = score.chordify()

		#initialize chord analyzing tool object
		self._analyzingTool = ChordAnalyzingTool()

		# traverse through whole score to extract notes and create interval objects
		scoreInput = self.__readScore(score=self._chordifiedScore)

		# run basic chord analyzing algorithm
		self.__basicAnalyze(inputs=scoreInput)

		# store prepared score
		self._preparedScoreInput = scoreInput

		# extract the key object list for priority control in progression
		self._keyList = [key for key in self._chordifiedScore.recurse().getElementsByClass(music21.key.Key)]

		# initialize progression verifier
		self._progressionVerifier = ProgressionVerifier(inputList=self._preparedScoreInput, keyList=self._keyList)


	def printPreparedScore(self):
		inputs = self._preparedScoreInput
		for measure in inputs:
			for interval in measure:
				interval.debug()
				print ""

	def runProgression(self, featureList=[], barLimit=2, verbal=False, output=None):
		result = self._progressionVerifier.verify(featureList=featureList, barLimit=barLimit)
		if verbal:
			cnameIndex = self._analyzingTool.convertMatchTupleKeyToIndex(key='cname')
			tonicIndex = self._analyzingTool.convertMatchTupleKeyToIndex(key='tonic')
			for (interval, matchTuple) in result:
				string = "At Measure "+str(interval.measureNo+1)+", offset "+str(interval.exactOffset)+", "
				string += str(matchTuple[tonicIndex])+str(matchTuple[cnameIndex])+", "+str(matchTuple)
				print string
		if output:
			self.__outputResultInMusicXml(result=result, outputFileName=output)
		return result

	def __outputResultInMusicXml(self, result, outputFileName):
		cnameIndex = self._analyzingTool.convertMatchTupleKeyToIndex(key='cname')
		tonicIndex = self._analyzingTool.convertMatchTupleKeyToIndex(key='tonic')
		copiedChordifiedScore = copy.deepcopy(self._chordifiedScore)
		for c in copiedChordifiedScore.recurse().getElementsByClass(music21.chord.Chord):
			c.closedPosition(forceOctave=5, inPlace=True)

		for (interval, matchTuple) in result:
			c = [offsetMap.element for offsetMap in copiedChordifiedScore.measure(interval.measureNo+1).offsetMap() if isinstance(offsetMap.element, music21.chord.Chord) and offsetMap.offset == interval.exactOffset]
			if len(c):
				c[0].addLyric(str(matchTuple[tonicIndex])+str(matchTuple[cnameIndex]))
		self._score.insert(0, copiedChordifiedScore)
		self._score.write('musicxml', fp=os.getcwd()+'/'+outputFileName)
		self._score.remove(copiedChordifiedScore)

	def __basicAnalyze(self, inputs):
		for i, measure in enumerate(inputs):
			for j, interval in enumerate(measure):
				tonicResult = self._analyzingTool.recognizeByAllTonic(interval)
				inputs[i][j].setRecognizedResultDict(tonicResult)
				inputs[i][j].analyzeEquivalentChord()

	def __readScore(self, score):
		inputs = []
		count = 1
		currentTimeSignature = None
		currentBaseLineFreq = None
		measure = score.measure(count)
		while measure is not None:
			if measure.timeSignature is not None:
				currentTimeSignature = measure.timeSignature
			if currentTimeSignature is None:
				# print "Error - No time signature detected."
				break
			#operation in each bar
			inputIntervalList = []
			continuousInterval = None
			intervalCounter = 0
			for offsetMap in measure.offsetMap():
				chordNoteList = []
				element = offsetMap.element
				if isinstance(element, music21.chord.Chord):
					for pitch in element.pitches:
						chordNoteList.append(ChordNote(name=pitch.name,frequency=pitch.frequency,offset=offsetMap.offset,endTime=offsetMap.endTime,measure=count-1))
				if len(chordNoteList) == 1:
					if continuousInterval is not None:
						noteNameList = [chordNote.name for chordNote in continuousInterval.noteList]
						if chordNoteList[0].name in noteNameList:
							for chordNote in continuousInterval.noteList:
								if chordNoteList[0].name == chordNote.name and chordNoteList[0].frequency < chordNote.frequency:
									continuousInterval.replaceNote(chordNote, chordNoteList[0])
									break
						else:
							continuousInterval.addNote(chordNoteList[0])
					else:
						continuousInterval = ChordInterval(intervalNo=intervalCounter, noteList=list(chordNoteList), offset=chordNoteList[0].offset)
						continuousInterval.setIntervalType(ChordInterval.IntervalType.Continuous)
						intervalCounter += 1
				elif len(chordNoteList):
					if continuousInterval is not None:
						inputIntervalList.append(continuousInterval)
						continuousInterval = None
						inputIntervalList[-1].setExactEndTime(inputIntervalList[-1].noteList[-1].endTime)
					noteNameList = [chordNote.name for chordNote in chordNoteList]
					tmpChordNoteDict = {}
					for chordNote in chordNoteList:
						if chordNote.name not in tmpChordNoteDict:
							tmpChordNoteDict[chordNote.name] = chordNote
						elif chordNote.frequency < tmpChordNoteDict[chordNote.name].frequency:
							tmpChordNoteDict[chordNote.name] = chordNote
					inputIntervalList.append(ChordInterval(intervalNo=intervalCounter, noteList=list(tmpChordNoteDict.values()), offset=chordNoteList[0].offset, endTime=chordNoteList[0].endTime))

					# check previous interval that whether it is OnBeat Interval
					if len(inputIntervalList) > 1 and inputIntervalList[-2].intervalType == ChordInterval.IntervalType.OnBeat:
						inputIntervalList[-1].setIntervalType(ChordInterval.IntervalType.AfterBeat)

					beatDuration = currentTimeSignature.beatDuration.quarterLength
					# check current interval that whether it is OnBeat
					if inputIntervalList[-1].exactOffset / beatDuration % 1 == 0:
						inputIntervalList[-1].setIntervalType(ChordInterval.IntervalType.OnBeat)
					# default will be Normal type

					# now check did baseline changed, only applicable to OnBeat / AfterBeat / Normal
					lowestFreq = inputIntervalList[-1].getLowestFrequency()
					if not (lowestFreq == currentBaseLineFreq):
						inputIntervalList[-1].setIntervalType(ChordInterval.IntervalType.ChangedBaseline)
						currentBaseLineFreq = lowestFreq

					intervalCounter += 1

			# continuousInterval can consist only the notes within the same measure, so handle the unhandled continuous notes here
			if continuousInterval is not None:
				inputIntervalList.append(continuousInterval)
				continuousInterval = None
				inputIntervalList[-1].setExactEndTime(inputIntervalList[-1].noteList[-1].endTime)
			inputs.append(inputIntervalList)

			count += 1
			measure = score.measure(count)
		return inputs

