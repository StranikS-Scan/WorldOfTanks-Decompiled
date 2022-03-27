# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/rts_battles.py
from itertools import chain
import typing
from gui.battle_results.components import base, personal, style
from gui.battle_results.components.common import RegularFinishResultBlock, convertStrToNumber
from gui.battle_results.components.personal import KillerPlayerNameBlock, fillKillerInfoBlock, fillVehicleStateBlock, fillTeamKillerBlock, EnemyDetailsBlock, EnemyTeamBaseDetailBlock, AllyTeamBaseDetailBlock
from gui.battle_results.components.vehicles import PersonalVehiclesBaseStatsBlock, AllVehicleBaseStatValuesBlock, RegularVehicleStatValuesBlock, RegularVehicleStatsBlock, TeamStatsBlock, TwoTeamsStatsBlock
from gui.battle_results.reusable.personal import RTSPersonalInfo
from gui.battle_results.battle_results_helper import getSupplyName, filterTechnique, getTeamSuppliesByType
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl import backport
from gui.impl.backport.backport_system_locale import getIntegralFormat
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from gui.shared.formatters import numbers
from constants import ARENA_BONUS_TYPE, DEATH_REASON
from RTSShared import RTSSupply
from shared_utils import first
from gui import makeHtmlString
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
_UNDEFINED_EFFICIENCY_VALUE = '-'
_RTS_STR_PATH = R.strings.rts_battles.battleResults
_BASE_STR_PATH = R.strings.battle_results

def _getAvatarInfo(result):
    return result[_RECORD.PERSONAL][_RECORD.PERSONAL_AVATAR]


def _getRTS1x7Currency(result):
    avatarInfo = _getAvatarInfo(result)
    return avatarInfo.get('rts1x7TokensGain', 0)


def _getRTS1x1Currency(result):
    avatarInfo = _getAvatarInfo(result)
    return avatarInfo.get('rts1x1TokensGain', 0)


def _isRTS1x1(reusable):
    return reusable.common.arenaBonusType == ARENA_BONUS_TYPE.RTS_1x1


def _isRTS1x7(reusable):
    return reusable.common.arenaBonusType == ARENA_BONUS_TYPE.RTS


def _isTanker(reusable):
    return _isRTS1x7(reusable) and not reusable.personal.isCommander


def _fillSupplyKillerBlock(block, deathReason, killerID, reusable):
    fillVehicleStateBlock(block, deathReason)
    killerBlock = SupplyKillerNameBlock()
    killerBlock.setSupplyInfo(getSupplyName(killerID, reusable))
    fillTeamKillerBlock(reusable, killerID, killerBlock, block)
    block.addComponent(block.getNextComponentIndex(), killerBlock)


def _get1x1OpponentPlayerInfo(reusable):
    for dbID, info in reusable.players.getPlayerInfoIterator():
        if dbID != reusable.common.commanderID:
            return info


def _makeStrWithThousand(value, digitLimit=4):
    return numbers.makeStringWithThousandSymbol(value, digitLimit=digitLimit, formatter=convertStrToNumber, defNegativeOrZero=0)


def _makeStrWithThousandSlash(left, right):
    return (_makeStrWithThousand(left, digitLimit=3), _makeStrWithThousand(right, digitLimit=3))


class _BaseTeamTitle(base.StatsItem):
    __slots__ = ()
    _RTS_STR_PATH = _RTS_STR_PATH.team.stats
    _BASE_STR_PATH = _BASE_STR_PATH.team.stats

    def _getCommanderTeamTitle(self, reusable):
        pass


class AllyTeamTitle(_BaseTeamTitle):
    __slots__ = ()

    def _convert(self, result, reusable):
        return backport.text(_RTS_STR_PATH.team.stats.battleResources()) if reusable.personal.isCommander else backport.text(self._BASE_STR_PATH.ownTeam())


class EnemyTeamTitle(_BaseTeamTitle):
    __slots__ = ()

    def _convert(self, result, reusable):
        if _isRTS1x1(reusable):
            opponentInfo = _get1x1OpponentPlayerInfo(reusable)
            if opponentInfo:
                return backport.text(_RTS_STR_PATH.team.stats.enemyStrategist(), playerName=opponentInfo.getFullName())
            return None
        else:
            commanderID = reusable.common.commanderID
            commanderInfo = reusable.players.getPlayerInfo(commanderID)
            return backport.text(self._BASE_STR_PATH.enemyTeam()) if reusable.personal.isCommander else backport.text(_RTS_STR_PATH.team.stats.enemyStrategist(), playerName=commanderInfo.getFullName())


class FinishResultBlock(RegularFinishResultBlock):
    __slots__ = ()

    @classmethod
    def _getFinishReasonLabel(cls, reusable, teamResult):
        return super(FinishResultBlock, cls)._getFinishReasonLabel(reusable, teamResult)


