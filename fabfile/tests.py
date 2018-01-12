# coding: utf-8
# pylint: disable=not-context-manager, relative-import
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from os import remove
from os.path import exists
from os.path import isdir
from os.path import join
from shutil import rmtree

from fabric.api import local
from fabric.context_managers import lcd
from fabric.decorators import task

from ._settings import PROJECT_DIR


@task
def run():
    """Запуск тестов."""
    with lcd(PROJECT_DIR):
        local('tox')


@task
def clean():
    """Удаление файлов, созданных во время сборки дистрибутивов."""
    for path in (
        join(PROJECT_DIR, '.tox'),
        join(PROJECT_DIR, '.eggs'),
    ):
        if exists(path):
            print('REMOVE:', path)
            if isdir(path):
                rmtree(path)
            else:
                remove(path)
