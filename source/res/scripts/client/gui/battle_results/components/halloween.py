# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/halloween.py
from helpers import dependency
from helpers import i18n
from gui.battle_results.reusable import sort_keys
from gui.battle_results.components import base
from gui.battle_results.components import vehicles
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.EVENT import EVENT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.utils.functions import makeTooltip
from skeletons.gui.halloween_controller import IHalloweenController

def _getBonusValueByName(item, bonusName):
    bonuses = item.getBonuses()
    for bonus in bonuses:
        if bonusName == bonus.getName():
            return bonus.getValue()


class _HalloweenItem(base.StatsItem):
    __slots__ = ()
    halloweenController = dependency.descriptor(IHalloweenController)


class _RewardStatsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        result = {'label': self._getLabel(value, reusable),
         'exp1Data': {'value': self._getXpData(value, reusable),
                      'icon': 'xp1'}}
        exp2Value = self._getFreeXpData(value, reusable)
        if exp2Value is not None:
            result['exp2Data'] = {'value': exp2Value,
             'icon': 'xp2'}
        tooltip = self._getTooltip(reusable)
        if tooltip is not None:
            result['tooltip'] = tooltip
        return result

    @classmethod
    def _getLabel(cls, value, reusable):
        pass

    @classmethod
    def _getXpData(cls, value, reusable):
        raise NotImplementedError

    @classmethod
    def _getFreeXpData(cls, value, reusable):
        raise NotImplementedError

    @classmethod
    def _getTooltip(cls, reusable):
        return None

    @staticmethod
    def _getBaseOriginalXp(reusable):
        return reusable.personal.getBaseXPRecords().getRecord('originalXP')

    @staticmethod
    def _getFreeOriginalXp(reusable):
        return reusable.personal.getBaseFreeXPRecords().getRecord('originalFreeXP')

    @staticmethod
    def _getBaseXp(reusable):
        return reusable.personal.getBaseXPRecords().getRecord('xp')

    @staticmethod
    def _getFreeXp(reusable):
        return reusable.personal.getBaseFreeXPRecords().getRecord('freeXP')

    @staticmethod
    def _getEventXp(reusable):
        return reusable.personal.getBaseXPRecords().findRecord('eventXPFactor100List_')

    @staticmethod
    def _getEventFreeXp(reusable):
        return reusable.personal.getBaseFreeXPRecords().findRecord('eventFreeXPFactor100List_')

    @staticmethod
    def _getPremiumXp(reusable):
        return reusable.personal.getPremiumXPRecords().getRecord('xp')

    @staticmethod
    def _getPremiumFreeXp(reusable):
        return reusable.personal.getPremiumFreeXPRecords().getRecord('freeXP')


class UserNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        playerInfo = reusable.getPlayerInfo()
        return playerInfo.name


class Exp1Tooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        title = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_EXP1_TITLE)
        desc = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_EXP1_DESC)
        return makeTooltip(title, desc)


class Exp2Tooltip(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        title = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_EXP2_TITLE)
        desc = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_EXP2_DESC)
        return makeTooltip(title, desc)


class SoulsItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        info = reusable.getPersonalVehiclesInfo(value)
        return info.eventPoints


