import os
from ChordRecognizer import ChordRecognizer
from ProgressionVerifier import ProgressionVerifier
import music21
import sys

curPath = os.getcwd() + '/'
try:
	inputFileName = sys.argv[1]
except IndexError:
	print "Fail to read input file name"
	sys.exit(1)
#read input

print "Reading input musicxml file"
try:
	score = music21.converter.parse(curPath+inputFileName)  #for relative path
except music21.converter.ConverterException:
	try:
		score = music21.converter.parse(inputFileName)  #for absolute path
	except music21.converter.ConverterException:
		print "Fail to read input file"
		sys.exit(1)

#initialize 15 chord recognizers with different tonic
recognizers = ChordRecognizer.getAllRecognizers()
#recognizers = ChordRecognizer.getRecognizersByTonic(['D']);


inputs = []
count = 1
measureLength = -1
measureLengthCounter = 0
prevTs = None
prevBase = None
while measureLengthCounter < score.highestTime:
	subScore = score.measure(count)
	count += 1
	tmpMeasure = subScore.parts[0].getElementsByClass(music21.stream.Measure)[0]
	if tmpMeasure.timeSignature is not None:
		prevTs = tmpMeasure.timeSignature
	if prevTs is None:
		print "Error - No time signature detected."
		sys.exit()
	measureLengthCounter += prevTs.beatCount * prevTs.beatDuration.quarterLength
	
	#operation in each bar
	notes = []
	for part in subScore.parts:
		measure = part.getElementsByClass(music21.stream.Measure)[0]
		for elem in measure.offsetMap():
			element = elem.element
			if isinstance(element, music21.note.GeneralNote) and not isinstance(element, music21.note.Rest) and not element.duration.isGrace:
				for pitch in element.pitches:
					notes.append((pitch.name, pitch.frequency, elem.offset, elem.endTime))

	# start = prevTs.beatDuration.quarterLength
	# end = start + prevTs.beatDuration.quarterLength

	interval = {}
	for (note, frequency, offset, endTime) in notes:

		if offset not in interval.keys():
			interval[offset] = {}
			interval[offset]["start"] = []
			interval[offset]["end"] = []
		if endTime not in interval.keys():
			interval[endTime] = {}
			interval[endTime]["start"] = []
			interval[endTime]["end"] = []

		interval[offset]["start"].append((note, frequency, offset, endTime))
		interval[endTime]["end"].append((note, frequency, offset, endTime))

	inputDictArr = []
	running = {}
	firstEntryArr = []
	for key in sorted(interval.keys()):
		ending = interval[key]["end"]
		starting = interval[key]["start"]
		for tup in ending:
			if str(tup) in running.keys():
				running.pop(str(tup))
		for tup in starting:
			running[str(tup)] = tup

		if running:
			runningNotes = list(running.values());
			if len(runningNotes) == 1:
				if prevBase is None:
					# first entry
					firstEntryArr.append(tuple(runningNotes[0]))
					continue
				else:
					# single note, take prevBase together
					runningNotes.append(tuple(prevBase))
			else:
				if prevBase is None and len(firstEntryArr):
					# first "chord" after "first entry"
					firstEntryInputDict = {}
					for (note, frequency, offset, endTime) in firstEntryArr:
						note = note.replace("-", "b")
						if note not in firstEntryInputDict.keys():
							firstEntryInputDict[note] = frequency
						else:
							if frequency < firstEntryInputDict[note]:
								firstEntryInputDict[note] = frequency
					inputDictArr.append(firstEntryInputDict)
					firstEntryArr = []
			inputDict = {}
			tmpBase = None
			for (note, frequency, offset, endTime) in runningNotes:
				note = note.replace("-", "b")
				if note not in inputDict.keys():
					inputDict[note] = frequency
				else:
					if frequency < inputDict[note]:
						inputDict[note] = frequency
				if tmpBase :
					if frequency < tmpBase[1] :
						tmpBase = (note, frequency, offset, endTime)
				else:
					tmpBase = (note, frequency, offset, endTime)
			if len(running.values()) > 1:
				prevBase = tmpBase
			inputDictArr.append(inputDict)
	if len(firstEntryArr) :
		firstEntryInputDict = {}
		for (note, frequency, offset, endTime) in firstEntryArr:
			note = note.replace("-", "b")
			if note not in firstEntryInputDict.keys():
				firstEntryInputDict[note] = frequency
			else:
				if frequency < firstEntryInputDict[note]:
					firstEntryInputDict[note] = frequency
		inputDictArr.append(firstEntryInputDict)
		firstEntryArr = []
	inputs.append(inputDictArr)

