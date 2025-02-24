# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/quest_flags_getters.py
from comp7.gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_constants import QuestFlagTypes
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import BaseQuestFlagsGetter

class Comp7QuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.COMP7, QuestFlagTypes.MARATHON)


class Comp7TournamentQuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.PERSONAL_MISSIONS,
     QuestFlagTypes.BATTLE,
     QuestFlagTypes.MARATHON,
     QuestFlagTypes.ELEN)
