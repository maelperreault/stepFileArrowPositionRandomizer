# Stepfile Arrow Randomizer v.0.1 by Ombar
#
# Randomizes arrow positions in (.sm) files
# All (.sm) files in program directory and sub-directorries are randomized
# Backups of (.sm) files are created in case something goes terribly wrong
# Randomization is really simple for now and simply prevents too many of the same arrows in a row
# Basically just moves existing arrows around, you need to create the arrows first
#
# HOW TO USE
# Use ArrowVortex to create basic (.sm) file)
# Add steps and hold arrows following the beat of the song
# Run Randomizer in the same directory as the file to randomize arrow positions

import os
import random
from shutil import copyfile

ARROW_COUNT = 4
ARROW_MAX_REPEAT = 2
ARROW_CAN_REPEAT_LAST_STEP = False

# stepfile (.sm) arrow values
ARROW_EMPTY = '0'
ARROW_STEP = '1'
ARROW_HOLD_START = '2'
ARROW_HOLD_STOP = '3'
ARROW_ROLL_START = '4'
ARROW_MINE = 'M'

DEBUG_ENABLED = False


def isValidArrowLine(line):
    # TODO: make generic
    return line and len(line) == ARROW_COUNT and line != "0000"

# test if arrow doesn't repeat too much


def isPreferredArrow(value, index, isJump, arrowCountStep, arrowCountHold, arrowCountJump, lastStepArrowIndex):

    # mines don't matter put them anywhere
    if value == ARROW_MINE:
        return False

    # dont prefer repeat of last step
    if value == ARROW_STEP and not isJump and index == lastStepArrowIndex:
        return False

    arrowCount = []

    if value == ARROW_STEP:
        arrowCount = arrowCountStep
    else:
        arrowCount = arrowCountHold

    minArrowCount = min(arrowCount)
    maxArrowCount = max(arrowCount)

    if arrowCount[index] == maxArrowCount and maxArrowCount - minArrowCount >= ARROW_MAX_REPEAT:
        return False

    if isJump:
        arrowCount = arrowCountJump

        minArrowCount = min(arrowCount)
        maxArrowCount = max(arrowCount)

        if arrowCount[index] == maxArrowCount and maxArrowCount - minArrowCount >= ARROW_MAX_REPEAT:
            return False

    return True


