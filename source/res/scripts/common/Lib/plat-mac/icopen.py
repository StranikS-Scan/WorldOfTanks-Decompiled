# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/icopen.py
from warnings import warnpy3k
warnpy3k('In 3.x, the icopen module is removed.', stacklevel=2)
import __builtin__
_builtin_open = globals().get('_builtin_open', __builtin__.open)

def _open_with_typer(*args):
    file = _builtin_open(*args)
    filename = args[0]
    mode = 'r'
    if args[1:]:
        mode = args[1]
    if mode[0] == 'w':
        from ic import error, settypecreator
        try:
            settypecreator(filename)
        except error:
            pass

    return file


__builtin__.open = _open_with_typer
