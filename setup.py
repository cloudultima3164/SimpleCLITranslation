from setuptools import setup

setup(name=SimpleCLITranslation,
      version=1.0,
      description='Easy CLI translator. Not very robust.',
      url='https://github.com/cloudultima3164/SimpleCLITranslation',
      author='CloudUltima3164',
      install_requires=[
          'pandas',
          'langdetect',
          'chardet']
      )
