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
verifierFeatureClass = ChordIdentifier.ProgressionVerifier.ProgressionVerifier.ProgressionFeature
verifierIntervalChoiceClass = ChordIdentifier.ProgressionVerifier.ProgressionVerifier.ProgressionIntervalChoice


featureList = [verifierFeatureClass.ChordFunction]
# identifier.runProgression(barLimit=3, choice=verifierIntervalChoiceClass.OnBeat, featureList=featureList, verbal=True, output="canonInD_OnBeat.xml")
# identifier.runProgression(barLimit=3, choice=verifierIntervalChoiceClass.AllIntervalType, featureList=featureList, verbal=True, output="canonInD_AllIntervalType.xml")

identifier.runProgression(barLimit=3, choice=verifierIntervalChoiceClass.ChangedBaseline, featureList=featureList, verbal=True, output="canonInD_ChangedBaseline_TtoT.xml")