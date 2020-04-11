# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe
import sys
from cx_Freeze import setup, Executable

executables = [Executable("main.py", base='Win32GUI', icon=None)]

build_exe_options = {"packages": ["qdarkstyle", "matplotlib", "numpy", "os", "math", "datetime",
                                  "xlsxwriter", "openpyxl", "docx", "collections", "sqlite3", "sys", "tabulate", "lxml"],
                     "include_files": ["UI", "resources", "GRAPHICS", "DOCS", "icon"]}

setup(
    name="PDF",
    version="1.0",
    description="Formulario a PDF",
    options={"build_exe": build_exe_options},
    executables=executables
)

# python setup.py build

# setup(name='APP',
#       version='1.0',
#       description='Software para el trabajo con niños que presentan autismo',
#       author='Solangel Ubieta Rodriguez',
#       author_email='solubieta93@gmail.com',
#       scripts=['__init__.py'],
#       console=['__init__.py'],
#       options={"py2exe": {"bundle_files": 1}},
#       zipfile=None,
# )

      # classifiers=[
      #     "Environment :: Console",
      #     "Intended Audience :: Developers",
      #     "Intended Audience :: Education",
      #     "Operating System :: OS Independent",
      #     "Programming Language :: Python",
      #     "Topic :: Education",
      #     "Programming Language :: Python :: 2.6",
      #     "Programming Language :: Python :: 2.7"]
      # )

      # pyinstaller --onefile 'nombrescript.py'