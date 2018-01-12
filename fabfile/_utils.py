# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys

if sys.version_info.major == 2:
    from contextlib import nested

else:
    from contextlib import ExitStack


    def nested(*context_managers):
        """Возвращает менеджер контекста с вложенными менеджерами.

        Пример использования:

        .. code-block:: python

           with nested(
               ContextManager1(),
               ContextManager1(),
               ContextManager1(),
           ):
               pass
        """
        exit_stack = ExitStack()

        for context_manager in context_managers:
            exit_stack.enter_context(context_manager)

        return exit_stack
