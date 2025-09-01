# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crystals_promo/crystals_promo_view.py
from account_helpers.AccountSettings import AccountSettings, CRYSTALS_INFO_SHOWN
from constants import ARENA_BONUS_TYPE, IS_CHINA
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBonsDevicesUrl, getBonsVehiclesUrl, getBonsInstructionsUrl
from gui.impl.backport.backport_system_locale import getIntegralFormat
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crystals_promo.condition_model import ConditionModel
from gui.impl.gen.view_models.views.lobby.crystals_promo.crystals_promo_view_model import CrystalsPromoViewModel
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from gui.shop import showIngameShop, Origin
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency, server_settings
from shared_utils import findFirst
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
_DEFAULT_VEHICLE_PRICE = 1500
_DEFAULT_EQUIPMENT_PRICE = 3000
_DEFAULT_INSTRUCTION_PRICE = 6
_DEFAULT_LEVEL = 10

class CrystalsPromoView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('__destroyViewObject', '__shopUrlsMap')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID):
        self.__shopUrlsMap = {}
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=CrystalsPromoViewModel())
        super(CrystalsPromoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrystalsPromoView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(CrystalsPromoView, self)._initialize()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.viewModel.goToShop += self.__goToShopHandler
        self.__shopUrlsMap = {CrystalsPromoViewModel.TANKS_TAB: getBonsVehiclesUrl(),
         CrystalsPromoViewModel.EQUIPMENT_TAB: getBonsDevicesUrl(),
         CrystalsPromoViewModel.INSTRUCTIONS_TAB: getBonsInstructionsUrl()}

    def _onLoading(self, *args, **kwargs):
        super(CrystalsPromoView, self)._onLoading(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)
        isFirstOpen = not AccountSettings.getSettings(CRYSTALS_INFO_SHOWN)
        if isFirstOpen:
            AccountSettings.setSettings(CRYSTALS_INFO_SHOWN, True)
        with self.getViewModel().transaction() as model:
            model.setSelectedTab(1 if isFirstOpen else 0)
            model.setEquipmentPrice(getIntegralFormat(_DEFAULT_EQUIPMENT_PRICE))
            model.setInstructionPrice(getIntegralFormat(_DEFAULT_INSTRUCTION_PRICE))
            model.setVehiclePrice(getIntegralFormat(_DEFAULT_VEHICLE_PRICE))
            model.setIsChina(IS_CHINA)
            self.__updateCondition(model)

    def _onLoaded(self, *args, **kwargs):
        super(CrystalsPromoView, self)._onLoaded(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        self.viewModel.goToShop -= self.__goToShopHandler
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.resumeLobbyHeader(self.uniqueID)
        super(CrystalsPromoView, self)._finalize()

    def __updateCondition(self, model):
        config = self.__lobbyContext.getServerSettings().getCrystalRewardConfig().getRewardInfoData()
        randomItem = findFirst(lambda i: i.arenaType == ARENA_BONUS_TYPE.REGULAR and i.level == _DEFAULT_LEVEL, config)
        if randomItem is not None:
            self.__fillBattleItemModel(model.battleType, randomItem, 'random')
        return

    @server_settings.serverSettingsChangeListener('crystal_rewards_config')
    def __onServerSettingsChanged(self, *_):
        with self.getViewModel().transaction() as model:
            self.__updateCondition(model)
            model.setSyncInitiator(not model.getSyncInitiator())

    def __goToShopHandler(self, args=None):
        if args is not None:
            tabIndex = args['tabIndex']
            showIngameShop(self.__shopUrlsMap[tabIndex], Origin.HANGAR_BONS_SCREEN)
            self.destroyWindow()
        return

    @classmethod
    def __fillBattleItemModel(cls, model, item, bonusTypeLabel):
        conditions = [cls.__createConditionModel(item.firstTopLength, item.winTop3, item.loseTop3), cls.__createConditionModel(item.topLength, item.winTop10, item.loseTop10)]
        model.setTitle(R.strings.menu.crystals.info.tab.get.dyn(bonusTypeLabel)())
        model.setIcon(R.images.gui.maps.icons.crystalsInfo.get.dyn(bonusTypeLabel)())
        model.conditions.clearItems()
        for condition in conditions:
            model.conditions.addViewModel(condition)

        model.conditions.invalidate()

    @staticmethod
    def __createConditionModel(position, win, defeat):
        conditions = ConditionModel()
        conditions.setPosition(position)
        conditions.setForWin(win)
        conditions.setForDefeat(defeat)
        return conditions
