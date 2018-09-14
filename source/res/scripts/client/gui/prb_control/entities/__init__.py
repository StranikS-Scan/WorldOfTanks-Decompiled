# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/__init__.py
from constants import IS_DEVELOPMENT
__all__ = ('initDevFunctional', 'finiDevFunctional')

def initDevFunctional():
    if IS_DEVELOPMENT:
        try:
            from gui.development.dev_prebattle import init
        except ImportError:

            def init():
                pass

        init()


def finiDevFunctional():
    if IS_DEVELOPMENT:
        try:
            from gui.development.dev_prebattle import fini
        except ImportError:

            def fini():
                pass

        fini()
