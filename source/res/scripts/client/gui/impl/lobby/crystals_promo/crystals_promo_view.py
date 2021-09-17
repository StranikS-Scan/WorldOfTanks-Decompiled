# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crystals_promo/crystals_promo_view.py
from constants import ARENA_BONUS_TYPE, IS_CHINA
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.app_loader.settings import APP_NAME_SPACE
from gui.impl.auxiliary.layer_monitor import LayerMonitor
from gui.impl.gen.view_models.views.lobby.crystals_promo.battle_type_model import BattleTypeModel
from gui.impl.gen.view_models.views.lobby.crystals_promo.condition_model import ConditionModel
from gui.impl.gen.view_models.views.lobby.crystals_promo.crystals_promo_view_model import CrystalsPromoViewModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.impl.gen import R
from account_helpers.AccountSettings import AccountSettings, CRYSTALS_INFO_SHOWN
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.backport.backport_system_locale import getIntegralFormat
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBonsDevicesUrl, getBonsVehiclesUrl, getBonsInstructionsUrl
from gui.shared.event_dispatcher import showShop
shopUrlsMap = {CrystalsPromoViewModel.TANKS_TAB: getBonsVehiclesUrl(),
 CrystalsPromoViewModel.EQUIPMENT_TAB: getBonsDevicesUrl(),
 CrystalsPromoViewModel.INSTRUCTIONS_TAB: getBonsInstructionsUrl()}

class CrystalsPromoView(ViewImpl):
    __slots__ = ('__visibility', '__isMarkerDisabled', '__destroyViewObject')
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID, visibility=HeaderMenuVisibilityState.ALL):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CrystalsPromoViewModel()
        super(CrystalsPromoView, self).__init__(settings)
        self.__visibility = visibility
        self.__isMarkerDisabled = False
        self.__destroyViewObject = LayerMonitor()
        app = self._appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
        if app and app.containerManager:
            markerView = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW))
            if markerView:
                self.__isMarkerDisabled = markerView.getIsMarkerDisabled()

    def _initialize(self, *args, **kwargs):
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def _onLoading(self, *args, **kwargs):
        self.__destroyViewObject.init(self.getParentWindow())
        isFirstOpen = not AccountSettings.getSettings(CRYSTALS_INFO_SHOWN)
        if isFirstOpen:
            AccountSettings.setSettings(CRYSTALS_INFO_SHOWN, True)
        with self.getViewModel().transaction() as model:
            model.setSelectedTab(1 if isFirstOpen else 0)
            model.setEquipmentPrice(getIntegralFormat(3000))
            model.setInstructionPrice(getIntegralFormat(6))
            model.setVehiclePrice(getIntegralFormat(3000))
            model.setIsChina(IS_CHINA)
            self.__updateCondition(model)
            model.goToShop += self.__goToShopHandler

    def __updateCondition(self, model):
        allRewards = self._lobbyContext.getServerSettings().getCrystalRewardConfig().getRewardInfoData()
        model.battleTypes.clearItems()
        battleTypes = model.battleTypes.getItems()
        rewards = self.__getRewards(allRewards, ARENA_BONUS_TYPE.REGULAR, 10)
        battleTypes.addViewModel(self.__getBattleType(R.strings.menu.crystals.info.tab.get.random(), R.images.gui.maps.icons.crystalsInfo.get.c_1_BLOCK(), [self.__getCondition(3, rewards.winTop3, rewards.loseTop3), self.__getCondition(rewards.topLength, rewards.winTop10, rewards.loseTop10)]))
        rewards = self.__getRewards(allRewards, ARENA_BONUS_TYPE.EPIC_RANDOM, 10)
        battleTypes.addViewModel(self.__getBattleType(R.strings.menu.crystals.info.tab.get.general(), R.images.gui.maps.icons.crystalsInfo.get.c_2_BLOCK(), [self.__getCondition(6, rewards.winTop3, rewards.loseTop3), self.__getCondition(rewards.topLength, rewards.winTop10, rewards.loseTop10)]))
        rewards = self.__getRewards(allRewards, ARENA_BONUS_TYPE.RANKED, 10)
        battleTypes.addViewModel(self.__getBattleType(R.strings.menu.crystals.info.tab.get.ranked(), R.images.gui.maps.icons.crystalsInfo.get.c_3_BLOCK(), [self.__getCondition(3, rewards.winTop3, rewards.loseTop3), self.__getCondition(rewards.topLength, rewards.winTop10, rewards.loseTop10)]))
        battleTypes.invalidate()

    def __goToShopHandler(self, args=None):
        if args is not None:
            tabIndex = args['tabIndex']
            showShop(shopUrlsMap[tabIndex])
            self.destroyWindow()
        return

    @staticmethod
    def __getRewards(allRewards, arenaType, level):
        return [ item for item in allRewards if item.arenaType is arenaType and item.level is level ][0]

    @staticmethod
    def __getBattleType(title, icon, conditions):
        newModel = BattleTypeModel()
        newModel.setTitle(title)
        newModel.setIcon(icon)
        for condition in conditions:
            newModel.conditions.addViewModel(condition)

        return newModel

    @staticmethod
    def __getCondition(position, win, defeat):
        conditions = ConditionModel()
        conditions.setPosition(position)
        conditions.setForWin(win)
        conditions.setForDefeat(defeat)
        return conditions

    def _onLoaded(self, *args, **kwargs):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def __onServerSettingsChanged(self, *_):
        with self.getViewModel().transaction() as model:
            self.__updateCondition(model)
            model.setSyncInitiator(not model.getSyncInitiator())

    def _finalize(self):
        self.__destroyViewObject.fini()
        self.viewModel.goToShop -= self.__goToShopHandler
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': self.__isMarkerDisabled}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': self.__visibility}), EVENT_BUS_SCOPE.LOBBY)

    @property
    def viewModel(self):
        return super(CrystalsPromoView, self).getViewModel()
