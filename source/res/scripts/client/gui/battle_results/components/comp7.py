# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/comp7.py
from constants import EntityCaptured
from fairplay_violation_types import FairplayViolations
from gui.battle_results.components import base, style
from gui.battle_results.components.vehicles import RegularVehicleStatValuesBlock, RegularVehicleStatsBlock, TeamStatsBlock, _getStunFilter
from gui.impl import backport
from gui.impl.gen.resources import R

def checkIfDeserter(reusable):
    if not reusable.personal.avatar.hasPenalties():
        return False
    penaltyName, _ = reusable.personal.avatar.getPenaltyDetails()
    return penaltyName == FairplayViolations.COMP7_DESERTER


def isQualificationBattle(avatarResults):
    return avatarResults.get('comp7QualActive', False)


class EfficiencyTitleWithSkills(base.StatsItem):

    def _convert(self, value, reusable):
        return backport.text(R.strings.battle_results.common.battleEfficiencyWithSkills.title())


class IsDeserterFlag(base.StatsItem):

    def _convert(self, result, reusable):
        if checkIfDeserter(reusable):
            if isQualificationBattle(result.get('avatar', {})):
                return backport.text(R.strings.comp7.battleResult.header.deserterQualification())
            return backport.text(R.strings.comp7.battleResult.header.deserter())


class Comp7VehicleStatsBlock(RegularVehicleStatsBlock):
    __slots__ = ('prestigePoints', 'isSuperSquad')

    def __init__(self, meta=None, field='', *path):
        super(Comp7VehicleStatsBlock, self).__init__(meta, field, *path)
        self.prestigePoints = 0
        self.isSuperSquad = False

    def setRecord(self, result, reusable):
        super(Comp7VehicleStatsBlock, self).setRecord(result, reusable)
        self.prestigePoints = result.prestigePoints
        avatar = reusable.avatars.getAvatarInfo(result.player.dbID)
        self.isSuperSquad = avatar.extensionInfo.get('isSuperSquad', False)


class Comp7TeamStatsBlock(TeamStatsBlock):
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(Comp7TeamStatsBlock, self).__init__(Comp7VehicleStatsBlock, meta, field, *path)


class Comp7VehicleStatValuesBlock(RegularVehicleStatValuesBlock):
    __slots__ = ('damageDealtBySkills', 'healed', 'capturedPointsOfInterest', 'roleSkillUsed')

    def setRecord(self, result, reusable):
        super(Comp7VehicleStatValuesBlock, self).setRecord(result, reusable)
        poiCaptured = result.entityCaptured
        self.damageDealtBySkills = style.getIntegralFormatIfNoEmpty(result.equipmentDamageDealt)
        self.healed = (result.healthRepair, result.alliedHealthRepair)
        self.capturedPointsOfInterest = style.getIntegralFormatIfNoEmpty(poiCaptured.get(EntityCaptured.POI_CAPTURABLE, 0))
        self.roleSkillUsed = style.getIntegralFormatIfNoEmpty(result.roleSkillUsed)


class AllComp7VehicleStatValuesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        isPersonal, iterator = result
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for vehicle in iterator:
            block = Comp7VehicleStatValuesBlock()
            block.setPersonal(isPersonal)
            block.addFilters(stunFilter)
            block.setRecord(vehicle, reusable)
            add(block)


class PersonalVehiclesComp7StatsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        add = self.addNextComponent
        stunFilter = _getStunFilter()
        for data in info.getVehiclesIterator():
            block = Comp7VehicleStatValuesBlock()
            block.setPersonal(True)
            block.addFilters(stunFilter)
            block.setRecord(data, reusable)
            add(block)
