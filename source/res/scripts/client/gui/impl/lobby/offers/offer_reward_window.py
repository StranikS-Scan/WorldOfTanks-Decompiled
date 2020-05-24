# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/offers/offer_reward_window.py
import logging
import shared_utils
from PlayerEvents import g_playerEvents
from gui.impl.auxiliary.rewards_helper import getRewardsBonuses
from gui.impl.backport import TooltipData, BackportTooltipWindow
from gui.impl.lobby.offers import getGfImagePath
from gui.shared.event_dispatcher import showOfferGiftsWindow
from gui.shared.utils.functions import stripAllTags
from helpers import dependency
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen.view_models.views.lobby.offers.offer_reward_model import OfferRewardModel
from gui.impl.pub import ViewImpl
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
_logger = logging.getLogger(__name__)

class OfferRewardWindow(ViewImpl):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, layoutID, offerID, giftID, cdnTitle='', cdnDescription='', cdnIcon=''):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.TOP_WINDOW_VIEW, model=OfferRewardModel())
        super(OfferRewardWindow, self).__init__(settings)
        self._offer = self._offersProvider.getOffer(offerID)
        self._gift = self._offer.getGift(giftID)
        self._cdnTitle = cdnTitle
        self._cdnDescription = cdnDescription
        self._cdnIcon = cdnIcon
        self._tooltipData = None
        return

    def createToolTip(self, event):
        if not self._gift.fromCdn:
            if self._tooltipData is not None:
                window = BackportTooltipWindow(self._tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(OfferRewardWindow, self).createToolTip(event)

    @property
    def _viewModel(self):
        return self.getViewModel()

    @property
    def _serverSettings(self):
        return self._lobbyContext.getServerSettings()

    def _initialize(self, *args, **kwargs):
        super(OfferRewardWindow, self)._initialize()
        self._viewModel.onAccept += self._onClose
        self._viewModel.onClose += self._onClose
        g_playerEvents.onAccountBecomeNonPlayer += self.destroyWindow

    def _finalize(self):
        super(OfferRewardWindow, self)._finalize()
        self._viewModel.onAccept -= self._onClose
        self._viewModel.onClose -= self._onClose
        g_playerEvents.onAccountBecomeNonPlayer -= self.destroyWindow

    def _onLoading(self, *args, **kwargs):
        super(OfferRewardWindow, self)._onLoading(*args, **kwargs)
        with self._viewModel.transaction() as model:
            if self._gift.fromCdn:
                title = self._cdnTitle
                description = self._cdnDescription
                icon = self._cdnIcon
            else:
                title = self._gift.title
                description = self._gift.description
                icon = ''
                bonusData = self._gift.bonus.displayedBonusData if self._gift.bonus else {}
                formattedBonuses = getRewardsBonuses(bonusData)
                formattedBonus = shared_utils.first(formattedBonuses)
                if formattedBonus is not None:
                    icon = getGfImagePath(formattedBonus.get('imgSource'))
                    self._tooltipData = TooltipData(tooltip=formattedBonus.get('tooltip', None), isSpecial=formattedBonus.get('isSpecial', False), specialAlias=formattedBonus.get('specialAlias', ''), specialArgs=formattedBonus.get('specialArgs', None))
                model.setCount(self._gift.giftCount)
                model.setHightlightType(self._gift.highlight)
            model.setName(title)
            model.setIcon(icon)
            model.setTooltipTitle(stripAllTags(title))
            model.setTooltipDescription(stripAllTags(description))
            bonusType = self._gift.bonusType
            if bonusType is not None:
                model.setBonusType(bonusType)
        return

    def _onClose(self):
        self.destroyWindow()
        if self._offer.isOfferAvailable and self._gift.isVehicle and self._serverSettings.isOffersEnabled():
            showOfferGiftsWindow(self._offer.id)
