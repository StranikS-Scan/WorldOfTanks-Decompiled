# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/quests_helpers.py


def filterCompletedProgressionQuests(quests, maxLength):
    if len(quests) > maxLength:
        quests = [ quest for quest in quests if ':progression:' not in quest.getID() ]
    return quests
