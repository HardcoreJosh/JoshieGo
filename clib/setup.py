from distutils.core import setup, Extension

module1 = Extension('gofeat',
                    sources=['gofeat.cpp'], include_dirs=['./'], 
                    extra_compile_args=['-std=c++11'])

setup(name='gofeat',
      version='1.0',
      description='go features including liberty, ladder, ko, etc.',
      ext_modules=[module1])
