import miniPdFuncs
import numpy as np

# Opens Windows open file dialog and retrurns the path of the chosen file
def WinOpenFile():
    import sys
    import ctypes
    co_initialize = ctypes.windll.ole32.CoInitialize
    #   Force STA mode
    co_initialize(None)

    import clr

    clr.AddReference('System.Windows.Forms')

    from System.Windows.Forms import OpenFileDialog

    file_dialog = OpenFileDialog()
    ret = file_dialog.ShowDialog()
    if ret != 1:
        print("Cancelled")
        sys.exit()
    print(file_dialog.FileName)
    return file_dialog.FileName


# Quick function to help define source and target columns
def DefineSourceAndTarget(*args): return dict(SOURCE=args[0]-1, TARGET=args[1]-1)


# Ensures input has only expected answers, not that the Boolean parameter must be passed
#   with 'Input' replacing your parameter name to properly function
# Boolean should be passed as a string, as it will need to be reevaluated.
def CheckInput(Input, Choices: list = None, Type: type = None, Boolean: str = None):
    if Input.lower() == 'quit':
        return 'quit'
    Params = [(key, value) for key, value in locals().items() if value is not None]
    ComparisonType = Params[1][0]
    ComparisonArg = Params[1][1]
    if len(Params) != 2:
        raise TypeError('Function expected 2 arguments but found {}'.format(len(Params)))
    def ListType(Input, Lst):
        while Input not in Lst:
            Input = input('Invalid input. Please enter one of the following choices: {}\n'.format(Lst)).lower()
        return Input
    def BoolType(Input, IsTrue):
        while not eval(IsTrue):
            Input = input('Requirement \'{}\' not met. Please enter a matching input.\n'.format(Boolean))
        return Input
    def TypeType(Input, Type):
        type_is_correct = False
        while not type_is_correct:
            try:
                Type(Input)
            except:
                Input = input('Invalid input. Expected type {}, but got type {}.\n'.format(Type, type(Input))).lower()
            else:
                type_is_correct = True
        return Input

    Dispatcher = {
        "Choices": ListType,
        "Boolean": BoolType,
        "Type": TypeType
    }
    # Some black magic happening here.
    # Parameters passed to the function have been converted to (key, value) tuples
    #   and we're just calling them along with the appropriate comparison function by index here.
    # We know passed order will always be consistent and there will always be a consistent
    #   number of arguments, so this shortcut will fly for now...
    # It's more funny than it is pretty.
    Input = Dispatcher[ComparisonType](Input, ComparisonArg)
    return Input


# Cleans up Ishin-style translation files
def IshinFileCleaner(Dataframe, TargetIndex):
    Dataframe[TargetIndex] = Dataframe[TargetIndex].map("")
    return Dataframe


# Prints current segment
def printCurrentSegment(SegmentIndex, SegmentCount, SourceSegment, TargetSegment):
    print("Segment {}/{}:\n\n Source: {}\n Target: {}\n".format(SegmentIndex,
                                    SegmentCount, SourceSegment, TargetSegment))


# Default user prompt to enter translation or option
def inputTranslation(Message=True):
    if Message:
        Input = CheckInput(
            input(" Please enter a translation or an option:\n\n"),
            Boolean="(Input != '')")
        UpperInput = Input.upper()
        return Input, UpperInput
    else:
        Input = CheckInput(input(), Boolean="(Input != '')")
        UpperInput = Input.upper()
        return Input, UpperInput


# Propagates an exact match over an entire document
# def Propagate(Translation, MatchDataFrame, TargetIndex):
def Propagate(Dataframe, SourceText, SourceIndex, TargetIndex):
    SourceName = Dataframe.columns[SourceIndex]
    TargetName = Dataframe.columns[TargetIndex]
    MatchDataFrame = Dataframe.loc[Dataframe[SourceName] == SourceText]
    if MatchDataFrame.empty:
        print("No matches to propagate to.")
    else:
        CurrentOrPrevious = CheckInput(
                             input('Propagate a new translation or a previously translated segment? [new/previous]\n').lower(),
                             Choices = ['new', 'previous'])

        if CurrentOrPrevious == 'new':
            print('Please enter translation:')
            Dataframe.loc[Dataframe[SourceName] == SourceText, TargetName] = inputTranslation(False)[0]
        elif CurrentOrPrevious == 'previous':
            print(MatchDataFrame.head(5))
            PropagateSegment = CheckInput(
                                input('Please input the segment that will be propagated.\n'),
                                Type = int)

            if PropagateSegment == 'quit':
                return 'quit'
            Dataframe.loc[Dataframe[SourceName] == SourceText, TargetName] = Dataframe.iat[PropagateSegment - 1, TargetIndex]
        elif CurrentOrPrevious == 'quit':
            return 'quit'
        print(Dataframe.loc[Dataframe[SourceName] == SourceText])
        print("Translation propagated")