def parseFile(fileName, directoryPath):
    if fileName.endswith(".sm"):
        filePath = os.path.join(directoryPath, fileName)

        backupFileIndex = 1
        backupFilePath = filePath + \
            ".{0:0=3d}".format(backupFileIndex) + ".bak"
        while os.path.exists(backupFilePath):
            backupFileIndex += 1
            backupFilePath = filePath + \
                ".{0:0=3d}".format(backupFileIndex) + ".bak"

        copyfile(filePath, backupFilePath)

        print("************************************************************")
        print(" File : \n   {}\n".format(filePath))
        print(" Created backup file : \n   {}\n".format(backupFilePath))
        print(" Randomization started ...\n")

        with open(filePath) as f:

            # get a list of all lines of file
            lines = f.readlines()
            newLines = []

            isHoldingArrows = [False for i in range(ARROW_COUNT)]
            newHoldingArrowsIndex = [-1 for i in range(ARROW_COUNT)]
            arrowCountStep = [0 for i in range(ARROW_COUNT)]
            arrowCountHold = [0 for i in range(ARROW_COUNT)]
            arrowCountJump = [0 for i in range(ARROW_COUNT)]
            lastStepArrowIndex = -1

            for lineNumber in range(len(lines)):
                line = lines[lineNumber].strip()

                # only handle arrows lines that are not empty
                if isValidArrowLine(line):  # and lineNumber < 100:

                    if DEBUG_ENABLED:
                        print(" Line {} : {}".format(lineNumber, line))

                    newLine = [ARROW_EMPTY for i in range(ARROW_COUNT)]

                    lineStepCount = line.count(ARROW_STEP)
                    lineHoldCount = line.count(ARROW_HOLD_START)
                    lineRollCount = line.count(ARROW_ROLL_START)
                    lineMineCount = line.count(ARROW_MINE)

                    isJump = lineStepCount + lineHoldCount + lineRollCount >= 2

                    # set new index for holdroll stop arrows first so they are not used by other arrows
                    for i in range(ARROW_COUNT):
                        arrowValue = line[i]

                        if arrowValue == ARROW_HOLD_STOP:
                            newLine[newHoldingArrowsIndex[i]] = arrowValue
                            newHoldingArrowsIndex[i] = -1

                    # randomize all non empty arrows
                    for arrowIndex in range(ARROW_COUNT):
                        arrowValue = line[arrowIndex]

                        if (
                            arrowValue == ARROW_STEP or
                            arrowValue == ARROW_HOLD_START or
                            arrowValue == ARROW_ROLL_START or
                            arrowValue == ARROW_MINE
                        ):
                            # find a new random spot for the arrow
                            validArrowIndexes = []
                            for i in range(ARROW_COUNT):
                                if newLine[i] == ARROW_EMPTY and not isHoldingArrows[i]:
                                    validArrowIndexes.append(i)

                            preferredArrowIndexes = []
                            for i in validArrowIndexes:
                                if isPreferredArrow(arrowValue, i, isJump, arrowCountStep, arrowCountHold, arrowCountJump, lastStepArrowIndex):
                                    preferredArrowIndexes.append(i)

                            randomIndex = 0

                            if len(preferredArrowIndexes) > 0:
                                random.shuffle(preferredArrowIndexes)
                                randomIndex = preferredArrowIndexes[0]
                            else:
                                random.shuffle(validArrowIndexes)
                                randomIndex = validArrowIndexes[0]

                            newLine[randomIndex] = arrowValue
                            isHoldingArrows[randomIndex] = True

                            # keep arrows count for diversity
                            if arrowValue == ARROW_HOLD_START or arrowValue == ARROW_ROLL_START:
                                arrowCountHold[randomIndex] += 1

                            if arrowValue == ARROW_STEP and not isJump:
                                arrowCountStep[randomIndex] += 1

                            if isJump:
                                arrowCountJump[randomIndex] += 1

                            # keep new index for hold/roll arrows
                            if arrowValue == ARROW_HOLD_START or arrowValue == ARROW_ROLL_START:
                                newHoldingArrowsIndex[arrowIndex] = randomIndex

                            if arrowValue == ARROW_STEP and not isJump:
                                lastStepArrowIndex = randomIndex

                            if DEBUG_ENABLED:
                                print("  Index : {} ".format(arrowIndex))
                                print(
                                    "  Step {} [{}] -> [{}]".format(arrowValue, arrowIndex, randomIndex))
                                print("  Valid : {}".format(validArrowIndexes))
                                print("  Preferred : {}".format(
                                    preferredArrowIndexes))
                                print("  Hold : {}".format(isHoldingArrows))
                                print("  Last Step : {}".format(
                                    lastStepArrowIndex))
                                print("")

                    # free arrows for the next line
                    for i in range(ARROW_COUNT):
                        if newLine[i] == ARROW_STEP or newLine[i] == ARROW_MINE or newLine[i] == ARROW_HOLD_STOP:
                            isHoldingArrows[i] = False

                    newLineStepCount = newLine.count(ARROW_STEP)
                    newLineHoldCount = newLine.count(ARROW_HOLD_START)
                    newLineRollCount = newLine.count(ARROW_ROLL_START)
                    newLineMineCount = newLine.count(ARROW_MINE)

                    if (
                        lineStepCount != newLineStepCount or
                        lineHoldCount != newLineHoldCount or
                        lineRollCount != newLineRollCount or
                        lineMineCount != newLineMineCount
                    ):
                        print("  ERROR : {} -> {}".format(line, newLine))

                    newLine = "".join(newLine)
                    newLines.append(newLine + '\n')
                else:
                    newLines.append(lines[lineNumber])

            # save the new randomized lines back to file
            fileWriter = open(filePath, 'w')
            fileWriter.writelines(newLines)
            fileWriter.close()

            print(" DONE!")
            print("************************************************************")
            print("")

# parse all (.sm) files in this directory and all sub directories


def parseDirectory(directoryName, directoryBasePath):

    # get current working dir
    directoryPath = os.path.join(directoryBasePath, directoryName)

    # try parse all documents as files or directories
    if os.path.isdir(directoryPath):
        for fileName in os.listdir(directoryPath):
            parseFile(fileName, directoryPath)
            parseDirectory(fileName, directoryPath)


# parse all (.sm) files in the current working directory and all sub directories
directoryPath = os.getcwd()

print("************************************************************")
print(" Stepfile Arrow Randomizer v.0.1 by Ombar")
print("")
print(" Randomizes arrow positions in (.sm) files")
print(" All (.sm) files in program directory and sub-directorries are randomized")
print(" Backups of (.sm) files are created in case something goes terribly wrong")
print(" Randomization is really simple for now and simply prevents too many of the same arrows in a row")
print(" Just moves existing arrows around, you need to create the arrows first")
print(" Run a couple times and test until you get a pattern you like")
print("")
print(" HOW TO USE")
print(" Use ArrowVortex to create basic (.sm) file")
print(" Add steps and hold arrows following the beat of the song")
print(" Run Randomizer in the same directory as the file to randomize arrow positions")
print("")
print("************************************************************")
print(" Randomizing (.sm) files in directory and sub-directories :")
print("    {}".format(directoryPath))
print("************************************************************")
print("")

parseDirectory("", directoryPath)

# wait for input before closing
print("Press any key to continue...", end='')
input()
