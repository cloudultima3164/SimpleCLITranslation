#!/usr/bin/env python
# Easy translation tool for working with the XLSX format translation import tool

import os
import pandas as pd
import langdetect as ld
import miniPdFuncs as pdFuncs
import translationFuncs as tf


# Help message
def printHelp():
    print("")
    print("Options:")
    print(" NEXT:        Skip the current segment")
    print(" PREVIOUS:    Return to the previous segment")
    print(" GOTO:        Go to the specified segment number")
    print("            - Syntax is \'GOTO X\', with X being the desired segment")
    print(" MATCH:       Returns exact matches for the current segment in source segments.")
    print("            - MATCH can be called with options PARTIAL and FULL, and SOURCE and TARGET")
    print("            - PARTIAL matches a user-defined string, FULL matches default string and is default behavior")
    print("            - SOURCE looks for a match in the source segments, TARGET looks for a match in the target segments")
    print("            - GETCONTEXT (or PASS to skip GETCONTEXT) can be called within the Match function")
    print(" PROPAGATE:   Propagates translation for the current segment in all target segments.")
    print(" GETCONTEXT:  Returns the the current segment, and the surrounding 2 segments")
    print("            - Syntax is \'getcontext X\' (X must be an integer), returns 2 + X surrounding segments")
    print("            - The program will return 2 segments on either side if only \'getcontext\' is entered.")
    print("            - If called from within the MATCH function, program will step through context for each match.")
    print(" RETRANSLATE: Retranslate a previous translated target segment. If you do not know the segment number,")
    print("              enter 0. The program will step through each translated segment until you quit.")
    print(" SAVE:        Save current translation progress.")
    print(" CLOSE:       Save and close the program")
    print("")


# Used to easily reset options list, as it may expand during translation due to append operations
def ResetOptions() -> list: return ['MATCH', 'PROPAGATE', 'GETCONTEXT', 'RETRANSLATE', 'SAVE', 'HELP']

# Start by asking user to select file in open file dialog.
# When we load the file into a DataFrame, we will do a little
#   more prep, like adjusting the index to start from 1,
#   and asking the user to tell us which columns to call
#   'Source' and 'Target'
File = tf.WinOpenFile()
TranslationTable = pdFuncs.FileToDf(File)[0]
TranslationTable.index = range(1, TranslationTable.shape[0] + 1)

print(TranslationTable.head(3))
SegmentPositions = input('Input your source and target segment column positions, separated by a space.\n').split()
SeriesDict = tf.DefineSourceAndTarget(int(SegmentPositions[0]), int(SegmentPositions[1]))
TargetSeries = TranslationTable.columns[SeriesDict['TARGET']]

Options = ResetOptions()

answer = tf.CheckInput(
    input('Perform initial Ishin translation file cleanup?[Y/n]\n').lower(),
    Choices=['y','n'])
if answer == 'quit':
    print('Exiting...')
    exit(1)
# YesNo = ['y', 'n']
# answer = input('Perform initial Ishin translation file cleanup?[Y/n]\n').lower()
# while answer not in YesNo:
#     answer = input("Invalid input. Please input \'y\' or \'n\'\n")

if answer == 'y':
    tf.IshinFileCleaner(TranslationTable, TargetSeries)

# Segment movement functions
def NextSegment(CurrentSegment) -> int: return CurrentSegment + 1
def PreviousSegment(CurrentSegment) -> int: return CurrentSegment - 1
def GoToSegment(SegmentNumber) -> int: return SegmentNumber

