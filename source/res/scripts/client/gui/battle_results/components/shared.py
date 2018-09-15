# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/shared.py
"""
Module contains components that are included in different blocks.
"""
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_ERROR
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, MARK_ON_GUN_RECORD, MARK_OF_MASTERY_RECORD
from gui.battle_results import stored_sorting
from gui.battle_results.components import base
from gui.shared.gui_items.dossier.achievements import MarkOnGunAchievement
_FALLOUT_SORTING_CRITERIA = 'victoryScore'
_FALLOUT_SORTING_DIRECTION = 'descending'

class TrueFlag(base.StatsItem):

    def _convert(self, value, reusable):
        return True


class FalseFlag(base.StatsItem):

    def _convert(self, value, reusable):
        return False


class ClientIndexItem(base.StatsItem):

    def _convert(self, value, reusable):
        return reusable.clientIndex


class PlayerNameBlock(base.StatsBlock):
    __slots__ = ('__dbID', 'nameLabel', 'fullNameLabel', 'clanLabel', 'regionLabel')

    def __init__(self, meta=None, field='', *path):
        super(PlayerNameBlock, self).__init__(meta, field, *path)
        self.__dbID = 0

    def setAccountDBID(self, dbID):
        self.__dbID = dbID

    def setPlayerInfo(self, playerInfo):
        self.__dbID = playerInfo.dbID
        self.nameLabel = playerInfo.name
        self.fullNameLabel = playerInfo.getFullName()
        self.clanLabel = playerInfo.clanAbbrev
        self.regionLabel = playerInfo.getRegionCode()

    def setRecord(self, result, reusable):
        if reusable is not None:
            self.setPlayerInfo(reusable.getPlayerInfo(self.__dbID))
        else:
            LOG_ERROR('Player is not found', result, reusable)
        return


class WasInBattleItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return reusable.wasInBattle()


class SortingBlock(base.StatsBlock):
    __slots__ = ('__setting', 'criteria', 'direction')

    def __init__(self, setting, meta=None, field='', *path):
        super(SortingBlock, self).__init__(meta, field, *path)
        self.criteria = None
        self.direction = None
        self.__setting = setting
        return

    @property
    def settingKey(self):
        return self.__setting

    def getVO(self):
        self.criteria, self.direction = stored_sorting.readStatsSorting(self.__setting)
        return super(SortingBlock, self).getVO()

    def setRecord(self, result, reusable):
        pass


class RegularSortingBlock(SortingBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(RegularSortingBlock, self).__init__(stored_sorting.STATS_REGULAR_SORTING, meta, field, *path)


class SortieSortingBlock(SortingBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(SortieSortingBlock, self).__init__(stored_sorting.STATS_SORTIE_SORTING, meta, field, *path)


class FalloutSortingBlock(SortingBlock):
    __slots__ = ('criteria', 'direction')

    def __init__(self, meta=None, field='', *path):
        super(FalloutSortingBlock, self).__init__('', meta, field, *path)
        self.criteria = _FALLOUT_SORTING_CRITERIA
        self.direction = _FALLOUT_SORTING_DIRECTION


class AchievementIcon(base.StatsBlock):
    __slots__ = ('big', 'small')

    def __init__(self, meta=None, field='', *path):
        super(AchievementIcon, self).__init__(meta, field, *path)
        self.small = ''
        self.big = ''

    def setRecord(self, result, reusable):
        self.small = result


class AchievementBlock(base.StatsBlock):
    __slots__ = ('type', 'block', 'icon', 'specialIcon', 'title', 'description', 'hasRibbon', 'customData', 'isUnique', 'rank', 'i18nValue', 'inactive', 'isRare', 'rareIconID', 'arenaType', 'vehicleLevel')

    def setUnique(self, value):
        self.isUnique = value

    def setRecord(self, result, reusable):
        if result.getType() != ACHIEVEMENT_TYPE.SERIES:
            self.rank = result.getValue()
            self.i18nValue = result.getI18nValue()
        icons = result.getIcons()
        specialIcon = icons.get(MarkOnGunAchievement.IT_95X85, None)
        customData = []
        recordName = result.getRecordName()
        if recordName == MARK_ON_GUN_RECORD:
            customData.extend([result.getDamageRating(), result.getVehicleNationID()])
        if recordName == MARK_OF_MASTERY_RECORD:
            customData.extend([result.getPrevMarkOfMastery(), result.getCompDescr()])
        self.type = recordName[1]
        self.block = result.getBlock()
        self.icon = result.getSmallIcon() if specialIcon is None else ''
        self.specialIcon = specialIcon
        self.title = result.getUserName()
        self.description = result.getUserDescription()
        self.hasRibbon = result.hasRibbon()
        self.customData = customData
        if reusable:
            self.arenaType = reusable.common.arenaBonusType
            playerVehiclesIterator = reusable.personal.getVehicleItemsIterator()
            for _, vehicle in playerVehiclesIterator:
                self.vehicleLevel = vehicle.level
                break

        return


class AchievementsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, record, reusable):
        for achievement, isUnique in record:
            component = AchievementBlock()
            component.setUnique(isUnique)
            component.setRecord(achievement, reusable)
            self.addComponent(self.getNextComponentIndex(), component)


class BiDiStatsBlock(base.StatsBlock):
    __slots__ = ()

    @property
    def left(self):
        component = self.getComponent(0)
        assert component is not None, 'Block is not configured, component must be added to index 0.'
        return component

    @property
    def right(self):
        component = self.getComponent(1)
        assert component is not None, 'Block is not configured, component must be added to index 1.'
        return component
