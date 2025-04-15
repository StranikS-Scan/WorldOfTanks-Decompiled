# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/DevHotkeysController.py
import Keys
import os
import subprocess

def handleKeyEvent(event):
    if event.isShiftDown() and event.isCtrlDown() and event.isAltDown() and event.isKeyDown() and not event.isRepeatedEvent():
        if event.key == Keys.KEY_P:
            subprocess.Popen([os.getcwd() + './../tools/PixelsHunter/PixelsHunter.exe', str(os.getpid())])
            __runSizeManager()
        elif event.key == Keys.KEY_S:
            __runSizeManager()


def __runSizeManager():
    from development.as_tools.change_window_size_manager import g_change_manager as m
    m.start()