Segment = 1
CLOSE_FILE: bool = 0
# Loop through segments
while CLOSE_FILE == 0:
    SourceSegment = TranslationTable.iat[Segment - 1, SeriesDict['SOURCE']]
    TargetSegment = TranslationTable.iat[Segment - 1, SeriesDict['TARGET']]

    # Detect segment language. If english, then iterate loop
    # This doesn't work well all of the time if segment strings are short.
    try:
        lang = ld.detect(TargetSegment)
    except:
        pass
    else:
        if lang == 'en':
            continue

    # Prints source segment and requests translation input
    # If you enter a valid option, the next while block will be executed
    # If you enter SAVE, the program will exit the loop and save your progress
    tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
    Target, TargetUpper = tf.inputTranslation()
    if TargetUpper.split()[0] in ['GETCONTEXT', 'MATCH']:
        Options.append(TargetUpper)

    # if TargetUpper == "CLOSE":  # Save and close
    #     print("\n")
    #     break
    # if TargetUpper == "NEXT":  # Skip this segment
    #     print("\n")
    #     continue

    if Target[0] == "^":
        print("Invalid input")
        while Target[0] == "^":
            Target, TargetUpper = tf.inputTranslation(False)
            if TargetUpper.split()[0] == 'GETCONTEXT':
                Options.append(TargetUpper)

    # While loop for checking and propagating translations
    while TargetUpper in Options:
        while TargetUpper not in Options:
            print("Option {} is invalid. Please choose {}".format(Target, Options))
            Target, TargetUpper = tf.inputTranslation(False)

        if TargetUpper.split()[0] == 'MATCH':
            # Prints matching results if the same translation exists elsewhere in the document
            try:
                MatchSeries = TargetUpper.split()[1]
            except:
                MatchSeries = 'SOURCE'
            else:
                MatchSeries = tf.CheckInput(
                    input("\nInvalid option for series. Please choose \'SOURCE\' or \'TARGET\'.\n"),
                    Choices=['SOURCE', 'TARGET'])
            finally:
                try:
                    MatchType = TargetUpper.split()[2]
                except:
                    MatchType = 'FULL'
                else:
                    MatchType = tf.CheckInput(
                        input("\nInvalid option for series. Please choose FULL or PARTIAL.\n").upper(),
                        Choices=['FULL', 'PARTIAL'])
                finally:
                    if MatchType == 'PARTIAL':
                        MatchString = input("\nPlease enter string to match.\n")
                    else:
                        if MatchSeries == 'SOURCE':
                            MatchString = TranslationTable.iat[Segment - 1, SeriesDict['SOURCE']]
                        elif MatchSeries == 'TARGET':
                            MatchString = TranslationTable.iat[Segment - 1, SeriesDict['TARGET']]
                    tf.MatchSegments(TranslationTable, MatchSeries, SeriesDict['SOURCE'], SeriesDict['TARGET'], MatchString, MatchType)
            tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
            Options = ResetOptions()
            Target, TargetUpper = tf.inputTranslation()

        elif TargetUpper == 'PROPAGATE':
            # Propagate translation to all other target segments with a matching source segment
            print("Please enter the translation:\n")
            # Target, TargetUpper = tf.inputTranslation(False)
            # MatchDf = TranslationTable.loc[SourceSegment[SeriesDict['SOURCE']]]
            # tf.Propagate(MatchDf, 2)
            check = tf.Propagate(TranslationTable, SourceSegment, SeriesDict['SOURCE'], SeriesDict['TARGET'])
            if check == 'quit':
                tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
                Target, TargetUpper = tf.inputTranslation()
            else:
                TargetUpper = 'NEXT'

        elif TargetUpper.split()[0] == 'GETCONTEXT':
            # Print context around current segment
            EmptyDf = pd.DataFrame(columns=['empty'])
            try:
                PlusAlpha = TargetUpper.split()[1]
            except:
                tf.GetContextSegs(TranslationTable, Segment - 1, EmptyDf)
            else:
                tf.GetContextSegs(TranslationTable, Segment - 1, EmptyDf, PlusAlpha)
            Options = ResetOptions()
            Target, TargetUpper = tf.inputTranslation()

        elif TargetUpper == 'RETRANSLATE':
            # Re-translate some previously translated segment
            Answer = int(tf.CheckInput(
                input("Please type segment number. If you do not know it, input \'0\'\n"),
                Type=int)) - 1
            tf.retranslateSegment(TranslationTable, SeriesDict['SOURCE'], SeriesDict['TARGET'], int(Answer))
            tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
            Target, TargetUpper = tf.inputTranslation()

        elif TargetUpper == 'SAVE':
            # Save progress without closing
            print("Saving..")
            pdFuncs.DfToFile(TranslationTable, File)
            tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
            Target, TargetUpper = tf.inputTranslation()
        elif TargetUpper == 'HELP':
            printHelp()
            tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
            Target, TargetUpper = tf.inputTranslation()

        if TargetUpper.split()[0] == 'GETCONTEXT':
            Options.append(TargetUpper)

    if TargetUpper.split()[0] == "GOTO":
        try:
            SegmentNumber = int(TargetUpper.split()[1])
        except:
            SegmentNumber = int(tf.CheckInput(
                input("Please specify a segment number.\n"),
                Type=int))
        finally:
            print("")
            Segment = GoToSegment(SegmentNumber)
            continue
    elif TargetUpper == "NEXT":
        print("")
        Segment = NextSegment(Segment)
        continue
    elif TargetUpper == "PREVIOUS":
        print("")
        Segment = PreviousSegment(Segment)
        continue
    elif TargetUpper == 'CLOSE':
        CLOSE_FILE = 1
        continue

    TranslationTable.iat[Segment - 1, SeriesDict['TARGET']] = Target
    if Segment == TranslationTable.index[-1]:
        CheckClose = tf.CheckInput(
            input('Save and quit?[Y/n]').lower(),
            Choices=['y', 'n']
            )
        if CheckClose == 'y':
            print("Saving...")
            pdFuncs.DfToFile(TranslationTable, File)
            CLOSE_FILE = 1
    else:
        Segment = NextSegment(Segment)
    print("")

print("Exiting...")
