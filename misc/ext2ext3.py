#!/usr/bin/env python
#coding:utf-8
from __future__ import absolute_import
from __future__ import print_function
import os, sys
import glob

if __name__ == "__main__":
    reg_Ext = r"(?<=\b)Ext(?=\b)" # для неймспейсов Ext
    reg_x = r"(?<=\b)x-(?=\b)" # для классов и селекторов x-
    reg_ext = r"(?<=\b)ext-(?=\b)" # для классов и селекторов ext-
    import re
    if len(sys.argv) != 3:
        print(u'usage: ext2ext3.py path_to_js_css wildcard')
        sys.exit()
    dir = sys.argv[1]
    for (path, dirs, files) in os.walk(dir):
        for input_file in glob.glob1(path, sys.argv[2]):
            input_file = os.path.join(os.path.abspath(path), input_file)
            fileName, fileExtension = os.path.splitext(input_file)
            output_file = '%s%s' % (fileName, fileExtension)
            data = open(input_file).read()
            data1,n1 = re.subn(reg_Ext, r'Ext3', data)
            data2,n2 = re.subn(reg_x, r'x3-', data1)
            data3,n3 = re.subn(reg_ext, r'ext3-', data2)
            if n1+n2+n3 > 0:
                print('modify file',input_file,' %s (Ext3), %s (x3), %s (ext3)' % (n1,n2,n3))
                os.rename(input_file, '%s%s-old' % (fileName, fileExtension))
                o = open(output_file,"w")
                o.write(data3)
                o.close()
