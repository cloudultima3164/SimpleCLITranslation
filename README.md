# SimpleCLITranslation
Simple CLI Tool for translation. Definitely could be improved on in several ways, but I'll do that later (don't expect this to be done - if it happens, it's a surprise). Note that this tool is currently only compatible with Windows.

---Using the tool---

I highly recommend downloading the compiled binary in the `SimpleCliTranslation > dist` folder, as it won't require setting up a Python interpreter.

There are two sets of commands that can be used with the tool. The first set can be used directly from the command line to provide various information about a file. You can display this message on your command line interface at any time by executing `<insert path to SimpleTranslation.exe> -h`

```shell
usage: SimpleTranslation.exe [-h] [-o {,length,find,pos_at_length}] [-a ARGUMENT]

optional arguments:
  -h, --help            show this help message and exit
  -o {,length,find,pos_at_length}, --Option {,length,find,pos_at_length}
                        Options to change program output.
                            'length': return length of source without opening file
                            'find': returns segments that contain specified string
                                use the --argument option to specify the search string.
                            'pos_at_length': returns the segment at which the Nth character is found 
                                use the --argument option to specify N.
  -a ARGUMENT, --Argument ARGUMENT
                        Argument used in conjunction with the 'pos_at_length' and 'find' options.
```

Please note that once you have actually opened the program and are translated, any commands (aka anything you don't intend to be a translation) are prefixed with a hyphen. You can get help at any time during usage of the program by executing `-help`, which will display the following message:

```shell
Options:
 -HELP:        Display this message
 -NEXT:        Skip the current segment
 -PREVIOUS:    Return to the previous segment
 -GOTO:        Go to the specified segment number
             - Syntax is '-GOTO X', with X being the desired segment
 -MATCH:       Returns exact matches for the current segment in source segments.
             - -MATCH can be called with options PARTIAL and FULL, and SOURCE and TARGET
             - PARTIAL matches a user-defined string, FULL matches default string and is default behavior
             - SOURCE looks for a match in the source segments, TARGET looks for a match in the target segments
             - -CONTEXT (or PASS to skip -CONTEXT) can be called within the Match function
 -PROP:        Propagates a new or exisiting translation to all matching target segments.
 -CONTEXT:     Returns the the current segment, and the surrounding 2 segments
             - Syntax is 'getcontext X' (X must be an integer), returns 2 + X surrounding segments
             - The program will return 2 segments on either side if only 'getcontext' is entered.
             - If called from within the -MATCH function, program will step through context for each match.
 -RETRANSLATE: Retranslate a previous translated target segment. If you do not know the segment number,
               enter 0. The program will step through each translated segment until you quit.
 -SAVE:        Save current translation progress.
 -CLOSE:       Close the program without saving.
```

---Simple instructions to get up and running with an interpreter---

If you insist on setting up an interepreter, you can follow the steps below. This will allow you to use the .py file, which can you edit as you wish.

Note: after each installation step, you must exit and reopen your command line interpreter for changes to take effect.
At any point, if you cannot properly execute a command, first make sure that you have a folder corresponding to the installed tool on your PATH environment variable.

:: Install Pyenv
  - Linux or Mac: https://github.com/pyenv/pyenv
  - Windows: https://github.com/pyenv-win/pyenv-win
 
:: Install Python with the following command on your command line interpreter

```shell
pyenv install 3.8.6
```

:: Set default Python version

```shell
pyenv global 3.8.6
```

:: Check that Python installation was successful

```shell
python -V
```

If you get anything other than `Python 3.8.6`, then either the installation was not completed properly or `<path to home folder>/.pyenv/shims` and `<path to home folder>/.pyenv/bin` are not in your PATH environment variable

::  Download pip with the following command

```shell
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```

:: Install pip with the following command (be sure to execute the command from the directory where `get-pip.py` was downloaded to)

```shell
python get-pip.py
```

:: Upgrade pip to the latest release using the following command (You do not need to restart shell after this step or the next)

```shell
python -m pip install -U pip
```

:: Install the translation program's dependencies using pip

```shell
python -m pip install pandas
python -m pip install chardet
```

:: Download the translation tool directly from this page, and run it using the following command

```shell
python <path to saved location>/SimpleTranslation.py
```

You will be prompted to select the file you wish to translate using an open file dialog.
Once you have selected the file, the program will read it into memory, and you are good to go!
If you need help understanding how the command line arguments work, run the script with option `-h`.
If you need help using the program, you can just type `help` and hit enter at any time during program execution
for a description on all of the possible commands.

If you need more help, please open an issue.
