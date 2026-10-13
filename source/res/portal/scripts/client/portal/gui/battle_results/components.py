# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_results/components.py
from debug_utils import LOG_ERROR
from gui.battle_results.components import base
from gui.impl.gen import R

class StatsItemType(object):
    PLACE = 'place'
    KILLS = 'kills'
    DAMAGE_DEAL = 'damageDealt'
    DAMAGE_BLOCK = 'damageBlockedByArmor'


ITEMS_ORDER = [StatsItemType.PLACE,
 StatsItemType.KILLS,
 StatsItemType.DAMAGE_DEAL,
 StatsItemType.DAMAGE_BLOCK]

class ProgressionTokensItem(base.StatsItem):

    def _convert(self, result, reusable):
        return result['avatar']['progressionTokens']


class VehicleExperienceItem(base.StatsItem):

    def _convert(self, result, reusable):
        return result['avatar']['vehicleExperience']


class BattleLevelItem(base.StatsItem):

    def _convert(self, result, reusable):
        return result['avatar']['portalBattleLevel']


class WaveCountItem(base.StatsItem):

    def _convert(self, result, reusable):
        return result['avatar']['wavesCount']


class CurrentWaveItem(base.StatsItem):

    def _convert(self, result, reusable):
        return result['avatar']['currentWave']


class StatsItemBlock(base.StatsBlock):
    __slots__ = ('type', 'value', 'wreathImage')
    _ICON_PATH = R.images.portal.gui.maps.icons.battle_result
    _DEFAULT_ICON = _ICON_PATH.wreath_transparent
    _PLACE_TO_WREATH = {1: _ICON_PATH.wreath_gold(),
     2: _ICON_PATH.wreath_silver(),
     3: _ICON_PATH.wreath_bronze()}

    def __init__(self, itemType, meta=None, field='', *path):
        super(StatsItemBlock, self).__init__(meta, field, *path)
        self.type = itemType
        self.value = 0
        self.wreathImage = R.invalid()

    def setRecord(self, result, reusable):
        self.value = self._getValue(result, reusable)
        self.wreathImage = self._getWreathImage(result, reusable)

    def _getValue(self, result, reusable):
        pass

    def _getWreathImage(self, result, reusable):
        return self._DEFAULT_ICON()


class PlaceParameter(StatsItemBlock):
    __slots__ = ()

    def _getValue(self, result, reusable):
        return result['personal']['avatar']['playerRank']

    def _getWreathImage(self, result, reusable):
        return self._PLACE_TO_WREATH.get(self.value, self._DEFAULT_ICON())


class SimpleEfficiencyParameter(StatsItemBlock):
    __slots__ = ()

    def _getValue(self, result, reusable):
        personalInfo = reusable.getPersonalVehiclesInfo(result['personal'])
        return getattr(personalInfo, self.type)

    def _getWreathImage(self, result, reusable):
        personalInfo = reusable.getPlayerInfo()
        personalDBID = personalInfo.dbID
        place = 1
        maxValue = self.value
        allPlayers = reusable.getAllPlayersIterator(result['vehicles'])
        for item in allPlayers:
            player = item.player
            if player.dbID <= 0 or player.dbID == personalDBID:
                continue
            curValue = getattr(item, self.type)
            if curValue > maxValue:
                place += 1
                maxValue = curValue

        return self._PLACE_TO_WREATH.get(place, self._DEFAULT_ICON())


class StatsBlock(base.StatsBlock):
    __slots__ = ()
    _itemsFactory = {StatsItemType.PLACE: PlaceParameter,
     StatsItemType.KILLS: SimpleEfficiencyParameter,
     StatsItemType.DAMAGE_DEAL: SimpleEfficiencyParameter,
     StatsItemType.DAMAGE_BLOCK: SimpleEfficiencyParameter}

    def setRecord(self, result, reusable):
        for itemType in ITEMS_ORDER:
            classType = self._itemsFactory.get(itemType)
            if classType is None:
                LOG_ERROR('Incorrect parameter of personal efficiency')
                continue
            component = classType(itemType)
            component.setRecord(result, reusable)
            self.addComponent(self.getNextComponentIndex(), component)

        return


class PlayerBlock(base.StatsBlock):
    __slots__ = ('isPersonal', 'isSquadMode', 'userName', 'clanAbbrev', 'place', 'squadIdx', 'hiddenName', 'kills', 'damage', 'damageBlocked', 'vehicleName', 'vehicleType', 'databaseID')

    def __init__(self, meta=None, field='', *path):
        super(PlayerBlock, self).__init__(meta, field, *path)
        self.isPersonal = False
        self.isSquadMode = False
        self.userName = ''
        self.hiddenName = ''
        self.clanAbbrev = ''
        self.place = 0
        self.squadIdx = 0
        self.kills = 0
        self.damage = 0
        self.damageBlocked = 0
        self.vehicleName = ''
        self.vehicleType = ''
        self.databaseID = 0

    def setRecord(self, vehicleSummarizeInfo, reusable):
        player = vehicleSummarizeInfo.player
        dbID = player.dbID
        if player.realName == player.fakeName:
            self.userName = player.realName
            self.clanAbbrev = player.clanAbbrev
        elif self.isPersonal:
            self.userName = player.realName
            self.clanAbbrev = player.clanAbbrev
            self.hiddenName = player.fakeName
        else:
            self.userName = player.fakeName
            self.hiddenName = player.realName
            self.clanAbbrev = ''
        avatarInfo = reusable.avatars.getAvatarInfo(dbID)
        if avatarInfo is not None and avatarInfo.extensionInfo is not None:
            self.place = avatarInfo.extensionInfo.get('playerRank', 0)
        return


class TeamStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        allPlayers = reusable.getAllPlayersIterator(result)
        personalInfo = reusable.getPlayerInfo()
        personalDBID = personalInfo.dbID
        team = personalInfo.team if personalInfo.squadIndex else 0
        for item in allPlayers:
            player = item.player
            if player.dbID <= 0:
                continue
            block = PlayerBlock()
            block.isPersonal = personalDBID == player.dbID
            block.isSquadMode = team != 0 and team == player.team
            block.squadIdx = player.squadIndex
            block.damage = item.damageDealt
            block.damageBlocked = item.damageBlockedByArmor
            block.kills = item.kills
            block.vehicleName = item.vehicle.shortUserName
            block.vehicleType = item.vehicle.type
            block.databaseID = item.player.dbID
            block.setRecord(item, reusable)
            self.addComponent(self.getNextComponentIndex(), block)
