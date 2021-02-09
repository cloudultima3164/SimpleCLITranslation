# SimpleCLITranslation
Simple CLI Tool for translation. Definitely could be improved on in several ways, but I'll do that later (don't expect this to be done - if it happens, it's a surprise)

---Simple instructions to get up and running---

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
python <path to saved location>/SimpleCLITranslation.py
```

You will be prompted to select the file you wish to translate using an open file dialog.
Once you have selected the file, the program will read it into memory, and you are good to go!
If you need help using the program, you can just type help and hit enter at any time for a description on all of the possible commands.
If you need more help, please open an issue.