class IsCompletedFlag(_HalloweenItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        info = reusable.getPersonalVehiclesInfo(value)
        return self.halloweenController.getProgress().getMaxLevel() == info.halloweenLevel


class HalloweenVehicleStatsBlock(vehicles.RegularVehicleStatsBlock):
    __slots__ = ('level', 'souls', 'status')

    def _setTotalStats(self, result, noPenalties):
        super(HalloweenVehicleStatsBlock, self)._setTotalStats(result, noPenalties)
        self.status = ''
        penaltyName = result.avatar.getPenaltyName()
        if not noPenalties and penaltyName:
            self.status = i18n.makeString({'event_afk': EVENT.BATTLE_RESULT_HASPENALTY_AFK,
             'event_deserter': EVENT.BATTLE_RESULT_HASPENALTY_DESERTER}[penaltyName])

    def setRecord(self, result, reusable):
        super(HalloweenVehicleStatsBlock, self).setRecord(result, reusable)
        self.level = result.halloweenLevel
        self.souls = result.eventPoints


class HalloweenBattlesTeamStatsBlock(vehicles.TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(HalloweenBattlesTeamStatsBlock, self).__init__(HalloweenVehicleStatsBlock, meta, field, *path)

    def setRecord(self, result, reusable):
        personalInfo = reusable.getPlayerInfo()
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sortKey=lambda info: sort_keys.PersonalFirstTeamItemSortKey(info, personalInfo.dbID))
        super(HalloweenBattlesTeamStatsBlock, self).setRecord(allies, reusable)


class OriginalRewardStats(_RewardStatsItem):
    __slots__ = ()

    @classmethod
    def _getLabel(cls, value, reusable):
        info = reusable.getPersonalVehiclesInfo(value)
        return str(info.eventPoints)

    @classmethod
    def _getXpData(cls, value, reusable):
        return cls._getBaseXp(reusable) - cls._getEventXp(reusable)

    @classmethod
    def _getFreeXpData(cls, value, reusable):
        return cls._getFreeXp(reusable) - cls._getEventFreeXp(reusable)


class LevelRewardStats(_RewardStatsItem):
    __slots__ = ()

    @classmethod
    def _getLabel(cls, value, reusable):
        info = reusable.getPersonalVehiclesInfo(value)
        return str(info.halloweenLevel)

    @classmethod
    def _getXpData(cls, value, reusable):
        return cls._getEventXp(reusable)

    @classmethod
    def _getFreeXpData(cls, value, reusable):
        return cls._getEventFreeXp(reusable)


class PremiumRewardStats(_RewardStatsItem):
    __slots__ = ()

    @classmethod
    def _getXpData(cls, value, reusable):
        return cls._getPremiumXp(reusable) - cls._getBaseXp(reusable)

    @classmethod
    def _getFreeXpData(cls, value, reusable):
        return cls._getPremiumFreeXp(reusable) - cls._getFreeXp(reusable)


class WithPremiumRewardStats(_RewardStatsItem):
    __slots__ = ()

    @classmethod
    def _getXpData(cls, value, reusable):
        return cls._getPremiumXp(reusable) - cls._getBaseXp(reusable)

    @classmethod
    def _getFreeXpData(cls, value, reusable):
        return cls._getPremiumFreeXp(reusable) - cls._getFreeXp(reusable)

    @classmethod
    def _getTooltip(cls, reusable):
        title = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_PREMIUMACCOUNT_TITLE)
        description = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_PREMIUMACCOUNT_DESC)
        return makeTooltip(title, description)


class WithMaxSoulsRewardStats(_RewardStatsItem):
    __slots__ = ()
    halloweenController = dependency.descriptor(IHalloweenController)

    @classmethod
    def _getLabel(cls, value, reusable):
        return str(cls.halloweenController.getProgress().getMaxLevel())

    @classmethod
    def _getXpData(cls, value, reusable):
        progressItem = cls.halloweenController.getProgress().getMaxProgressItem()
        itemBonus = _getBonusValueByName(progressItem, 'xpFactorHE')
        return cls._getBaseOriginalXp(reusable) * (itemBonus - 1)

    @classmethod
    def _getFreeXpData(cls, value, reusable):
        progressItem = cls.halloweenController.getProgress().getMaxProgressItem()
        itemBonus = _getBonusValueByName(progressItem, 'freeXPFactorHE')
        return cls._getFreeOriginalXp(reusable) * (itemBonus - 1)

    @classmethod
    def _getTooltip(cls, reusable):
        title = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_MAXLEVEL_TITLE)
        description = i18n.makeString(TOOLTIPS.HALLOWEEN_VICTORYSCREEN_MAXLEVEL_DESC)
        return makeTooltip(title, description)


class ProgressItemStatsBlock(base.StatsBlock):
    __slots__ = ('index', 'unlocked', 'value', 'tooltip', 'specialAlias', 'specialArgs', 'isSpecial', 'bonus', 'statusDescription')


class ProgressStatsBlock(base.StatsBlock):
    __slots__ = ()
    halloweenController = dependency.descriptor(IHalloweenController)

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        maxSouls = 0
        for index, item in enumerate(self.halloweenController.getProgress().items):
            block = ProgressItemStatsBlock()
            maxSouls += item.getMaxProgress()
            level = item.getLevel()
            block.index = level
            block.unlocked = index <= info.halloweenLevelMax
            block.value = maxSouls
            block.specialAlias = TOOLTIPS_CONSTANTS.HALLOWEEN_PROGRESS_TOOLTIP
            block.specialArgs = (level, info.halloweenLevel, info.halloweenLevelMax)
            block.isSpecial = None
            block.bonus = item.getGUIBonusData().get('bonus')
            block.statusDescription = item.getStatusDescription()
            self.addComponent(self.getNextComponentIndex(), block)

        return


class ProgressValueBlock(_HalloweenItem):

    def _convert(self, value, reusable):
        halloweenProgress = self.halloweenController.getProgress()
        info = reusable.getPersonalVehiclesInfo(value)
        halloweenLevel = info.halloweenLevelOnStart
        eventPointsOnStart = info.eventPointsOnStart
        eventPoints = info.eventPoints
        startPoints = eventPointsOnStart
        maxPoints = 0
        for index, item in enumerate(halloweenProgress.items):
            if index <= halloweenLevel:
                startPoints += item.getMaxProgress()
            if index <= info.halloweenLevelMax:
                maxPoints += item.getMaxProgress()

        startPoints = min(startPoints, maxPoints)
        endPoints = min(startPoints + eventPoints, maxPoints)
        startPoints = startPoints if startPoints != endPoints else -1
        return (endPoints, startPoints)
