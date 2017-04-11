import os
import ChordIdentifier
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
	rawScore = music21.converter.parse(curPath+inputFileName)  #for relative path
except music21.converter.ConverterException:
	try:
		rawScore = music21.converter.parse(inputFileName)  #for absolute path
	except music21.converter.ConverterException:
		print "Fail to read input file"
		sys.exit(1)
identifier = ChordIdentifier.Identifier(score=rawScore)
# identifier.printPreparedScore()
featureList = [ChordIdentifier.ProgressionVerifier.ProgressionVerifier.ProgressionFeatures.PriorAllIntervalType]
identifier.runProgression(barLimit=3, featureList=featureList, verbal=True, output="output.xml")