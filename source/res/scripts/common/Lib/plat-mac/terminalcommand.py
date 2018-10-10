# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/terminalcommand.py
from warnings import warnpy3k
warnpy3k('In 3.x, the terminalcommand module is removed.', stacklevel=2)
import time
import os
from Carbon import AE
from Carbon.AppleEvents import *
TERMINAL_SIG = 'trmx'
START_TERMINAL = '/usr/bin/open /Applications/Utilities/Terminal.app'
SEND_MODE = kAENoReply

def run(command):
    termAddress = AE.AECreateDesc(typeApplicationBundleID, 'com.apple.Terminal')
    theEvent = AE.AECreateAppleEvent(kAECoreSuite, kAEDoScript, termAddress, kAutoGenerateReturnID, kAnyTransactionID)
    commandDesc = AE.AECreateDesc(typeChar, command)
    theEvent.AEPutParamDesc(kAECommandClass, commandDesc)
    try:
        theEvent.AESend(SEND_MODE, kAENormalPriority, kAEDefaultTimeout)
    except AE.Error as why:
        if why[0] != -600:
            raise
        os.system(START_TERMINAL)
        time.sleep(1)
        theEvent.AESend(SEND_MODE, kAENormalPriority, kAEDefaultTimeout)


if __name__ == '__main__':
    run('ls -l')
