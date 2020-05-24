# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/offers/offer_banner_window.py
import BigWorld
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.offers.offer_banner_model import OfferBannerModel
from gui.impl.lobby.offers import getGfImagePath
from gui.shared.event_dispatcher import showOfferGiftsWindow
from helpers import dependency, getClientLanguage, isPlayerAccount
import ResMgr
from gui.impl.pub import ViewImpl, WindowImpl
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider

class OfferBannerWindowView(ViewImpl):
    _offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, offerID):
        settings = ViewSettings(layoutID=R.views.lobby.offers.OfferBannerWindow(), flags=ViewFlags.WINDOW_DECORATOR, model=OfferBannerModel())
        super(OfferBannerWindowView, self).__init__(settings)
        self._offerID = offerID
        self._langCode = getClientLanguage()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        super(OfferBannerWindowView, self)._initialize()
        self.viewModel.onSelect += self._onSelect
        self.viewModel.onClose += self._onClose
        g_playerEvents.onAccountBecomeNonPlayer += self.destroyWindow

    def _finalize(self):
        super(OfferBannerWindowView, self)._finalize()
        self.viewModel.onSelect -= self._onSelect
        self.viewModel.onClose -= self._onClose
        g_playerEvents.onAccountBecomeNonPlayer -= self.destroyWindow

    def _onLoading(self, *args, **kwargs):
        super(OfferBannerWindowView, self)._onLoading(*args, **kwargs)
        offer = self._offersProvider.getOffer(self._offerID)
        if offer is None:
            return
        else:
            localization = ResMgr.openSection(self._offersProvider.getCdnResourcePath(offer.cdnLocFilePath, relative=False))
            with self.viewModel.transaction() as model:
                model.setTitle(R.strings.offers.banner.title())
                model.setName(localization.readString('nameInBanner', default=''))
                model.setIcon(getGfImagePath(self._offersProvider.getCdnResourcePath(offer.cdnBannerLogoPath, relative=True)))
            return

    def _onSelect(self):
        if isPlayerAccount():
            BigWorld.player().setOfferBannerSeen(self._offerID)
        showOfferGiftsWindow(self._offerID)
        self.destroyWindow()

    def _onClose(self):
        if isPlayerAccount():
            BigWorld.player().setOfferBannerSeen(self._offerID)


class OfferBannerWindow(WindowImpl):
    _appLoader = dependency.descriptor(IAppLoader)
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _loaded = set()

    def __init__(self, offerID, controller):
        super(OfferBannerWindow, self).__init__(WindowFlags.WINDOW, content=OfferBannerWindowView(offerID), parent=None, areaID=R.areas.default())
        self.offerID = offerID
        self.controller = controller
        self._loaded.add(self.offerID)
        return

    @property
    def serverSettings(self):
        return self._lobbyContext.getServerSettings()

    @classmethod
    def isLoaded(cls, offerID):
        return offerID in OfferBannerWindow._loaded

    @classmethod
    def tryLoad(cls, offerID, controller):
        if not cls.isLoaded(offerID):
            window = cls(offerID, controller)
            window.load()
            window.center()

    def _initialize(self):
        super(OfferBannerWindow, self)._initialize()
        self._appLoader.onGUISpaceLeft += self._updateVisibility
        self._offersProvider.onOffersUpdated += self._onOffersUpdated
        self.serverSettings.onServerSettingsChange += self._updateVisibility
        self.controller.onShowBanners += self.show
        self.controller.onHideBanners += self.hide
        if not self.controller.isEnabled():
            self.hide()

    def _finalize(self):
        super(OfferBannerWindow, self)._finalize()
        self._appLoader.onGUISpaceLeft -= self._updateVisibility
        self._offersProvider.onOffersUpdated -= self._onOffersUpdated
        self.serverSettings.onServerSettingsChange -= self._updateVisibility
        self.controller.onShowBanners -= self.show
        self.controller.onHideBanners -= self.hide
        if self.offerID in self._loaded:
            self._loaded.remove(self.offerID)
        self.controller = None
        return

    def _onOffersUpdated(self):
        offer = self._offersProvider.getOffer(self.offerID)
        if offer is None or not offer.showBanner or not offer.isOfferAvailable or self._offersProvider.isBannerSeen(offer.id):
            self.destroy()
        return

    def _updateVisibility(self, *args, **kwargs):
        if not self.controller.isEnabled():
            self.destroy()
        elif self.isHidden():
            self.show()
