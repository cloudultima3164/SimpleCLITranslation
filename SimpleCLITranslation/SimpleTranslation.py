#!/usr/bin/env python
# Easy translation tool for working with the XLSX format translation import tool

import os
import pandas as pd
import numpy as np
import miniPdFuncs as pdFuncs
import translationFuncs as tf
import os
import argparse
from argparse import RawTextHelpFormatter


############################
#        FUNCTIONS
############################

def parse_options():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('-o', '--Option', nargs=1, type=str,
                        choices=['','length', 'find', 'pos_at_length'],
                        default=[''],
                        help='Options to change program output. \
                              \n    \'length\': return length of source without opening file \
                              \n    \'find\': returns segments that contain specified string  \
                              \n        use the --argument option to specify the search string. \
                              \n    \'pos_at_length\': returns the segment at which character N is found \
                              \n        use the --argument option to specify N.')
    parser.add_argument('-a', '--Argument', default='',
                        help='Argument used in conjunction with the \'pos_at_length\' and \'find\' options.')
    return parser.parse_args()


def parse_file(need_segments=True):
    file_path = tf.WinOpenFile()
    df = pdFuncs.FileToDf(file_path)[0]
    if need_segments:
        # df.index = range(1, df.shape[0] + 1)
        print(df.head(3))
        SegmentPositions = input('Input your source and target segment column positions, separated by a space.\n').split()
        return dict(Table=df, File=file_path, SeriesIndexes=tf.DefineSourceAndTarget(int(SegmentPositions[0]), int(SegmentPositions[1])))
    else:
        return dict(Table=df, File=file_path)

def return_length(empty=None):
    parse_file_output = parse_file()
    Table = parse_file_output['Table']
    LengthColumn = Table.columns[parse_file_output['SeriesIndexes']['SOURCE']]
    Length = Table[LengthColumn].str.len().sum()
    print('Length of source is {} characters'.format(Length))

def find_string(string=''):
    parse_file_output = parse_file()
    Table = parse_file_output['Table']
    SeriesIndexes = parse_file_output['SeriesIndexes']
    mask = np.column_stack([Table[col].astype('str').str.contains(string.lower(), case=False) for col in Table.columns])
    search_result = Table.loc[mask.any(axis=1)]
    search_result_formatted =["\nSegment {}\nSource: {}\nTarget: {}". \
                                format(search_result.index[x], 
                                        search_result.iat[x, SeriesIndexes['SOURCE']],
                                        search_result.iat[x, SeriesIndexes['TARGET']])
                                for x in range(search_result.shape[0])]
    print('\n\nMatched strings\n--------------\n')
    print(*search_result_formatted, sep='\n')

def find_string_at_length(position=1000):
    position = int(position)
    parse_file_output = parse_file()
    Table = parse_file_output['Table']
    LengthColumn = Table.columns[parse_file_output['SeriesIndexes']['SOURCE']]
    current_position = 0
    segment = 1
    for record in Table[LengthColumn]:
        current_position = current_position + len(record)
        if current_position >= position:
            print("\nSegment containing character:\n")
            print("\nSegment {}\nSource: {}". \
                    format(segment, record))
            return
        segment = segment + 1
    raise ValueError('Source shorter than {} characters. No match found.'.format(position))


# Help message
def printHelp():
    print("")
    print("Options:")
    print(" -HELP:        Display this message")
    print(" -NEXT:        Skip the current segment")
    print(" -PREVIOUS:    Return to the previous segment")
    print(" -GOTO:        Go to the specified segment number")
    print("             - Syntax is \'-GOTO X\', with X being the desired segment")
    print(" -MATCH:       Returns exact matches for the current segment in source segments.")
    print("             - -MATCH can be called with options PARTIAL and FULL, and SOURCE and TARGET")
    print("             - PARTIAL matches a user-defined string, FULL matches default string and is default behavior")
    print("             - SOURCE looks for a match in the source segments, TARGET looks for a match in the target segments")
    print("             - -CONTEXT (or PASS to skip -CONTEXT) can be called within the Match function")
    print(" -PROP:        Propagates a new or exisiting translation to all matching target segments.")
    print(" -CONTEXT:     Returns the the current segment, and the surrounding 2 segments")
    print("             - Syntax is \'getcontext X\' (X must be an integer), returns 2 + X surrounding segments")
    print("             - The program will return 2 segments on either side if only \'getcontext\' is entered.")
    print("             - If called from within the -MATCH function, program will step through context for each match.")
    print(" -RETRANSLATE: Retranslate a previous translated target segment. If you do not know the segment number,")
    print("               enter 0. The program will step through each translated segment until you quit.")
    print(" -SAVE:        Save current translation progress.")
    print(" -CLOSE:       Close the program without saving.")
    print("")


