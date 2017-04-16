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

# all possible feature combination for OnBeat mode
identifier.runProgression(choice=verifierIntervalChoiceClass.OnBeat, featureList=[verifierFeatureClass.ChordFunction], verbal=False, output=True)
# identifier.runProgression(choice=verifierIntervalChoiceClass.OnBeat, featureList=[verifierFeatureClass.FirstComeFirstServe], verbal=False, output=True)
identifier.runProgression(choice=verifierIntervalChoiceClass.OnBeat, featureList=[verifierFeatureClass.VtoIProgression, verifierFeatureClass.ChordFunction], verbal=False, output=True)
# identifier.runProgression(choice=verifierIntervalChoiceClass.OnBeat, featureList=[verifierFeatureClass.VtoIProgression, verifierFeatureClass.FirstComeFirstServe], verbal=False, output=True)


# all possible feature combination for AllIntervalType mode
identifier.runProgression(choice=verifierIntervalChoiceClass.AllIntervalType, featureList=[verifierFeatureClass.ChordFunction], verbal=False, output=True)
# identifier.runProgression(choice=verifierIntervalChoiceClass.AllIntervalType, featureList=[verifierFeatureClass.FirstComeFirstServe], verbal=False, output=True)
identifier.runProgression(choice=verifierIntervalChoiceClass.AllIntervalType, featureList=[verifierFeatureClass.VtoIProgression, verifierFeatureClass.ChordFunction], verbal=False, output=True)
# identifier.runProgression(choice=verifierIntervalChoiceClass.AllIntervalType, featureList=[verifierFeatureClass.VtoIProgression, verifierFeatureClass.FirstComeFirstServe], verbal=False, output=True)



# all possible feature combination for ChangedBaseline mode
identifier.runProgression(choice=verifierIntervalChoiceClass.ChangedBaseline, featureList=[verifierFeatureClass.ChordFunction], verbal=False, output=True)
# identifier.runProgression(choice=verifierIntervalChoiceClass.ChangedBaseline, featureList=[verifierFeatureClass.FirstComeFirstServe], verbal=False, output=True)
identifier.runProgression(choice=verifierIntervalChoiceClass.ChangedBaseline, featureList=[verifierFeatureClass.VtoIProgression, verifierFeatureClass.ChordFunction], verbal=False, output=True)
# identifier.runProgression(choice=verifierIntervalChoiceClass.ChangedBaseline, featureList=[verifierFeatureClass.VtoIProgression, verifierFeatureClass.FirstComeFirstServe], verbal=False, output=True)