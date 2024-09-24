# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/wrappers/function_helpers.py
from functools import wraps

def replaceNoneKwargsModel(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        actual = kwargs['model'] if 'model' in kwargs else None
        if actual is None:
            with self.getViewModel().transaction() as model:
                kwargs['model'] = model
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
        return

    return wrapper
