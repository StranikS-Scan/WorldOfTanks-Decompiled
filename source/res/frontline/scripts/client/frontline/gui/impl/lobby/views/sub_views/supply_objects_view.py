# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/sub_views/supply_objects_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import Epic
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from epic_constants import EPIC_BATTLE_TEAM_ID
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showHangar
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IEpicBattleMetaGameController
from frontline.gui.impl.gen.view_models.views.lobby.views.supply_objects_model import SupplyType
from frontline.gui.impl.gen.view_models.views.lobby.views.supply_objects_view_model import SupplyObjectsViewModel, SupplyParamsModel, SupplyObjectsModel
from frontline.gui.params import getSupplyParameters, SUPPLY_PARAMS_KEYS, getArmorDamageFactors
_SUPPLY_HINT_SETTING_BY_ID = {SupplyType.PILLBOX: Epic.SUPPLY_PILLBOX_HINT_VIEWED,
 SupplyType.MORTAR: Epic.SUPPLY_MORTAR_HINT_VIEWED,
 SupplyType.FLAMER: Epic.SUPPLY_FLAMER_HINT_VIEWED,
 SupplyType.AIRSHIP: Epic.SUPPLY_AIRSHIP_HINT_VIEWED}
_SUPPLY_ID_BY_TYPE = {SupplyType.PILLBOX: 1,
 SupplyType.MORTAR: 2,
 SupplyType.FLAMER: 3,
 SupplyType.AIRSHIP: 4}
_SUPPLY_TYPES_BY_ID = {SupplyType.PILLBOX: 'attack1',
 SupplyType.MORTAR: 'def1',
 SupplyType.FLAMER: 'def2',
 SupplyType.AIRSHIP: 'attack2'}
_SHOW_ORDER_TUPLE = tuple(SUPPLY_PARAMS_KEYS)
_DEFAULT_SECTOR_ID = 1

class SupplyObjectsView(ViewImpl):
    __slots__ = ('__isHeaderVisible',)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __epicMetaController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, parentView):
        settings = ViewSettings(R.views.frontline.lobby.SupplyObjectsView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = SupplyObjectsViewModel()
        self.__isHeaderVisible = True
        super(SupplyObjectsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SupplyObjectsView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onSupplySelected, self.__onSupplySelected), (self.viewModel.onClose, self.__onClose))

    def _onLoading(self, *args, **kwargs):
        super(SupplyObjectsView, self)._onLoading(*args, **kwargs)
        self.__setupSupplies()

    def __setupSupplies(self):
        with self.viewModel.transaction() as vm:
            supplyArray = vm.getSupplyObjects()
            supplyArray.clear()
            for supplyId in _SUPPLY_TYPES_BY_ID:
                hintName = _SUPPLY_HINT_SETTING_BY_ID.get(supplyId, None)
                isHintViewed = AccountSettings.getEpic(hintName)
                supply = SupplyObjectsModel()
                supply.setPoint(_SUPPLY_TYPES_BY_ID.get(supplyId))
                supply.setObject(supplyId)
                supply.setIsHintShow(isHintViewed)
                supplyArray.addViewModel(supply)

            supplyArray.invalidate()
        return

    @args2params(SupplyType)
    def __onSupplySelected(self, supplyId):
        from frontline.gui.impl.lobby.views.frontline_container_view import changeHeaderVisible
        self.__disableHint()
        isVisible = supplyId == SupplyType.NONE
        changeHeaderVisible(isVisible)
        if not isVisible:
            self.__fillSupplyModel(supplyId)

    def __fillSupplyModel(self, supplyType):
        supplyID = _SUPPLY_ID_BY_TYPE.get(supplyType)
        config = self.__epicMetaController.getSupplyParams()
        vehicle = Vehicle(typeCompDescr=config[supplyID]['intCD'])
        params = getSupplyParameters(vehicle)
        if not AccountSettings.getEpic(_SUPPLY_HINT_SETTING_BY_ID[supplyType]):
            AccountSettings.setEpic(_SUPPLY_HINT_SETTING_BY_ID[supplyType], True)
            self.__setupSupplies()
        sectorProgression = self.__epicMetaController.getSectorsProgression()
        supplyTeam = EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER if supplyID in sectorProgression.attackersSupplyTypes() else EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER
        hullDamageFactor, turretDamageFactor = getArmorDamageFactors(vehicle.descriptor)
        with self.viewModel.transaction() as vm:
            vm.setSupplyHullDamageFactor(hullDamageFactor)
            vm.setSupplyTurretDamageFactor(turretDamageFactor)
            vm.setSupplyTeam(supplyTeam)
            supplyParams = vm.getSupplyParams()
            supplyParams.clear()
            for parameter in _SHOW_ORDER_TUPLE:
                for name, value in params.items():
                    if value is None or parameter != name:
                        continue
                    if name == 'turretArmor' and supplyTeam == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER:
                        continue
                    paramModel = SupplyParamsModel()
                    paramModel.setName(name)
                    paramModel.setValue(value)
                    supplyParams.addViewModel(paramModel)

            supplyParams.invalidate()
        return

    def __disableHint(self):
        settings = self.__settingsCore.serverSettings
        hint = OnceOnlyHints.EPIC_SUPPLY_INFO_HINT
        if settings.getOnceOnlyHintsSetting(hint):
            return
        settings.setOnceOnlyHintsSettings({hint: True})

    def __onClose(self):
        self.destroyWindow()
        showHangar()
