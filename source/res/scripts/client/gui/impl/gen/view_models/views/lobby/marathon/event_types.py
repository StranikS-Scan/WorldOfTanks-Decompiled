# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/event_types.py
from frameworks.wulf import ViewModel

class EventTypes(ViewModel):
    __slots__ = ()
    BATTLE_QUEST = 'battleQuest'
    RESEARCH_VEHICLE = 'researchVehicle'
    RESEARCH_MODULE = 'researchModule'
    CREW_MEMBER_NEW_SKILL = 'crewMemberNewSkill'
    PERSONAL_MISSION = 'personalQuest'
    DAILY_QUEST = 'dailyQuest'
    RANKED_BATTLES = 'rankedBattles'
    BATTLE_PASS = 'battlePass'

    def __init__(self, properties=0, commands=0):
        super(EventTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(EventTypes, self)._initialize()
