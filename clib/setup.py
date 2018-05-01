from distutils.core import setup, Extension

module1 = Extension('gofeat',
                    sources=['gofeat.c'])

setup(name='gofeat',
      version='1.0',
      description='This is a demo package',
      ext_modules=[module1])
