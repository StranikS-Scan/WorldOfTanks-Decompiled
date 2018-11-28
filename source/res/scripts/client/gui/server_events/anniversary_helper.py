# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/anniversary_helper.py
ANNIVERSARY_EVENT_PREFIX = 'anniversary_ga'

def getEventNameByQuest(quest):
    return ANNIVERSARY_EVENT_PREFIX if quest.getID().startswith(ANNIVERSARY_EVENT_PREFIX) else None
