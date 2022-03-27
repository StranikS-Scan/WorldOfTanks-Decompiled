# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/epic_game.py


def searchRankForSlot(slotIdx, slotEventsConfig):
    for rank, updateSet in enumerate(slotEventsConfig):
        if slotIdx in updateSet:
            return rank

    return None
