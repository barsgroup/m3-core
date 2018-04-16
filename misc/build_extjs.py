# coding:utf-8

from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import codecs
import subprocess

PROJECT_PATH = os.path.abspath(__file__)
M3_PROJECT_PATH = os.path.dirname(os.path.dirname(PROJECT_PATH))
LIVEGRID_PATH = os.path.join(M3_PROJECT_PATH, 'src', 'm3', 'static', 'vendor', 'extjs')

LIVEGRID_DEBUG_FILE = 'ext-all-debug.js'
LIVEGRID_OUT_FILE = 'ext-all.js'

def compile_production(src_file, output_file):
    '''
    Компиляция google closure
    '''
    command = 'java -jar compiler.jar --compilation_level WHITESPACE_ONLY --js %s --js_output_file %s' % \
        (src_file, output_file)
    popen = subprocess.Popen(
        command,
        shell = True,
    )
    popen.wait()

def main():
    '''
    Основная функция
    '''
    src_file = os.path.join(LIVEGRID_PATH, LIVEGRID_DEBUG_FILE)
    output_file = os.path.join(LIVEGRID_PATH, LIVEGRID_OUT_FILE)
    compile_production(src_file, output_file)

if __name__ == '__main__':
    
    print("Compile extjs-all-debug.js to extjs-all.js")
    main()
    print("It's a Good job")
