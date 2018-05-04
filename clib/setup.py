from distutils.core import setup, Extension

module1 = Extension('gofeat',
                    sources=['gofeat.c'], include_dirs=['./'])

setup(name='gofeat',
      version='1.0',
      description='go features including liberty, ladder, ko, etc.',
      ext_modules=[module1])