class PersonalVehicleNamesBlock(personal.PersonalVehicleNamesBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        if reusable.personal.isCommander:
            self.addNextComponent(base.DirectStatsItem('', backport.text(_RTS_STR_PATH.commander())))
        else:
            super(PersonalVehicleNamesBlock, self).setRecord(result, reusable)


class SupplyKillerNameBlock(KillerPlayerNameBlock):
    __slots__ = ()

    def setSupplyInfo(self, supplyName):
        self.fakeNameLabel = supplyName
        self.realNameLabel = supplyName
        self.fullNameLabel = supplyName


class CommanderVehicleBlock(personal.PersonalVehicleBlock):
    __slots__ = ()

    def setVehicle(self, item):
        pass

    def setRecord(self, result, reusable):
        self.isVehicleStatusDefined = False
        self.vehicleIcon = backport.image(R.images.gui.maps.icons.rtsBattles.postbattle.strategist())
        if reusable.personal.avatar.isPrematureLeave:
            self.isPrematureLeave = True
            self.vehicleState = backport.text(_BASE_STR_PATH.common.vehicleState.prematureLeave())


class TankmanVehicleBlock(personal.PersonalVehicleBlock):
    __slots__ = ()

    def _setKillerInfo(self, deathReason, killerID, reusable):
        if killerID in reusable.common.getAllSupplies():
            _fillSupplyKillerBlock(self, deathReason, killerID, reusable)
        else:
            fillKillerInfoBlock(self, deathReason, killerID, reusable)


class PersonalVehiclesBlock(personal.PersonalVehiclesBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        if reusable.personal.isCommander:
            component = CommanderVehicleBlock()
            component.setRecord(result, reusable)
            self.addComponent(self.getNextComponentIndex(), component)
        else:
            super(PersonalVehiclesBlock, self).setRecord(result, reusable)

    def _createComponent(self):
        return TankmanVehicleBlock()


class IsCommanderBlock(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return reusable.personal.isCommander


class EfficiencyTitle(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        if _isRTS1x7(reusable):
            if reusable.personal.isCommander:
                return backport.text(_BASE_STR_PATH.common.battleEfficiency.title())
            commanderID = reusable.common.commanderID
            commanderInfo = reusable.players.getPlayerInfo(commanderID)
            playerName = commanderInfo.getFullName()
            return backport.text(_RTS_STR_PATH.tankerBattleEfficiency.title(), playerName=playerName)
        elif _isRTS1x1(reusable):
            opponentInfo = _get1x1OpponentPlayerInfo(reusable)
            if opponentInfo:
                return backport.text(_RTS_STR_PATH.tankerBattleEfficiency.title(), playerName=opponentInfo.getFullName())
            return None
        else:
            return None


class RTS1x7CurrencyBalanceChange(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return getIntegralFormat(_getRTS1x7Currency(result))


class RTS1x1CurrencyBalanceChange(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return getIntegralFormat(_getRTS1x1Currency(result))


class RTSEnemyDetailsBlock(EnemyDetailsBlock):
    __slots__ = ('isUserNameHidden',)

    def setRecord(self, result, reusable):
        self.isUserNameHidden = _isRTS1x1(reusable) or not reusable.personal.isCommander
        super(RTSEnemyDetailsBlock, self).setRecord(result, reusable)


class SupplyTotalEfficiencyDetailsHeader(personal.TotalEfficiencyDetailsHeader):
    __slots__ = ()

    def setRecord(self, result, reusable):
        for _, _, supplies in reusable.getPersonalDetailsIterator(result, onlySummary=True):
            if not supplies:
                return
            kills = sum((s.targetKills for s in supplies))
            self.kills = numbers.formatInt(kills, _UNDEFINED_EFFICIENCY_VALUE)
            self.killsTooltip = self._makeEfficiencyHeaderTooltip('summKill', kills)
            damageDealt = sum((s.damageDealt for s in supplies))
            self.damageDealt = numbers.makeStringWithThousandSymbol(damageDealt, formatter=self._formatter)
            self.damageDealtTooltip = self._makeEfficiencyHeaderTooltip('summDamage', damageDealt)
            spotted = sum((s.spotted for s in supplies))
            self.spotted = numbers.formatInt(spotted, _UNDEFINED_EFFICIENCY_VALUE)
            self.spottedTooltip = self._makeEfficiencyHeaderTooltip('summSpotted', spotted)
            damageBlockedByArmor = sum((s.damageBlockedByArmor for s in supplies))
            self.damageBlockedByArmor = numbers.makeStringWithThousandSymbol(damageBlockedByArmor, formatter=self._formatter)
            self.damageBlockedTooltip = self._makeEfficiencyHeaderTooltip('summArmor', damageBlockedByArmor)
            damageAssisted = sum((s.damageAssisted for s in supplies))
            self.damageAssisted = numbers.makeStringWithThousandSymbol(damageAssisted, formatter=self._formatter)
            self.damageAssistedTooltip = self._makeEfficiencyHeaderTooltip('summAssist', damageAssisted)
            self.damageAssistedStun = ''
            self.criticalDamages = ''
            self.hasEfficencyStats = kills + damageDealt + spotted + damageBlockedByArmor + damageAssisted > 0


class TotalEfficiencyDetailsBlock(personal.TotalEfficiencyDetailsBlock):
    __slots__ = ('_result',)

    def setRecord(self, result, reusable):
        self._result = result
        blocks = []
        for bases, vehicles, supplies in reusable.getPersonalDetailsIterator(result):
            components = []
            self._createBasesBlock(bases, reusable, components)
            techniqueBlock = base.StatsBlock(base.ListMeta())
            supplyDetailedBlocks = self._createDetailedBlocks(reusable, supplies)
            if supplyDetailedBlocks:
                label = self._getBlockLabel(reusable, 'supplies')
                self._appendDetailedBlock(techniqueBlock, label, supplyDetailedBlocks, 'supplyEfficiencyHeader')
            vehicleDetailedBlocks = self._createDetailedBlocks(reusable, vehicles)
            if vehicleDetailedBlocks:
                label = self._getBlockLabel(reusable, 'technique')
                self._appendDetailedBlock(techniqueBlock, label, vehicleDetailedBlocks, 'efficiencyHeader')
            for component in components:
                techniqueBlock.addComponent(techniqueBlock.getNextComponentIndex(), component)

            blocks.append(techniqueBlock)

        for block in blocks[-1:] + blocks[:-1]:
            self.addComponent(self.getNextComponentIndex(), block)

    def _createEnemyBlock(self):
        return RTSEnemyDetailsBlock()

    @staticmethod
    def _getBlockLabel(reusable, postfix):
        prefix = ''
        if _isRTS1x1(reusable) or _isTanker(reusable):
            prefix = 'personal_score_'
        return backport.text(_RTS_STR_PATH.battleEfficiency.dyn(prefix + postfix)())

    def _createBasesBlock(self, bases, reusable, components):
        for info in bases:
            if info.capturePoints > 0:
                components.append(style.GroupMiddleLabelBlock(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_BASES))
                component = EnemyTeamBaseDetailBlock()
                component.setRecord(info, reusable)
                components.append(component)
            component = RTSAllyTeamBaseDetailBlock()
            hasData = component.setRecord(self._result, reusable)
            if hasData:
                components.append(component)


class RTSAllyTeamBaseDetailBlock(AllyTeamBaseDetailBlock):

    def setRecord(self, result, reusable):
        vehicleInfo = reusable.getPersonalVehiclesInfo(result, reusable)
        defencePoints = vehicleInfo.droppedCapturePoints
        self.defenceTotalItems = defencePoints
        if self._showDefencePoints and defencePoints > 0:
            self.defenceValues = (backport.getIntegralFormat(defencePoints),)
            self.defenceNames = (backport.text(R.strings.tooltips.battleResults.defence.totalPoints()),)
            return True
        return False


class PersonalVehiclesRTSStatsBlock(PersonalVehiclesBaseStatsBlock):
    __slots__ = ()

    def _createStatsBlock(self, reusable=None):
        if _isRTS1x1(reusable):
            return RTS1x1VehicleStatValuesBlock()
        return RTS1x7VehicleStatValuesBlock() if reusable.personal.isCommander else RTSVehicleStatValuesBlock()


class RTSVehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('tankmanDamageToSupplies', 'supplyDamageToTankman', 'spottedStrategistItems', 'spottedSupplies', 'damagedKilledSupplies')

    def __init__(self, meta=None, field='', *path):
        super(RTSVehicleStatValuesBlock, self).__init__(meta, field, *path)
        self.tankmanDamageToSupplies = 0
        self.supplyDamageToTankman = 0
        self.spottedStrategistItems = 0
        self.spottedSupplies = 0
        self.damagedKilledSupplies = (0, 0)

    def setRecord(self, result, reusable):
        super(RTSVehicleStatValuesBlock, self).setRecord(result, reusable)
        self.tankmanDamageToSupplies = style.getIntegralFormatIfNoEmpty(result.supplyDamageDealt)
        self.supplyDamageToTankman = style.getIntegralFormatIfNoEmpty(result.damageReceivedFromSupply)
        self.spottedStrategistItems = style.getIntegralFormatIfNoEmpty(result.spotted)
        self.spottedSupplies = style.getIntegralFormatIfNoEmpty(result.spottedSupplies)
        self.damagedKilledSupplies = (len(result.damagedSupplies), result.killedSupplies)
        self.damagedKilled = (len(result.damagedTanks), result.kills - result.killedSupplies)


class RTS1x7VehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('shotsByTanksSupplies', 'damageDealtByTanksSupplies', 'damageBlockedByTanksSupplies', 'hitsByTanks', 'hitsBySupplies')

    def __init__(self, meta=None, field='', *path):
        super(RTS1x7VehicleStatValuesBlock, self).__init__(meta, field, *path)
        self.shotsByTanksSupplies = (0, 0)
        self.damageDealtByTanksSupplies = (0, 0)
        self.damageBlockedByTanksSupplies = (0, 0)
        self.hitsByTanks = (0, 0)
        self.hitsBySupplies = (0, 0)

    def setRecord(self, result, reusable):
        makeStr = _makeStrWithThousandSlash
        self.shotsByTanksSupplies = makeStr(result.shotsByTanks, result.shotsBySupplies)
        self.damageDealtByTanksSupplies = makeStr(result.damageDealtByTanks, result.damageDealtBySupplies)
        self.damageBlockedByTanksSupplies = makeStr(result.damageBlockedByTanks, result.damageBlockedBySupplies)
        self.hits = makeStr(result.directEnemyHits, result.piercingEnemyHits)
        self.hitsByTanks = makeStr(result.directEnemyHitsByTanks, result.piercingEnemyHitsByTanks)
        self.hitsBySupplies = makeStr(result.directEnemyHitsBySupplies, result.piercingEnemyHitsBySupplies)
        self.explosionHits = makeStr(result.explosionHitsByTanks, result.explosionHitsBySupplies)
        self.sniperDamageDealt = makeStr(result.sniperDamageDealtByTanks, result.sniperDamageDealtBySupplies)
        self.directHitsReceived = style.getIntegralFormatIfNoEmpty(result.directHitsReceived)
        self.piercingsReceived = style.getIntegralFormatIfNoEmpty(result.piercingsReceived)
        self.noDamageDirectHitsReceived = style.getIntegralFormatIfNoEmpty(result.noDamageDirectHitsReceived)
        self.explosionHitsReceived = style.getIntegralFormatIfNoEmpty(result.explosionHitsReceived)
        self.teamHitsDamage = makeStr(result.tkills, result.tdamageDealt)
        self.spotted = style.getIntegralFormatIfNoEmpty(result.spotted)
        self.damagedKilled = (len(result.damagedTanks), result.kills)
        self.damageAssisted = style.getIntegralFormatIfNoEmpty(result.damageAssisted)
        self.damageAssistedStun = style.getIntegralFormatIfNoEmpty(result.damageAssistedStun)
        self.stunNum = style.getIntegralFormatIfNoEmpty(result.stunNum)
        self.stunDuration = style.getFractionalFormatIfNoEmpty(result.stunDuration)
        self.capturePoints = (result.capturePoints, result.droppedCapturePoints)
        self.mileage = result.mileage


class RTS1x1VehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('tankmanDamageToSupplies', 'supplyDamageToTankman', 'spottedStrategistItems', 'spottedSupplies', 'damagedKilledSupplies', 'shotsByTanksSupplies', 'damageDealtByTanksSupplies', 'damageBlockedByTanksSupplies', 'hitsByTanks', 'hitsBySupplies')

    def __init__(self, meta=None, field='', *path):
        super(RTS1x1VehicleStatValuesBlock, self).__init__(meta, field, *path)
        self.tankmanDamageToSupplies = 0
        self.supplyDamageToTankman = 0
        self.spottedStrategistItems = 0
        self.spottedSupplies = 0
        self.damagedKilledSupplies = (0, 0)
        self.shotsByTanksSupplies = (0, 0)
        self.damageDealtByTanksSupplies = (0, 0)
        self.damageBlockedByTanksSupplies = (0, 0)
        self.hitsByTanks = (0, 0)
        self.hitsBySupplies = (0, 0)

    def setRecord(self, result, reusable):
        makeStr = _makeStrWithThousandSlash
        self.shotsByTanksSupplies = makeStr(result.shotsByTanks, result.shotsBySupplies)
        self.hits = makeStr(result.directEnemyHits, result.piercingEnemyHits)
        self.hitsByTanks = makeStr(result.directEnemyHitsByTanks, result.piercingEnemyHitsByTanks)
        self.hitsBySupplies = makeStr(result.directEnemyHitsBySupplies, result.piercingEnemyHitsBySupplies)
        self.explosionHits = makeStr(result.explosionHitsByTanks, result.explosionHitsBySupplies)
        self.damageDealtByTanksSupplies = makeStr(result.damageDealtByTanks, result.damageDealtBySupplies)
        self.sniperDamageDealt = makeStr(result.sniperDamageDealtByTanks, result.sniperDamageDealtBySupplies)
        self.directHitsReceived = style.getIntegralFormatIfNoEmpty(result.directHitsReceived)
        self.piercingsReceived = style.getIntegralFormatIfNoEmpty(result.piercingsReceived)
        self.noDamageDirectHitsReceived = style.getIntegralFormatIfNoEmpty(result.noDamageDirectHitsReceived)
        self.explosionHitsReceived = style.getIntegralFormatIfNoEmpty(result.explosionHitsReceived)
        self.damageBlockedByTanksSupplies = makeStr(result.damageBlockedByTanks, result.damageBlockedBySupplies)
        self.teamHitsDamage = makeStr(result.tkills, result.tdamageDealt)
        self.spotted = style.getIntegralFormatIfNoEmpty(result.spotted)
        self.damagedKilled = (len(result.damagedTanks), result.kills - result.killedSupplies)
        self.spottedSupplies = style.getIntegralFormatIfNoEmpty(result.spottedSupplies)
        self.damagedKilledSupplies = (len(result.damagedSupplies), result.killedSupplies)
        self.damageAssisted = style.getIntegralFormatIfNoEmpty(result.damageAssisted)
        self.tankmanDamageToSupplies = style.getIntegralFormatIfNoEmpty(result.supplyDamageDealt)
        self.supplyDamageToTankman = style.getIntegralFormatIfNoEmpty(result.damageReceivedFromSupply)
        self.stunDuration = style.getFractionalFormatIfNoEmpty(result.stunDuration)
        self.damageAssistedStun = style.getIntegralFormatIfNoEmpty(result.damageAssistedStun)
        self.stunNum = style.getIntegralFormatIfNoEmpty(result.stunNum)
        self.capturePoints = (result.capturePoints, result.droppedCapturePoints)
        self.mileage = result.mileage


class RTSCommanderAllVehiclesStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('commanderSupplyDamage', 'damageToCommanderSupplies')

    def __init__(self, meta=None, field='', *path):
        super(RTSCommanderAllVehiclesStatValuesBlock, self).__init__(meta, field, *path)
        self.commanderSupplyDamage = 0
        self.damageToCommanderSupplies = 0

    def setRecord(self, result, reusable):
        super(RTSCommanderAllVehiclesStatValuesBlock, self).setRecord(result, reusable)
        self.commanderSupplyDamage = style.getIntegralFormatIfNoEmpty(result.supplyDamageDealt)
        self.damageToCommanderSupplies = style.getIntegralFormatIfNoEmpty(result.supplyDamageReceived)


class AllTankmansVehicleStatValuesBlock(AllVehicleBaseStatValuesBlock):
    __slots__ = ()

    def _createStatsBlock(self, _=None):
        return RTSVehicleStatValuesBlock()


class RTSVehicleStatsBlock(RegularVehicleStatsBlock):

    def _setKillerInfo(self, deathReason, killerID, reusable):
        if killerID in reusable.common.getAllSupplies():
            if deathReason == DEATH_REASON.DESTROYED_BY_RAMMING:
                deathReason = DEATH_REASON.DESTROYED_BY_SUPPLY_RAMMING
            _fillSupplyKillerBlock(self, deathReason, killerID, reusable)
        else:
            if _isRTS1x1(reusable):
                killerInfo = _get1x1OpponentPlayerInfo(reusable)
                killerDBID = killerInfo.dbID if killerInfo else 0
                killerID = reusable.vehicles.getVehicleID(killerDBID)
            elif _isRTS1x7(reusable) and not reusable.personal.isCommander:
                commanderID = reusable.common.commanderID
                killerID = reusable.vehicles.getVehicleID(commanderID)
            fillKillerInfoBlock(self, deathReason, killerID, reusable)


class RTSCommanderVehicleStatsBlock(RegularVehicleStatsBlock):
    __slots__ = ()


class RTSTwoTeamsStatsBlock(TwoTeamsStatsBlock):

    def setEnemyCommanderBlockRef(self, blockRef):
        self.right.setCommanderBlockRef(blockRef)

    def clearEnemyCommanderBlockRef(self):
        self.right.clearCommanderBlockRef()


class RTSTeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(RTSTeamStatsBlock, self).__init__(None, meta, field, *path)
        return

    def setRecord(self, result, reusable):
        if self._isCommanderData(reusable):
            self._setCommanderTeam(result, reusable)
        else:
            self._setTankmanTeam(result, reusable)

    def _isCommanderData(self, reusable):
        return _isRTS1x1(reusable)

    def _setCommanderTeam(self, result, reusable):
        teamPlayerInfo = self._getTeamPlayerInfo(reusable)
        vehicles, supplies = filterTechnique(result)
        for idx, item in enumerate(chain(supplies, vehicles)):
            if item.vehicle.isCommander:
                if self._processCommanderVehicle(item, reusable):
                    continue
            block = self._createCommanderBlock(item.vehicle, reusable)
            block.vehicleSort = idx
            block.setRecord(item, reusable)
            if teamPlayerInfo:
                block.setPlayerInfo(teamPlayerInfo)
            self.addNextComponent(block)

    def _processCommanderVehicle(self, item, reusable):
        return True

    def _getBlockType(self, result=None):
        return RTSVehicleStatsBlock()

    def _setTankmanTeam(self, result, reusable):
        super(RTSTeamStatsBlock, self).setRecord(result, reusable)

    @staticmethod
    def _createCommanderBlock(vehicle, reusable):
        if vehicle.isSupply:
            return RTSSupplyStatsBlock()
        return RTSVehicleStatsBlock() if _isRTS1x1(reusable) else RTSCommanderVehicleStatsBlock()


class RTSAllyTeamStatsBlock(RTSTeamStatsBlock):

    def _isCommanderData(self, reusable):
        isCommander = super(RTSAllyTeamStatsBlock, self)._isCommanderData(reusable)
        return isCommander or reusable.personal.isCommander


class RTSEnemyTeamStatsBlock(RTSTeamStatsBlock):
    __slots__ = ('__commanderBlockRef',)

    def __init__(self, meta=None, field='', *path):
        super(RTSEnemyTeamStatsBlock, self).__init__(meta, field, *path)
        self.__commanderBlockRef = None
        return

    def setCommanderBlockRef(self, commanderBlockRef):
        self.__commanderBlockRef = commanderBlockRef

    def clearCommanderBlockRef(self):
        self.__commanderBlockRef = None
        return

    def _isCommanderData(self, reusable):
        isCommander = super(RTSEnemyTeamStatsBlock, self)._isCommanderData(reusable)
        return isCommander or not reusable.personal.isCommander

    def _processCommanderVehicle(self, item, reusable):
        self.__commanderBlockRef.setCommanderData(item, reusable)
        return True

    def _getTeamPlayerInfo(self, reusable):
        return _get1x1OpponentPlayerInfo(reusable) if _isRTS1x1(reusable) else None


class RTSCommanderUserVehicleStatsBlock(RTSCommanderVehicleStatsBlock):

    def __init__(self, meta=None, field='', *path):
        super(RTSCommanderUserVehicleStatsBlock, self).__init__(meta, field, *path)
        self.__isInitialized = False

    def setCommanderData(self, item, reusable):
        super(RTSCommanderUserVehicleStatsBlock, self).setRecord(item, reusable)
        self.vehicleSort = 0
        self.__isInitialized = True

    def setRecord(self, record, reusable):
        pass

    def getVO(self):
        return None if not self.__isInitialized else super(RTSCommanderUserVehicleStatsBlock, self).getVO()


class RTSSupplyStatValuesBlock(base.StatsBlock):
    __slots__ = ('shotsBySupplies', 'hits', 'damageDealtBySupplies', 'sniperDamageDealtBySupplies', 'directHitsReceivedBySupplies', 'piercingsReceivedBySupplies', 'noDamageDirectHitsReceivedBySupplies', 'spottedTanksBySupplies', 'damagedKilledTanksBySupplies')

    def __init__(self, meta=None, field='', *path):
        super(RTSSupplyStatValuesBlock, self).__init__(meta, field, *path)
        self.shotsBySupplies = 0
        self.hits = (0, 0)
        self.damageDealtBySupplies = 0
        self.sniperDamageDealtBySupplies = 0
        self.directHitsReceivedBySupplies = 0
        self.piercingsReceivedBySupplies = 0
        self.noDamageDirectHitsReceivedBySupplies = 0
        self.spottedTanksBySupplies = 0
        self.damagedKilledTanksBySupplies = (0, 0)

    def setRecord(self, result, reusable):
        self.shotsBySupplies = style.getIntegralFormatIfNoEmpty(result.shots)
        self.hits = (result.directHits, result.piercings)
        self.damageDealtBySupplies = style.getIntegralFormatIfNoEmpty(result.damageDealt)
        self.sniperDamageDealtBySupplies = style.getIntegralFormatIfNoEmpty(result.sniperDamageDealt)
        self.directHitsReceivedBySupplies = style.getIntegralFormatIfNoEmpty(result.directHitsReceived)
        self.piercingsReceivedBySupplies = style.getIntegralFormatIfNoEmpty(result.piercingsReceived)
        self.noDamageDirectHitsReceivedBySupplies = style.getIntegralFormatIfNoEmpty(result.noDamageDirectHitsReceived)
        self.spottedTanksBySupplies = style.getIntegralFormatIfNoEmpty(result.spotted - result.spottedSupplies)
        self.damagedKilledTanksBySupplies = (len(result.damagedTanks), result.kills - result.killedSupplies)

    def getVO(self):
        return [ style.makeStatValue(component.getField(), component.getVO()) for component in self._components ]


class RTSBarricadesSupplyStatValuesBlock(base.StatsBlock):
    __slots__ = ('totalDamagedByBarricades', 'killedTanksByBarricades')

    def __init__(self, meta=None, field='', *path):
        super(RTSBarricadesSupplyStatValuesBlock, self).__init__(meta, field, *path)
        self.totalDamagedByBarricades = 0
        self.killedTanksByBarricades = 0

    def setRecord(self, result, reusable):
        self.totalDamagedByBarricades = style.getIntegralFormatIfNoEmpty(result.damageDealt)
        self.killedTanksByBarricades = style.getIntegralFormatIfNoEmpty(result.kills - result.killedSupplies)

    def getVO(self):
        return [ style.makeStatValue(component.getField(), component.getVO()) for component in self._components ]


class RTSWatchTowerSupplyStatValuesBlock(base.StatsBlock):
    __slots__ = ('spottedEnemiesByWatchtowers', 'damagedByWatchtowers')

    def __init__(self, meta=None, field='', *path):
        super(RTSWatchTowerSupplyStatValuesBlock, self).__init__(meta, field, *path)
        self.damagedByWatchtowers = 0
        self.spottedEnemiesByWatchtowers = 0

    def setRecord(self, result, reusable):
        self.damagedByWatchtowers = style.getIntegralFormatIfNoEmpty(result.damageDealt)
        self.spottedEnemiesByWatchtowers = style.getIntegralFormatIfNoEmpty(result.spotted)

    def getVO(self):
        return [ style.makeStatValue(component.getField(), component.getVO()) for component in self._components ]


class RTSAllSupplyStatValuesBlock(base.StatsBlock):
    __slots__ = ()
    _SUPPLY_BLOCKS = {RTSSupply.BARRICADES: RTSBarricadesSupplyStatValuesBlock,
     RTSSupply.WATCH_TOWER: RTSWatchTowerSupplyStatValuesBlock}

    def setRecord(self, result, reusable):
        _, iterator = result
        for vehInfo in iterator:
            block = self._createStatBlock(vehInfo)
            block.setRecord(vehInfo, reusable)
            self.addNextComponent(block)

    def _createStatBlock(self, vehInfo):
        rtsSupplyType = RTSSupply.TAG_TO_SUPPLY[getVehicleClassTag(vehInfo.vehicle.tags)]
        block = self._SUPPLY_BLOCKS.get(rtsSupplyType, RTSSupplyStatValuesBlock)
        return block()


class RTSSupplyStatsBlock(RegularVehicleStatsBlock):

    def _setXP(self, result, noPenalties=True):
        self.xp = 0
        self.xpSort = 0

    def _setAchievements(self, result, reusable):
        pass

    def _setVehicleState(self, result, reusable):
        if self._isObserver:
            return
        self.killerID = -1
        self.deathReason = result.deathReason
        self.vehicleState = style.makeSupplyStatus(alive=result.aliveCount, total=len(getTeamSuppliesByType(self.intCD, self._team, reusable)))
        self.isTeamKiller = result.isTeamKiller


class _TotalEconomicsDetailsBlock(base.StatsBlock):
    __slots__ = ('__blockClass',)

    def __init__(self, block, meta=None, field='', *path):
        super(_TotalEconomicsDetailsBlock, self).__init__(meta, field, *path)
        self.__blockClass = block

    def setRecord(self, result, reusable):
        block = self.__blockClass(base.ListMeta(registered=True))
        block.hasAnyPremium = reusable.hasAnyPremiumInPostBattle
        block.canResourceBeFaded = reusable.canResourceBeFaded
        block.setRecord(result, reusable)
        self.addNextComponent(block)


class TotalMoneyDetailsBlock(_TotalEconomicsDetailsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(TotalMoneyDetailsBlock, self).__init__(MoneyDetailsBlock, meta, field, *path)


class _EconomicsDetailsBlock(base.StatsBlock):
    __slots__ = ('hasAnyPremium', 'canResourceBeFaded')

    def __init__(self, meta=None, field='', *path):
        super(_EconomicsDetailsBlock, self).__init__(meta, field, *path)
        self.hasAnyPremium = False
        self.canResourceBeFaded = True

    def _addEmptyRow(self):
        self.addNextComponent(style.EmptyStatRow())

    def _addStatsRow(self, label, labelArgs=None, column1=None, column2=None, column3=None, column4=None, htmlKey=''):
        value = style.makeStatRow(label, labelArgs=labelArgs, column1=column1, column2=column2, column3=column3, column4=column4, htmlKey=htmlKey)
        self.addNextComponent(base.DirectStatsItem('', value))


class MoneyDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()
    _intermediateTotalRecords = ('credits', 'originalCreditsToDraw', 'originalCreditsToDrawSquad')

    def setRecord(self, result, reusable):
        isTotalShown = False
        _, _, _, additionalRecords = first(reusable.personal.getMoneyRecords())
        self.__addBaseCredits(result)
        if _isTanker(reusable):
            isTotalShown |= self.__addEventsMoneyForTanker(result)
        else:
            isTotalShown |= self.__addEventsMoneyForStrategist(result)
        if isTotalShown:
            self._addEmptyRow()
            if _isTanker(reusable):
                self.__addBattleResultsForTanker(result)
            else:
                self.__addBattleResultsForStrategist(result)
            self._addEmptyRow()
        if _isTanker(reusable):
            self._addAdditionalInfo(additionalRecords)
        if _isTanker(reusable):
            self.__addTotalResultsForTanker(additionalRecords, result)
        else:
            self.__addTotalResultsForStrategist(result)
        self._addEmptyRow()

    def __addBaseCredits(self, result):
        avatarInfo = _getAvatarInfo(result)
        baseCredits = avatarInfo['credits'] - avatarInfo['eventCredits']
        premiumCredits = baseCredits
        self._addStatsRow('base', column1=style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium), column3=style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium))

    def _addAdditionalInfo(self, additionalRecords):
        self.__addStatsItem('autoRepair', additionalRecords, 'autoRepairCost')
        self.__addAutoCompletion('autoLoad', additionalRecords, 'autoLoadCredits', 'autoLoadGold')
        self.__addAutoCompletion('autoEquip', additionalRecords, 'autoEquipCredits', 'autoEquipGold')
        self._addEmptyRow()

    def __addStatsItem(self, label, baseRecords, *names):
        baseValue = baseRecords.getRecord(*names)
        premiumValue = baseValue
        baseLabel = style.makeCreditsLabel(baseValue, canBeFaded=not self.hasAnyPremium)
        premiumLabel = style.makeCreditsLabel(premiumValue, canBeFaded=self.hasAnyPremium)
        self._addStatsRow(label, column1=baseLabel, column3=premiumLabel)
        return baseValue != 0 or premiumValue != 0

    def __addAutoCompletion(self, label, additionalRecords, creditsRecord, goldRecord):
        credit = additionalRecords.getRecord(creditsRecord)
        columns = {'column1': style.makeCreditsLabel(credit, canBeFaded=not self.hasAnyPremium),
         'column3': style.makeCreditsLabel(credit, canBeFaded=self.hasAnyPremium)}
        self._addStatsRow(label, **columns)

    def __addEventsMoneyForStrategist(self, result):
        avatarInfo = _getAvatarInfo(result)
        baseEventCredits = avatarInfo['eventCredits']
        premiumEventCredits = baseEventCredits
        if baseEventCredits:
            columns = {}
            if baseEventCredits:
                columns['column1'] = style.makeCreditsLabel(baseEventCredits, canBeFaded=not self.hasAnyPremium)
            if premiumEventCredits:
                columns['column3'] = style.makeCreditsLabel(premiumEventCredits, canBeFaded=self.hasAnyPremium)
            self._addStatsRow('event', **columns)
            return True
        return False

    def __addEventsMoneyForTanker(self, result):
        avatarInfo = _getAvatarInfo(result)
        baseEventCredits = avatarInfo['eventCredits']
        premiumEventCredits = baseEventCredits
        if baseEventCredits or premiumEventCredits:
            columns = {}
            if baseEventCredits:
                columns['column1'] = style.makeCreditsLabel(baseEventCredits, canBeFaded=not self.hasAnyPremium)
            if premiumEventCredits:
                columns['column3'] = style.makeCreditsLabel(premiumEventCredits, canBeFaded=self.hasAnyPremium)
            self._addStatsRow('event', **columns)
            return True
        return False

    def __addBattleResultsForStrategist(self, result):
        avatarInfo = _getAvatarInfo(result)
        baseCredits = avatarInfo['credits']
        premiumCredits = baseCredits
        baseCreditsLabel = style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium)
        premiumCreditsLabel = style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium)
        self._addStatsRow('intermediateTotal', column1=baseCreditsLabel, column3=premiumCreditsLabel)

    def __addBattleResultsForTanker(self, result):
        avatarInfo = _getAvatarInfo(result)
        baseCredits = avatarInfo['credits']
        premiumCredits = baseCredits
        baseCreditsLabel = style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium)
        premiumCreditsLabel = style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium)
        self._addStatsRow('intermediateTotal', column1=baseCreditsLabel, column3=premiumCreditsLabel)

    def __addTotalResultsForTanker(self, additionalRecords, result):
        avatarInfo = _getAvatarInfo(result)
        baseCanBeFaded = not self.hasAnyPremium and self.canResourceBeFaded
        autoCredits = additionalRecords.getRecord('autoRepairCost', 'autoLoadCredits', 'autoEquipCredits')
        totalCredits = avatarInfo['credits'] + autoCredits
        columns = {'column1': style.makeCreditsLabel(totalCredits, canBeFaded=baseCanBeFaded),
         'column3': style.makeCreditsLabel(totalCredits, canBeFaded=baseCanBeFaded)}
        self._addStatsRow('total', htmlKey='lightText', **columns)

    def __addTotalResultsForStrategist(self, result):
        avatarInfo = _getAvatarInfo(result)
        baseCredits = avatarInfo['credits']
        premiumCredits = baseCredits
        baseCreditsLabel = style.makeCreditsLabel(baseCredits, canBeFaded=not self.hasAnyPremium)
        premiumCreditsLabel = style.makeCreditsLabel(premiumCredits, canBeFaded=self.hasAnyPremium)
        self._addStatsRow('total', htmlKey='lightText', column1=baseCreditsLabel, column3=premiumCreditsLabel)


class RTSSpecialCurrencyDetailsBlock(_TotalEconomicsDetailsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(RTSSpecialCurrencyDetailsBlock, self).__init__(RTSSpecialCurrencyBlock, meta, field, *path)


class RTSSpecialCurrencyBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        if _isTanker(reusable):
            value1x7 = _getRTS1x7Currency(result)
            label = style.makeToken1x7Label(value1x7)
            self._addRecord(backport.text(R.strings.battle_results.details.calculations.rtsToken1x7()), label)
            value1x1 = _getRTS1x1Currency(result)
            label = style.makeToken1x1Label(value1x1)
            self._addRecord(backport.text(R.strings.battle_results.details.calculations.rtsToken1x1()), label)
        personalInfo = RTSPersonalInfo(result[_RECORD.PERSONAL])
        rtsLeaderboardPoints = sum((vehInfo.get('rtsLeaderPoints', 0) for _, vehInfo in personalInfo.getVehicleCDsIterator(result, reusable)))
        label = style.makeRTSLeaderboardPointsLabel(rtsLeaderboardPoints)
        self._addRecord(backport.text(R.strings.battle_results.details.calculations.rtsLeaderboardPoints()), label)
        rtsEventPoints = sum((vehInfo.get('rtsEventPoints', 0) for _, vehInfo in personalInfo.getVehicleCDsIterator(result, reusable)))
        label = style.makeRTSEventPointsLabel(rtsEventPoints)
        self._addRecord(backport.text(R.strings.battle_results.details.calculations.rtsEventPoints()), label)

    def _addRecord(self, res, value):
        self.addNextComponent(style.StatRow(res, res, style.NORMAL_SOLID_STAT_ROW, column3=value))


class GainCreditsInBattleItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        avatarInfo = _getAvatarInfo(result)
        avatarInfoCredits = avatarInfo['credits']
        return getIntegralFormat(avatarInfoCredits)


class GainCrystalInBattleItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        avatarInfo = _getAvatarInfo(result)
        crystal = avatarInfo['eventCrystal']
        return getIntegralFormat(crystal)


class TotalCrystalDetailsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        block = CrystalDetailsBlock(base.ListMeta(registered=True))
        block.setRecord(result, reusable)
        self.addNextComponent(block)


class CrystalDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        avatarInfo = _getAvatarInfo(result)
        eventCrystal = avatarInfo['eventCrystal']
        if eventCrystal > 0:
            self._addRecord(backport.text(R.strings.battle_results.details.calculations.crystal.rtsEvent()), eventCrystal)
            self.addNextComponent(style.EmptyStatRow())
            i18nText = backport.text(R.strings.battle_results.details.calculations.total())
            totalStr = makeHtmlString('html_templates:lobby/battle_results', 'lightText', {'value': i18nText})
            crystalTotal = eventCrystal
            self._addRecord(totalStr, crystalTotal)

    def _addRecord(self, res, value):
        self.addNextComponent(style.StatRow(res, res, style.NORMAL_SOLID_STAT_ROW, column3=style.makeCrystalLabel(value)))


class TotalXPDetailsBlock(_TotalEconomicsDetailsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(TotalXPDetailsBlock, self).__init__(XPDetailsBlock, meta, field, *path)


class XPDetailsBlock(_EconomicsDetailsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        avatarInfo = _getAvatarInfo(result)
        xp = avatarInfo['xp']
        eventFreeXP = avatarInfo['eventFreeXP']
        self._addRecord(backport.text(R.strings.battle_results.details.calculations.base()), xp, eventFreeXP)

    def _addRecord(self, res, xp, freeXp):
        self.addNextComponent(style.StatRow(res, res, style.WIDE_SOLID_STAT_ROW, column3=style.makeXpLabel(xp), column4=style.makeFreeXpLabel(freeXp)))


class CanBeFadedFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return False
