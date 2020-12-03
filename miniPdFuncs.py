import pandas as pd
from chardet.universaldetector import UniversalDetector
from datetime import datetime
import numpy as np
import sys
import os

if not sys.warnoptions:
    import warnings
    warnings.simplefilter('error')

# This function detects file encoding (to decrease parse time)
# Encoding is req'd for passing a dataframe, is string must be
# converted to a byte string
def detectChars(File, Dataframe=False, Series=None, Encoding=None):
    detector = UniversalDetector()
    detector.reset()
    if not Dataframe:
        with open(File, 'rb') as f:
            for row in f:
                detector.feed(row)
                if detector.done: break
        detector.close()
        result = detector.result
        return result
    elif Dataframe:
        for row in File[Series]:
            byte_string = bytearray(row, Encoding)
            detector.feed(byte_string)
            if detector.done: break
        detector.close()
        result = detector.result
        return result
    return 1


# This function writes a file's contents to a dataframe
# Currently only compatible with csv, txt, and xlsx
def FileToDf(File, Encoding='utf-8', ColumnNames=None, Seperator=',', KeepHeader='infer', CMfilter=False):
    FilePath = File.split(os.extsep)
    Extension = FilePath[1]
    FilePath = FilePath[0]
    if (Extension == "csv") | (Extension.find('txt') != -1):
        df = pd.read_csv(File, encoding=Encoding, names=ColumnNames,
                         header=KeepHeader, sep=Seperator, dtype='object')
        return df, Extension
    elif (Extension == "xlsx"):
        df = pd.read_excel(File, names=ColumnNames,
                           header=KeepHeader, dtype='object')
        return df, Extension

    return 1


# Remove commas from a series of numbers
def RemSepCommas(Series):
    Commas = Series.str.contains(',', regex=False).any()
    if Commas:
        Series = Series.str.replace(',', '')
    return Series.astype('float')


# Append multiple dataframes stored in a dictionary
def ConcatDfDictionary(DfDictionary, DictLen):
    if DictLen == 1:
        df = pd.DataFrame(data=DfDictionary[0])
    elif DictLen > 1:
        df = pd.concat(DfDictionary, ignore_index=True)
        df.reset_index(drop=True, inplace=True)
    else:
        raise ValueError('Unhandled value for DictLen: {}'.format(DictLen))
    return df


# creates slices on a string for parsing dates quicker
def date_indexing(dstr):
    return datetime(*map(int, [dstr[:4], dstr[5:7], dstr[8:10],
                               dstr[11:13], dstr[14:16], dstr[17:19], dstr[20:]]))


# Converts series to datetime. Only used with raw CM logs.
def ConvertToDateTime(series):
    series = np.frompyfunc(date_indexing, 1, 1)(series)
    return series


# Filters DataFrame to specified time range
def GetTimeRange(Dataframe, Series, From, Until):
    Dataframe = Dataframe[Dataframe[Series] > From]
    Dataframe = Dataframe[Dataframe[Series] < Until]
    return Dataframe


# Filters DataFrame by specified value
def GetSimpMaskDf(Dataframe, Series, Value, ReturnCopy=False):
    if Series:
        if (type(Series) == str):
            pass
        elif (type(Series) == int):
            Series = Dataframe.columns[Series]
        Dataframe = Dataframe[np.in1d(Dataframe[Series], Value)]
    elif not Series:
        Dataframe = Dataframe[Value]
    else:
        raise ValueError('ERROR: Cannot parse arguements {}, {}, {}'.format(Dataframe, Series, Value))
    if ReturnCopy:
        DfCopy = Dataframe.copy()
        DfCopy.reset_index(inplace=True, drop=True)
        return DfCopy
    else:
        return Dataframe


# For saving a series of masked Dataframes.
# Useful when aggregating several times over the same data
def MaskedDfsToDict(Dataframe, MaskSeries, AggregateDf):
    DfDict = {k: GetSimpMaskDf(Dataframe, MaskSeries,
              AggregateDf[MaskSeries][k]) for k in range(AggregateDf.shape[0])}
    return DfDict


# Adds comma and decimal formatting to numbers
def AddCommaDot(Series):
    MapFunc = lambda x: "{0:,.2f}".format(x)
    Series = np.frompyfunc(MapFunc, 1, 1)(Series)
    return Series


# writes dataframe to a csv
# will extend to allow path input later
def DfToFile(Dataframe, Identifier, Extension=None, Folder=None):
    t0 = datetime.now()
    if (Folder == None): # If Folder argument is not passed,
                         # we assume that the Identifier contains the full path
        Filepath = Identifier
    else: # otherwise we join the Folder and Identifier arguments as a file path
        Filepath = os.path.join(Folder, Identifier)
    if (Extension == None): # If the Extension argument is not passed,
                            # we assume that it is contained in the Identifier
                            # argument in the second indice
        Extension = Identifier.split(os.extsep)[1]
        # We need to attempt to test if we can save first, so we pass the actual
        # save argument to another function as a string
        if (Extension == "csv"):
            Function = "Dataframe.to_csv(Filepath, header=True, index=False)"
            TryResult = TrySave(Dataframe, Filepath, Function)
        elif (Extension == "xlsx"):
            Function = "Dataframe.to_excel(Filepath, header=True, index=False)"
            TryResult = TrySave(Dataframe, Filepath, Function)
    else:
        if (Extension == "csv"):
            Function = "Dataframe.to_csv(Filepath, header=True, index=False)"
            TryResult = TrySave(Dataframe, Filepath, Function)
        elif (Extension == "xlsx"):
            Function = "Dataframe.to_excel(Filepath, header=True, index=False)"
            TryResult = TrySave(Dataframe, Filepath, Function)
    if (TryResult == 1):
        print('\nExported to:\n')
        print('{}\n'.format(Filepath))
    elif (TryResult == 2):
        print("\nSave operation cancelled.\n")


# Attempts to write a dataframe to a file. If the file is already in use, the
# program will ask you to close the other program before attempting to save again
def TrySave(Dataframe, Filepath, Function):
    TryResult = 0
    try: fopen = open(Filepath, 'r+')
    except:
        print("File is open in another application.")
        while (TryResult == 0):
            TryAgain = input('Please enter OK to try again or CANCEL to cancel save operation.\n').upper()
            if (TryAgain == 'OK'):
                try: fopen = open(Filepath, 'r+')
                except: print("Error unresolved.")
                else: TryResult = 1
            if (TryAgain == "CANCEL"):
                TryResult = 2
    else: TryResult = 1
    finally:
        if (TryResult == 1):
            fopen.close()
            eval(Function)
        elif (TryResult == 2):
            pass
        return TryResult