# Used to easily reset options list, as it may expand during translation due to append operations
def ResetOptions() -> list: return ['-MATCH',
                                    '-PROP',
                                    '-CONTEXT',
                                    '-RETRANSLATE',
                                    '-SAVE',
                                    '-HELP']


def AllOptions() -> list: return ['-MATCH',
                                  '-PROP',
                                  '-CONTEXT',
                                  '-RETRANSLATE',
                                  '-SAVE',
                                  '-HELP',
                                  '-NEXT',
                                  '-PREVIOUS',
                                  '-GOTO',
                                  '-CLOSE']

# Segment movement functions
def NextSegment(CurrentSegment) -> int: return CurrentSegment + 1
def PreviousSegment(CurrentSegment) -> int: return CurrentSegment - 1
def GoToSegment(SegmentNumber) -> int: return SegmentNumber


############################
#         MAIN
############################


def main(empty=None):
    # Start by asking user to select file in open file dialog.
    parse_file_output = parse_file()
    TranslationTable = parse_file_output['Table']
    File = parse_file_output['File']


    # Setting up temp file in case of a crash or unintentional close
    FileSplit = os.path.split(File)
    temp_directory = os.path.join(FileSplit[0], 'temp')
    temp_file_path = os.path.join(temp_directory, '{}{}'.format('~', FileSplit[1]))
    temp_file_path = '{}{}'.format(os.path.splitext(temp_file_path)[0], '.csv')

    if not os.path.exists(temp_directory):
        os.mkdir(temp_directory)
    if not os.path.exists(temp_file_path):
        TranslationTable.to_csv(temp_file_path)
    else:
        temp_df = pd.read_csv(temp_file_path)
        if not TranslationTable.equals(temp_file_path):
            restore = tf.CheckInput(input("\nThe program may have closed incorrectly during the last session. \
                                \nWould you like to restore to the most recent point?[Y/n]\n"),
                                Choices=['y', 'n'])
            if restore == 'y':
                TranslationTable.update(temp_df, overwrite=True)
        temp_df = ''

    # When we load the file into a DataFrame, we will do a little
    #   more prep, like adjusting the index to start from 1,
    #   and asking the user to tell us which columns to call
    #   'Source' and 'Target'

    TranslationTable.index = range(1, TranslationTable.shape[0] + 1)
    SeriesDict = parse_file_output['SeriesIndexes']
    TargetSeries = TranslationTable.columns[SeriesDict['TARGET']]

    Options = ResetOptions()

    answer = tf.CheckInput(
        input('Perform initial file cleanup?[Y/n]\n').lower(),
        Choices=['y','n'])
    if answer == 'quit':
        print('Exiting...')
        exit(1)

    if answer == 'y':
        tf.FileCleaner(TranslationTable, TargetSeries)

    Segment = 1
    CLOSE_FILE: bool = 0
    # Loop through segments
    while CLOSE_FILE == 0:
        if (Segment) > TranslationTable.shape[0]:
            Continue = tf.CheckInput(input('End of file reached. Continue editing or save and quit? [continue/save]\n'),
                        Choices=['continue', 'save'])
            if Continue == 'continue': 
                Segment = PreviousSegment(Segment)
            elif Continue == 'save':
                print("\nSaving...")
                pdFuncs.DfToFile(TranslationTable, File)
                CLOSE_FILE = 1
                continue

        if CLOSE_FILE == 0:
            SourceSegment = TranslationTable.iat[Segment - 1, SeriesDict['SOURCE']]
            TargetSegment = TranslationTable.iat[Segment - 1, SeriesDict['TARGET']]

        # Detect segment language. If english, then iterate loop
        # This doesn't work well all of the time if segment strings are short.
        try:
            maybe_lang = ld.detect(TargetSegment)
        except:
            pass
        else:
            if maybe_lang == 'en':
                continue

        # Prints source segment and requests translation input
        # If you enter a valid option, the next while block will be executed
        # If you enter -SAVE, the program will exit the loop and save your progress
        tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
        Target, TargetUpper = tf.inputTranslation(valid_options=AllOptions())
        if TargetUpper.split()[0] in ['-CONTEXT', '-MATCH']:
            Options.append(TargetUpper)

        # While loop for checking and propagating translations
        while TargetUpper in Options:
            while TargetUpper not in Options:
                print("Option {} is invalid. Please choose {}".format(Target, Options))
                Target, TargetUpper = tf.inputTranslation(False, valid_options=AllOptions())

            if TargetUpper.split()[0] == '-MATCH':
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
                            MatchString = TranslationTable.iat[Segment - 1, SeriesDict[MatchSeries]]
                        return_value = tf.MatchSegments(TranslationTable, MatchSeries, SeriesDict['SOURCE'], SeriesDict['TARGET'], MatchString, MatchType)
                if return_value == 'propagate':
                    TargetUpper = '-NEXT'
                else:
                    tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
                    Options = ResetOptions()
                    Target, TargetUpper = tf.inputTranslation(valid_options=AllOptions())

            elif TargetUpper == '-PROP':
                # Propagate translation to all other target segments with a matching source segment
                check = tf.Propagate(TranslationTable, SourceSegment, SeriesDict['SOURCE'], SeriesDict['TARGET'])
                if check == 'quit':
                    tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
                    Target, TargetUpper = tf.inputTranslation(valid_options=AllOptions())
                else:
                    TargetUpper = '-NEXT'

            elif TargetUpper.split()[0] == '-CONTEXT':
                # Print context around current segment
                EmptyDf = pd.DataFrame(columns=['empty'])
                try:
                    PlusAlpha = TargetUpper.split()[1]
                except:
                    tf.GetContextSegs(TranslationTable, Segment - 1, EmptyDf)
                else:
                    tf.GetContextSegs(TranslationTable, Segment - 1, EmptyDf, PlusAlpha)
                Options = ResetOptions()
                Target, TargetUpper = tf.inputTranslation(valid_options=AllOptions())

            elif TargetUpper == '-RETRANSLATE':
                # Re-translate some previously translated segment
                Answer = int(tf.CheckInput(
                    input("Please type segment number. If you do not know it, input \'0\'\n"),
                    Type=int)) - 1
                tf.retranslateSegment(TranslationTable, SeriesDict['SOURCE'], SeriesDict['TARGET'], int(Answer))
                tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
                Target, TargetUpper = tf.inputTranslation(valid_options=AllOptions())

            elif TargetUpper == '-SAVE':
                # Save progress without closing
                print("Saving..")
                pdFuncs.DfToFile(TranslationTable, File)
                tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
                Target, TargetUpper = tf.inputTranslation(valid_options=AllOptions())
            elif TargetUpper == '-HELP':
                printHelp()
                tf.printCurrentSegment(Segment, TranslationTable.shape[0], SourceSegment, TargetSegment)
                Target, TargetUpper = tf.inputTranslation(valid_options=AllOptions())

            if TargetUpper.split()[0] == '-CONTEXT':
                Options.append(TargetUpper)

        if TargetUpper.split()[0] == "-GOTO":
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
        elif TargetUpper == "-NEXT":
            print("")
            Segment = NextSegment(Segment)
            continue
        elif TargetUpper == "-PREVIOUS":
            print("")
            Segment = PreviousSegment(Segment)
            continue
        elif TargetUpper == '-CLOSE':
            CLOSE_FILE = 1
            continue

        TranslationTable.iat[Segment - 1, SeriesDict['TARGET']] = Target
        TranslationTable.to_csv(temp_file_path)
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


if __name__ == '__main__':
    args = parse_options()
    dispatcher = {
        '': main,
        'length': return_length,
        'find': find_string,
        'pos_at_length': find_string_at_length
    }
    dispatcher[args.Option[0]](args.Argument)