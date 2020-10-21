# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/congratulation_view.py
from constants import EventPackType
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.server_events.awards_formatters import getEventShopCongratsFormatter, AWARDS_SIZES
from gui.server_events.events_dispatcher import showEventShop
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import getAbsoluteUrl
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.halloween.congratulation_view_model import CongratulationViewModel
from gui.impl.gen.view_models.views.lobby.halloween.reward_model import RewardModel
from gui.impl.pub import ViewImpl
from skeletons.gui.game_event_controller import IGameEventController

class CongratulationView(ViewImpl):
    gameEventController = dependency.descriptor(IGameEventController)
    _BONUSES_ORDER = ('customizations', 'battleToken', 'premium_plus', 'goodies', 'items', 'crewBooks', 'customizations', 'tmanToken')

    def __init__(self, layoutID, packType=None):
        settings = ViewSettings(layoutID)
        settings.model = CongratulationViewModel()
        super(CongratulationView, self).__init__(settings)
        self.__layoutID = layoutID
        self.__type = packType
        self.__shop = self.gameEventController.getShop()
        self.__blur = None
        self.bonusCache = {}
        return

    @property
    def viewModel(self):
        return super(CongratulationView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            bonus = self.bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
                window.load()
                return window
        super(CongratulationView, self).createToolTip(event)

    def _initialize(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        super(CongratulationView, self)._initialize()
        self.viewModel.onClose += self.__onClose

    def _onLoading(self):
        super(CongratulationView, self)._onLoading()
        self.__blur = CachedBlur(enabled=True, ownLayer=LAYER_NAMES.WINDOWS, blurAnimRepeatCount=4)
        self.__fillViewModel()

    def _finalize(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        super(CongratulationView, self)._finalize()
        self.viewModel.onClose -= self.__onClose
        self.bonusCache = {}
        self.__blur.fini()

    def _getKeySortOrder(self, key):
        return self._BONUSES_ORDER.index(key) if key in self._BONUSES_ORDER else -1

    def _sortFunc(self, b1, b2):
        return cmp(self._getKeySortOrder(b1.bonusName), self._getKeySortOrder(b2.bonusName))

    def __fillRewards(self, rewardsModel, bonuses, isExtra=False):
        bonusIdx = 1
        for bonus in bonuses:
            reward = RewardModel()
            reward.setId(bonusIdx)
            if self.__type == EventPackType.PLAYER.value:
                reward.setDescription(bonus.userName)
            reward.setIcon(getAbsoluteUrl(bonus.getImage(AWARDS_SIZES.BIG)))
            reward.setHighlightIcon(getAbsoluteUrl(bonus.getHighlightIcon(AWARDS_SIZES.BIG)))
            reward.setOverlayIcon(getAbsoluteUrl(bonus.getOverlayIcon(AWARDS_SIZES.BIG)))
            reward.setLabelCount(bonus.label)
            tooltipId = str(self.__type) + str(bonusIdx) + str(isExtra)
            self.bonusCache[tooltipId] = bonus
            reward.setTooltipId(tooltipId)
            rewardsModel.addViewModel(reward)
            bonusIdx += 1

        rewardsModel.invalidate()

    def __onClose(self):
        self.destroyWindow()
        showEventShop()

    def __fillViewModel(self):
        shop = self.__shop
        packItem = shop.getPackItemByType(self.__type)
        formatter = getEventShopCongratsFormatter()
        bonuses = sorted(formatter.format(packItem.getBonuses()), cmp=self._sortFunc)
        extraBonuses = sorted(formatter.format(packItem.extraBonuses), cmp=self._sortFunc)
        with self.viewModel.transaction() as model:
            model.setType(self.__type)
            self.__fillRewards(model.mainRewards, bonuses)
            self.__fillRewards(model.additionRewards, extraBonuses, isExtra=True)