# Returns either a full or partial string match
def MatchSegments(Dataframe, MatchSeries, SourceIndex, TargetIndex, MatchString, MatchType=None):
    SeriesIndexes = dict(SOURCE=SourceIndex, TARGET=TargetIndex)
    MatchSeriesIndex = SeriesIndexes[MatchSeries]
    if (MatchType in [None, 'FULL']):
        MatchDf = miniPdFuncs.GetSimpMaskDf(Dataframe, MatchSeriesIndex, MatchString)
    elif (MatchType == 'PARTIAL'):
        Series = Dataframe.columns[MatchSeriesIndex]
        MatchDf = miniPdFuncs.GetSimpMaskDf(Dataframe, "", Dataframe[Series].str.contains(MatchString))
    if MatchDf.empty:
        print("\nNo matches found")
    else:
        MatchDf.reset_index(inplace=True)
        Results = ["\nSegment {}\nTarget: {}\nSource: {}".format(MatchDf.iat[x, 0], MatchDf.iat[x, SourceIndex + 1], MatchDf.iat[x, TargetIndex + 1]) for x in range(MatchDf.shape[0])]
        print("\nResults:")
        print(*Results, sep="\n")

        print("\nPlease enter one of the following commands:")
        print("  PASS (Go back to entering translation)")
        print("  GETCONTEXT (Get more context for current matches)")

        # Processing matching options
        Option = CheckInput(input("\n").lower(),
                            Choices=['pass', 'getcontext'])
        # If PASS, then simply exit the function
        if (Option.upper() == 'PASS'):
            return
        # If GETCONTEXT, get matches with some surrounding segments
        # Program will print context matches in blocks and ask if the
        # user wants to continue printing
        elif (Option.upper() == 'GETCONTEXT'):
            GetContextSegs(Dataframe, MatchDataFrame=MatchDf)


# Returns a segment and its surrounding segments
def GetContextSegs(Dataframe, SegmentIndex=None, MatchDataFrame=None, PlusAlpha=0):
    # YesNo = ['y', 'n']
    PlusAlpha = int(PlusAlpha)
    if not MatchDataFrame.empty: # Executed if called from inside MatchSourceSeg function
        for SubSegment in MatchDataFrame['index']:

            Previous = [Dataframe.iat[SubSegment + x - 1, 1] for x in range(-2 - PlusAlpha, 0)]
            print("\nPrevious {}:".format(2 + PlusAlpha))
            print(*Previous, sep='\n')

            print("\nMatched segment:")
            print(Dataframe.iat[SubSegment - 1, 1])

            if (SubSegment < (Dataframe.shape[0] - 3)):
                Next = [Dataframe.iat[SubSegment + x - 1, 1] for x in range(1, 3 + PlusAlpha)]
                print("\nNext {}:".format(2 + PlusAlpha))
                print(*Next, sep='\n')

            if (SubSegment != MatchDataFrame.iat[-1, MatchDataFrame.columns.get_loc('index')]):
                Continue = CheckInput(input("\nView context for next match? [Y/n]\n").lower(),
                            Choices=['y', 'n'])
                # Continue = input("\nView context for next match? [Y/n]\n").lower()
                # while (Continue not in YesNo):
                #     Continue = input("Invalid input. Please input \'y\' or \'n\'\n")
                # If y, then program will print the next context match
                if Continue == 'y':
                    continue
                # If n, break out of loop and finish function
                elif Continue == 'n':
                    break
                elif Continue == 'quit':
                    break
        Continue = CheckInput(input("\n\nEnter \'OK\' to continue.\n").lower(),
                              Boolean="Input == 'ok'")
        # Continue = input("\n\nEnter \'OK\' to continue.\n").upper()
        # while (Continue != 'OK'):
        #     Continue = input("Enter \'OK\' to continue.\n").upper()
    else:  # Executed if called outside of MatchSourceSeg function
        Previous = [Dataframe.iat[SegmentIndex + x, 1] for x in range(-2 - PlusAlpha, 0)]
        print("\nPrevious {}:".format(2 + PlusAlpha))
        print(*Previous, sep='\n')

        print("\nMatched segment:")
        print(Dataframe.iat[SegmentIndex, 1])

        if (SegmentIndex < (Dataframe.shape[0] - 3)):
            Next = [Dataframe.iat[SegmentIndex + x, 1] for x in range(1, 3 + PlusAlpha)]
            print("\nNext {}:".format(2 + PlusAlpha))
            print(*Next, sep='\n')


# Allows user to retranslate a segment of their choice. If the user doesn't know
# which segment to look in, the program will step through all translated segments
def retranslateSegment(Dataframe, SourceIndex, TargetIndex, SegmentIndex):

    if (SegmentIndex == -1): # Finds list of translated segments and loops through,
                               # asking if you would like to retranslate each one
        LangList = []
        for row in range(Dataframe.shape[0]):
            try: lang = ld.detect(Dataframe.iat[row, TargetIndex])
            except: lang = None
            finally: LangList.append(lang)
        MaskedFrame = Dataframe[np.in1d(LangList, 'en')]

        for TranslatedSegment in MaskedFrame.index:
            print("\nSource:{}\nTarget:{}\n".format(Dataframe.iat[TranslatedSegment, SourceIndex], Dataframe.iat[TranslatedSegment, TargetIndex]))
            Answer = CheckInput(input("Retranslate segment? [Y/n]\n").lower(),
                                  Choices=['y', 'n'])

            if Answer == 'y':
                Target = inputTranslation()
                Dataframe.iat[TranslatedSegment, TargetIndex] = Target
            elif Answer == 'n':
                pass
            elif Answer == 'quit':
                break
    else:
        print("\nSource:{}\nTarget:{}\n".format(Dataframe.iat[SegmentIndex, SourceIndex], Dataframe.iat[SegmentIndex, TargetIndex]))
        Answer = CheckInput(input("Retranslate segment? [Y/n]\n").lower(),
                            Choices=['y', 'n'])

        if Answer == 'y':
            Target = inputTranslation()[0]
            Dataframe.iat[SegmentIndex, TargetIndex] = Target
        elif Answer == 'n':
            pass
        elif Answer == 'quit':
            pass
