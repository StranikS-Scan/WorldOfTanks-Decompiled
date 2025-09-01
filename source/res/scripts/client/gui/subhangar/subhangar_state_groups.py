# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/subhangar/subhangar_state_groups.py
from enum import Enum

class CameraMover(object):

    def moveCamera(self, cameraManager, cameraName):
        cameraManager.switchByCameraName(cameraName)


class SubhangarStateGroupConfig(object):

    def __init__(self, stateGroups=(), cameraMover=CameraMover()):
        self.stateGroups = stateGroups
        self.cameraMover = cameraMover


class SubhangarStateGroupConfigProvider(object):

    def getSubhangarStateGroupConfig(self):
        raise NotImplementedError


class SubhangarStateGroups(Enum):
    Customization = 'CustomizationStates'
    PersonalMissions = 'PersonalMissionsStates'
    VehicleHub = 'VehicleHubStates'
    VehicleHubOverviewLargeTank = 'VehicleHubOverviewLargeTankStates'
    VehicleHubModulesLargeTank = 'VehicleHubModulesLargeTankStates'
    VehicleHubUpgradesLargeTank = 'VehicleHubUpgradesLargeTankStates'
    VehicleHubArmorLargeTank = 'VehicleHubArmorLargeTankStates'
    VehicleHubStatsLargeTank = 'VehicleHubStatsLargeTankStates'
    VehicleHubOverviewMediumTank = 'VehicleHubOverviewMediumTankStates'
    VehicleHubModulesMediumTank = 'VehicleHubModulesMediumTankStates'
    VehicleHubUpgradesMediumTank = 'VehicleHubUpgradesMediumTankStates'
    VehicleHubStatsMediumTank = 'VehicleHubStatsMediumTankStates'
    VehicleHubArmorMediumTank = 'VehicleHubArmorMediumTankStates'
    VehicleHubOverviewSmallTank = 'VehicleHubOverviewSmallTankStates'
    VehicleHubModulesSmallTank = 'VehicleHubModulesSmallTankStates'
    VehicleHubUpgradesSmallTank = 'VehicleHubUpgradesSmallTankStates'
    VehicleHubStatsSmallTank = 'VehicleHubStatsSmallTankStates'
    VehicleHubArmorSmallTank = 'VehicleHubArmorSmallTankStates'
    PostBattleSmall = 'PostBattleSmallStates'
    PostBattleMedium = 'PostBattleMediumStates'
    PostBattleLarge = 'PostBattleLargeStates'
    PostBattleVictory = 'PostBattleVictoryStates'
    PostBattleDefeat = 'PostBattleDefeatStates'
    PostBattleCommon = 'PostBattleCommonStates'