#inputs structure
#[measure 1, measure 2, [ interval 1, interval 2, {note 1, note 2, note: frequency, note 4, ... }, interval 4, ... ], measure 4, ... ]
#                       ^                         ^                ^
#                   in measure 3            in interval 3        in note 3

barResult = []
weightedResult = []
weightedDict = {}
for i, inputDictArr in enumerate(inputs):
	resultArr = []
	for j, inputDict in enumerate(inputDictArr):
		tonicResult = {}
		weightedInterval = {}
		weightedInterval['bar'] = i
		weightedInterval['interval'] = j
		weightedFlag = False
		for r in recognizers:
			tonicResult[r.tonic] = r.recognize(inputDict)
			# Only I and V chords are weighted
			for cname in tonicResult[r.tonic][0]:
				#exact match
				match = [x for x in cname if x == 'i' or x == 'I' or x == 'v' or x == 'V']
				if len(match) == 1:
					#create dict for this tonic
					if r.tonic not in weightedInterval:
						weightedInterval[r.tonic] = ([], [])
					tmpDict = {}
					tmpDict['ctype'] = match[0]
					tmpDict['cname'] = cname
					weightedInterval[r.tonic][0].append(tmpDict)
					if not weightedFlag:
						weightedFlag = True
			for cname in tonicResult[r.tonic][1]:
				#possible match
				match = [x for x in cname if x == 'i' or x == 'I' or x == 'v' or x == 'V']
				if len(match) == 1:
					#create dict for this tonic
					if r.tonic not in weightedInterval:
						weightedInterval[r.tonic] = ([], [])
					tmpDict = {}
					tmpDict['ctype'] = match[0]
					tmpDict['cname'] = cname
					weightedInterval[r.tonic][1].append(tmpDict)
					if not weightedFlag:
						weightedFlag = True
		resultArr.append(tonicResult)
		if weightedFlag:
			weightedResult.append(weightedInterval)
			weightedDict[i,',',j] = weightedInterval
	barResult.append(resultArr)


#barResult structure
#[measure 1, measure 2, [ interval 1, interval, { tonic 1, tonic 2, tonic: (exact, possible), tonic 4, ... }, interval 4, ...  ], measure 4, ... ]
#                       ^                       ^                   ^
#                   in measure 3           in interval 3          in tonic 3

#weightedResult structure
#[weightedInterval 1, weightedInterval 2, {bar: i, interval: j, tonic 1, tonic 2, tonic: ([exact 1, exact 2, {ctype: V, cname: V7}, ...], [poss 1, poss2, {ctype: V, cname: V7}, ...]), ...}, ...]
#                                         ^                                       ^                          ^                                            ^
#                                    in weightedInterval 3                    in tonic 3                 in exact 3                                   in possible 3

for i, resultArr in enumerate(barResult):
	print "Bar",i

	for j, result in enumerate(resultArr):
		print "\tInterval", j
		print "\tInput notes: ", inputs[i][j].keys()
		# first print exact match
		print "\tExact match chords are: "
		for tonic in result.keys():
			if len(result[tonic][0]) > 0:
				print "\t\t", tonic, ": ", result[tonic][0]
		# then print possible match
		print "\tPossible match chords are: "
		for tonic in result.keys():
			if len(result[tonic][1]) > 0:
				print "\t\t", tonic, ": ", result[tonic][1]
		print ""

# for i, weightedInterval in enumerate(weightedResult):
# 	print "Weighted Interval", i
# 	print "At Bar ", weightedInterval['bar'], ", Interval ", weightedInterval['interval']
# 	tonicList = [tonic for tonic in weightedInterval.keys() if tonic is not 'bar' and tonic is not 'interval']
# 	tonicList.sort()
# 	print "\tExact match chords are: "
# 	for tonic in tonicList:
# 		print "\t\t", tonic, ": ", weightedInterval[tonic][0]
# 	print "\tPossible match chords are: "
# 	for tonic in tonicList:
# 		print "\t\t", tonic, ": ", weightedInterval[tonic][1]
# 	print ""

#Progression Verifying
progressionVerifier = ProgressionVerifier(resultList = barResult, weightedResult = weightedResult, weightedDict = weightedDict)
progressionVerifier.verify2()

# for bar in range(len(barResult)):
# 	if bar in resultDict:
# 		for interval in range(len(barResult[bar])):
# 			if interval in resultDict[bar]:
# 				for dicts in resultDict[bar][interval]:
# 					print dicts


