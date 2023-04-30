# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/quests_packer.py
import constants
from gui.server_events.events_helpers import isPremium, isDailyQuest
from gui.shared.missions.packers.events import TokenUIDataPacker, PrivateMissionUIDataPacker, DailyQuestUIDataPacker

def getEventUIDataPacker(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return TokenUIDataPacker(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return PrivateMissionUIDataPacker(event)
    else:
        return DailyQuestUIDataPacker(event) if isPremium(event.getID()) or isDailyQuest(event.getID()) or event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None
