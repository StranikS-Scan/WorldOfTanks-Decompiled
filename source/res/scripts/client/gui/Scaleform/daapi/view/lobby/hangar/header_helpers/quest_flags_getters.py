# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/header_helpers/quest_flags_getters.py
import typing
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_constants import QuestFlagTypes
from gui.shared.system_factory import collectQuestFlags
from shared_utils import findFirst
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.base_flags import IQuestsFlag
    from gui.shared.gui_items.Vehicle import Vehicle

class IQuestFlagsGetter(object):

    @classmethod
    def getVO(cls, vehicle, params=None):
        raise NotImplementedError

    @classmethod
    def showQuestsInfo(cls, questType, questID):
        raise NotImplementedError


class BaseQuestFlagsGetter(IQuestFlagsGetter):
    _SUPPORTED_FLAGS = ()
    _ALL_QUEST_FLAGS = None

    @classmethod
    def getVO(cls, vehicle, params=None):
        if not cls._isQuestFlagsVisible():
            return []
        else:
            quests = []
            allQuestFlags = cls.__getAllQuestFlags()
            for flagType in cls._SUPPORTED_FLAGS:
                questFlag = allQuestFlags.get(flagType)
                if questFlag is None:
                    continue
                flagParams = params.get(flagType, {}) if params is not None else {}
                vo = questFlag.formatQuests(vehicle, flagParams)
                if vo:
                    if flagParams.get('isGrouped', True):
                        quests.append(vo)
                    else:
                        quests.extend(vo)

            return quests

    @classmethod
    def showQuestsInfo(cls, questType, questID):
        allQuestFlags = cls.__getAllQuestFlags()
        questFlag = findFirst(lambda p: p.isFlagSuitable(questType), allQuestFlags.values())
        if questFlag is not None:
            questFlag.showQuestsInfo(questType, questID)
        return

    @classmethod
    def _isQuestFlagsVisible(cls):
        return True

    @classmethod
    def __getAllQuestFlags(cls):
        if cls._ALL_QUEST_FLAGS is None:
            cls._ALL_QUEST_FLAGS = collectQuestFlags()
        return cls._ALL_QUEST_FLAGS


class DefaultQuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.PERSONAL_MISSIONS,
     QuestFlagTypes.BATTLE,
     QuestFlagTypes.MARATHON,
     QuestFlagTypes.ELEN)


class RankedQuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.RANKED,)


class MapboxQuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.BATTLE,
     QuestFlagTypes.MAPBOX,
     QuestFlagTypes.MARATHON,
     QuestFlagTypes.ELEN)


class Comp7QuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.COMP7, QuestFlagTypes.MARATHON)


class Comp7TournamentQuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.PERSONAL_MISSIONS,
     QuestFlagTypes.BATTLE,
     QuestFlagTypes.MARATHON,
     QuestFlagTypes.ELEN)
