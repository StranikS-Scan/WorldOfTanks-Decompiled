# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/widgets/frontman_widget.py
import typing
import HBAccountSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbDispatcherProperty
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.common.ability_model import AbilityModel
from historical_battles.gui.impl.gen.view_models.views.lobby.base_frontman_model import BaseFrontmanModel, FrontmanState, FrontmanRole
from historical_battles.gui.impl.gen.view_models.views.lobby.hangar_view_model import HangarViewModel
from historical_battles.polygons_config import PolygonsConfigReader
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import FrontmanRoleID, AccountSettingsKeys, FRONTMAN_PROGRESS_QUEST_PREFIX_TPL
from items import vehicles
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from historical_battles.gui.server_events.game_event.frontman_item import FrontmanItem
FrontmanRoleIDToRole = {FrontmanRoleID.AVIATION: FrontmanRole.AVIATION,
 FrontmanRoleID.ARTILLERY: FrontmanRole.ARTILLERY,
 FrontmanRoleID.ENGINEER: FrontmanRole.ENGINEER}

class FrontmanWidget(object):
    __slots__ = ('__viewModel', '__frontmanPolygons')
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel):
        self.__viewModel = viewModel
        self.__frontmanPolygons = PolygonsConfigReader.readXml(PolygonsConfigReader.FRONTMANS_PATH)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onLoading(self):
        self.__viewModel.onVehicleChange += self.__onVehicleChange

    def destroy(self):
        self.__viewModel.onVehicleChange -= self.__onVehicleChange

    def updateModel(self, model):
        selectedFrontman = self._gameEventController.frontController.getSelectedFrontman()
        if not selectedFrontman:
            return
        frontmanModel = self.__getSelectedFrontmanModel(model)
        self.__fillVehicleInfo(frontmanModel, selectedFrontman, True)

    def createFrontmanModel(self, frontman):
        if frontman.getSelectedVehicle() is None:
            return
        else:
            frontmanModel = BaseFrontmanModel()
            self.__fillFrontmanInfo(frontmanModel, frontman)
            selectedFrontmanID = self._gameEventController.frontController.getSelectedFrontmanID()
            self.__fillVehicleInfo(frontmanModel, frontman, frontman.getID() == selectedFrontmanID)
            self.__fillAbilities(frontmanModel, frontman)
            self.__fillProgressInfo(frontmanModel, frontman)
            return frontmanModel

    def updateFrontmanVehicle(self, model):
        selectedFrontman = self._gameEventController.frontController.getSelectedFrontman()
        selectedFrontmanModel = self.__getSelectedFrontmanModel(model)
        self.__fillVehicleInfo(selectedFrontmanModel, selectedFrontman, True)

    @staticmethod
    def __createAbilityModel(abilityId, iconName):
        ability = AbilityModel()
        ability.setId(abilityId)
        ability.setIconName(iconName)
        return ability

    def __onVehicleChange(self):
        frontmanModel = self.__getSelectedFrontmanModel(self.__viewModel)
        if frontmanModel.getHasNewVehicle():
            frontmanModel.setHasNewVehicle(False)
            self.__setViewedVehicle(frontmanModel.vehicle.getId())
        self._gameEventController.frontController.changeSelectedFrontmanVehicle()

    def __fillFrontmanInfo(self, frontmanModel, frontman):
        frontmanID = int(frontman.getID())
        frontmanModel.setId(frontmanID)
        frontmanModel.setRole(FrontmanRoleIDToRole.get(frontman.getRoleID(), FrontmanRole.AVIATION))
        frontmanModel.setState(self.__getFrontmanState(frontman))
        frontmanModel.setPolygon(self.__frontmanPolygons.getPolygon(self._gameEventController.frontController.getSelectedFrontmanID()))

    def __fillVehicleInfo(self, frontmanModel, frontman, isSelectedFrontman=False):
        vehicle = frontman.getSelectedVehicle()
        curVehIsProfiled = frontman.getIsProfiledVehicle()
        frontmanModel.vehicle.setId(vehicle.intCD)
        frontmanModel.vehicle.setType(vehicle.type)
        frontmanModel.vehicle.setName(vehicle.userName)
        frontmanModel.setCanSwitchVehicle(self._gameEventController.canVehicleStartToBattle(vehicle.intCD))
        frontmanModel.setIsProfiledVehicle(curVehIsProfiled)
        if isSelectedFrontman:
            heroVehicle = frontman.getHeroVehicle()
            if heroVehicle.invID >= 0 and not self.__checkIsViewedVehicle(heroVehicle.intCD):
                if curVehIsProfiled:
                    frontmanModel.setHasNewVehicle(True)
                else:
                    self.__setViewedVehicle(heroVehicle.intCD)

    @staticmethod
    def __checkIsViewedVehicle(intCD):
        vehSettings = HBAccountSettings.getSettings(AccountSettingsKeys.VIEWED_VEHICLES)
        return vehSettings.get(intCD, -1) > 0

    @staticmethod
    def __setViewedVehicle(intCD):
        vehSettings = HBAccountSettings.getSettings(AccountSettingsKeys.VIEWED_VEHICLES)
        vehSettings[intCD] = True
        HBAccountSettings.setSettings(AccountSettingsKeys.VIEWED_VEHICLES, vehSettings)

    @staticmethod
    def __fillProgressInfo(frontmanModel, frontman):
        roleAbilityID = frontman.getRoleAbility()
        roleAbility = vehicles.g_cache.equipments()[roleAbilityID]
        frontmanModel.setPerkName(roleAbility.iconName)
        frontmanModel.setPerkId(roleAbilityID)
        roleQuest = frontman.roleQuest
        roleName = roleAbility.userString
        roleDescr = roleAbility.description
        frontmanModel.progress.setNameRole(roleName)
        frontmanModel.progress.setDescriptionRole(roleDescr)
        frontmanModel.progress.setNameQuest(backport.text(R.strings.hb_lobby.hangar.frontmanWidget.questHeader()))
        frontmanModel.progress.setDescriptionQuest(backport.text(R.strings.hb_lobby.quest.dyn(FRONTMAN_PROGRESS_QUEST_PREFIX_TPL.format(frontman.getID()))()))
        frontmanModel.progress.setMaxProgress(roleQuest.getMaxProgress())
        frontmanModel.progress.setIsCompleted(frontman.hasRole())
        frontmanModel.progress.setCurrentProgress(roleQuest.getCurrentProgress())

    def __getSelectedFrontmanModel(self, hangarModel):
        selectedFrontman = self._gameEventController.frontController.getSelectedFrontman()
        selectedFrontmanModel = next((item for item in hangarModel.getFrontmen() if item.getId() == selectedFrontman.getID()))
        return selectedFrontmanModel

    def __onAnimationCompleted(self):
        selectedFrontman = self._gameEventController.frontController.getSelectedFrontman()
        frontmanID = selectedFrontman.getID()
        progress = selectedFrontman.roleQuest.getCurrentProgress()
        progressSettings = HBAccountSettings.getSettings(AccountSettingsKeys.FRONTMEN_PREVIOUS_PROGRESS)
        progressSettings[frontmanID] = progress
        HBAccountSettings.setSettings(AccountSettingsKeys.FRONTMEN_PREVIOUS_PROGRESS, progressSettings)

    def __fillAbilities(self, frontmanModel, frontman):
        abilities = frontmanModel.getAbilities()
        abilities.clear()
        for abilityID in frontman.getSelectedVehicleAbilities():
            ability = vehicles.g_cache.equipments()[abilityID]
            abilities.addViewModel(self.__createAbilityModel(abilityID, ability.iconName))

        abilities.invalidate()

    @staticmethod
    def __getFrontmanState(frontman):
        if frontman.isInBattle():
            return FrontmanState.INBATTLE
        return FrontmanState.INPLATOON if frontman.isInUnit() else FrontmanState.DEFAULT
