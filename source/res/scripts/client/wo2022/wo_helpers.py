# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/wo2022/wo_helpers.py
from gui.impl import backport
from gui.impl.gen import R

def getEventName():
    return backport.text(R.strings.wo2022.eventName())


def getTimeLeftString(timeLeft):
    return backport.getTillTimeStringByRClass(timeLeft, R.strings.menu.Time.timeLeftShort, isRoundUp=True)
