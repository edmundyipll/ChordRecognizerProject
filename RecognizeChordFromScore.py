import os
from ChordAnalyzingTool import ChordAnalyzingTool
from ProgressionVerifier import ProgressionVerifier
from ChordNote import ChordNote
from ChordInterval import ChordInterval
import music21
import sys
import copy

curPath = os.getcwd() + '/'
try:
	inputFileName = sys.argv[1]
except IndexError:
	print "Fail to read input file name" 
	sys.exit(1)
#read input

print "Reading input musicxml file"
try:
	rawScore = music21.converter.parse(curPath+inputFileName)  #for relative path
except music21.converter.ConverterException:
	try:
		rawScore = music21.converter.parse(inputFileName)  #for absolute path
	except music21.converter.ConverterException:
		print "Fail to read input file"
		sys.exit(1)

#initialize chord analyzing tool object
analyzeTool = ChordAnalyzingTool()

# chordify
score = rawScore.chordify()

inputs = []
count = 1
currentTimeSignature = None
currentBaseLineFreq = None
measure = score.measure(count)
while measure is not None:
	if measure.timeSignature is not None:
		currentTimeSignature = measure.timeSignature
	if currentTimeSignature is None:
		print "Error - No time signature detected."
		sys.exit()
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
	if continuousInterval is not None:
		inputIntervalList.append(continuousInterval)
		continuousInterval = None
		inputIntervalList[-1].setExactEndTime(inputIntervalList[-1].noteList[-1].endTime)
	inputs.append(inputIntervalList)

	count += 1
	measure = score.measure(count)


# #inputs structure
# #[measure 1, measure 2, [ interval 1, interval 2, interval Object, interval 4, ... ], measure 4, ... ]
# #                       ^                         ^                
# #                   in measure 3            in interval 3        

for i, measure in enumerate(inputs):
	resultArr = []
	for j, interval in enumerate(measure):
		tonicResult = analyzeTool.recognizeByAllTonic(interval)
		inputs[i][j].setRecognizedResultDict(tonicResult)
		inputs[i][j].analyzeEquivalentChord()

for measure in inputs:
	for interval in measure:
		interval.debug()
		print ""


# #Progression Verifying
progressionVerifier = ProgressionVerifier(inputList=inputs)
result = progressionVerifier.verify(featureList=[ProgressionVerifier.ProgressionFeatures.PriorAllIntervalType])
for (interval, matchTuple) in result:
	print matchTuple

# output as xml file
for c in score.recurse().getElementsByClass(music21.chord.Chord):
	c.closedPosition(forceOctave=5, inPlace=True)

for (interval, matchTuple) in result:
	c = [offsetMap.element for offsetMap in score.measure(interval.measureNo+1).offsetMap() if isinstance(offsetMap.element, music21.chord.Chord) and offsetMap.offset == interval.exactOffset]
	if len(c):
		c[0].addLyric(str(matchTuple[4])+str(matchTuple[0]))
rawScore.insert(0, score)
rawScore.write('musicxml', fp=curPath+'output.xml')
sys.exit(0)