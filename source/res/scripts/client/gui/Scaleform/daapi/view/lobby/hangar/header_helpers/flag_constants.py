# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/flag_constants.py
from gui.shared.system_factory import registerQuestFlag
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags import RankedQuestsFlag, MapboxQuestsFlag, ElenQuestsFlag, BattleQuestsFlag, Comp7QuestsFlag, MarathonQuestsFlag
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.personal_mission_flags import PersonalMissionsFlag

class QuestFlagTypes(object):
    PERSONAL_MISSIONS = 'personalMissions'
    BATTLE = 'battleQuests'
    COMP7 = 'comp7Quests'
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
registerQuestFlag(QuestFlagTypes.COMP7, Comp7QuestsFlag)
