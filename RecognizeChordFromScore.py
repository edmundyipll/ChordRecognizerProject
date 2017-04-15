import os
import ChordIdentifier
import music21
import sys

curPath = os.getcwd() + '/'
try:
	inputFilename = sys.argv[1]
except IndexError:
	print "Fail to read input file name" 
	sys.exit(1)
#read input

print "Reading input musicxml file"
try:
	rawScore = music21.converter.parse(curPath+inputFilename)  #for relative path
except music21.converter.ConverterException:
	try:
		rawScore = music21.converter.parse(inputFilename)  #for absolute path
	except music21.converter.ConverterException:
		print "Fail to read input file"
		sys.exit(1)
inputFilename = inputFilename.split('/')[-1]

# first search for saved storage
print "Searching storage folder for saved ChordIdentifier"
identifier = ChordIdentifier.Identifier.load(scoreFilename=inputFilename)

if not identifier:
	print "Initializing new ChordIdentifier"
	identifier = ChordIdentifier.Identifier(score=rawScore, scoreFilename=inputFilename)
	print "Save into storage folder"
	identifier.save(overwrite=True)
	
# identifier.printPreparedScore()
verifierFeatureClass = ChordIdentifier.ProgressionVerifier.ProgressionFeature
verifierIntervalChoiceClass = ChordIdentifier.ProgressionVerifier.ProgressionIntervalChoice


featureList = [verifierFeatureClass.ChordFunction]
# identifier.runProgression(barLimit=3, choice=verifierIntervalChoiceClass.OnBeat, featureList=featureList, verbal=True, output="canonInD_OnBeat.xml")
# identifier.runProgression(barLimit=3, choice=verifierIntervalChoiceClass.AllIntervalType, featureList=featureList, verbal=True, output="canonInD_AllIntervalType.xml")

# identifier.runProgression(barLimit=3, choice=verifierIntervalChoiceClass.AllIntervalType, featureList=featureList, verbal=True)