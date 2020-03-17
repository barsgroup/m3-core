# coding: utf-8
from __future__ import absolute_import
import os
from setuptools import setup, find_packages


def _read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__),
            fname)).read()
    except IOError:
        return ''


setup(
    name='m3-core',
    url='https://github.com/barsgroup/m3-core',
    license='MIT',
    author='BARS Group',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description=_read('DESCRIPTION.md'),
    description_content_type='text/markdown',
    install_requires=(
        'm3-builder>=1.2.0',
        'm3-django-compat>=1.5.1',
    ),
    long_description=_read('README.md'),
    long_description_content_type='text/markdown',
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
    setup_requires=(
        'm3-builder>=1.2.0',
    ),
    set_build_info=os.path.dirname(__file__),
)
