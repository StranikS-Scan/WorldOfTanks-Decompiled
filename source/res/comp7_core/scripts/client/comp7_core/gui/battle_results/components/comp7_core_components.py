# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/battle_results/components/comp7_core_components.py
from constants import EntityCaptured
from gui.battle_results.components import base, style
from gui.battle_results.components.vehicles import RegularVehicleStatValuesBlock, RegularVehicleStatsBlock, TeamStatsBlock, _getStunFilter
from gui.impl import backport
from gui.impl.gen.resources import R

def checkIfDeserter(reusable, fairplayViolation):
    if not reusable.personal.avatar.hasPenalties():
        return False
    penaltyName, _ = reusable.personal.avatar.getPenaltyDetails()
    return penaltyName == fairplayViolation


class EfficiencyTitleWithSkills(base.StatsItem):

    def _convert(self, value, reusable):
        return backport.text(R.strings.battle_results.common.battleEfficiencyWithSkills.title())


class IsDeserterFlag(base.StatsItem):

    def _convert(self, result, reusable):
        raise NotImplementedError


class Comp7CoreVehicleStatsBlock(RegularVehicleStatsBlock):
    __slots__ = ('prestigePoints', 'isSuperSquad')

    def __init__(self, meta=None, field='', *path):
        super(Comp7CoreVehicleStatsBlock, self).__init__(meta, field, *path)
        self.prestigePoints = 0
        self.isSuperSquad = False

    def setRecord(self, result, reusable):
        super(Comp7CoreVehicleStatsBlock, self).setRecord(result, reusable)
        self.prestigePoints = result.prestigePoints
        avatar = reusable.avatars.getAvatarInfo(result.player.dbID)
        self.isSuperSquad = avatar.extensionInfo.get('isSuperSquad', False)


class Comp7CoreTeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(Comp7CoreTeamStatsBlock, self).__init__(Comp7CoreVehicleStatsBlock, meta, field, *path)


class Comp7CoreVehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('damageDealtBySkills', 'healed', 'capturedPointsOfInterest', 'roleSkillUsed')

    def setRecord(self, result, reusable):
        super(Comp7CoreVehicleStatValuesBlock, self).setRecord(result, reusable)
        poiCaptured = result.entityCaptured
        self.damageDealtBySkills = style.getIntegralFormatIfNoEmpty(result.equipmentDamageDealt)
        self.healed = (result.healthRepair, result.alliedHealthRepair)
        self.capturedPointsOfInterest = style.getIntegralFormatIfNoEmpty(poiCaptured.get(EntityCaptured.POI_CAPTURABLE, 0))
        self.roleSkillUsed = style.getIntegralFormatIfNoEmpty(result.roleSkillUsed)


class AllComp7CoreVehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPersonal, iterator = result
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for vehicle in iterator:
            block = Comp7CoreVehicleStatValuesBlock()
            block.setPersonal(isPersonal)
            block.addFilters(stunFilter)
            block.setRecord(vehicle, reusable)
            add(block)


class PersonalVehiclesComp7CoreStatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for data in info.getVehiclesIterator():
            block = Comp7CoreVehicleStatValuesBlock()
            block.setPersonal(True)
            block.addFilters(stunFilter)
            block.setRecord(data, reusable)
            add(block)
