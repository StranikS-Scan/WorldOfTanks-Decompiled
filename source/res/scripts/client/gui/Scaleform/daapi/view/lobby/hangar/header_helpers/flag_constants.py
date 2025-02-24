# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/flag_constants.py
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.personal_mission_flags import PersonalMissionsFlag
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags import RankedQuestsFlag, ElenQuestsFlag, BattleQuestsFlag, MarathonQuestsFlag, MapboxQuestsFlag
from gui.shared.system_factory import registerQuestFlag

class QuestFlagTypes(object):
    PERSONAL_MISSIONS = 'personalMissions'
    BATTLE = 'battleQuests'
    MAPBOX = 'mapboxQuests'
    MARATHON = 'marathonQuests'
    ELEN = 'elenQuests'
    RANKED = 'rankedQuests'


registerQuestFlag(QuestFlagTypes.PERSONAL_MISSIONS, PersonalMissionsFlag)
registerQuestFlag(QuestFlagTypes.MARATHON, MarathonQuestsFlag)
registerQuestFlag(QuestFlagTypes.ELEN, ElenQuestsFlag)
registerQuestFlag(QuestFlagTypes.BATTLE, BattleQuestsFlag)
registerQuestFlag(QuestFlagTypes.RANKED, RankedQuestsFlag)
registerQuestFlag(QuestFlagTypes.MAPBOX, MapboxQuestsFlag)
