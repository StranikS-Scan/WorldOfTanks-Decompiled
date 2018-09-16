# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/personalreserves/boosters_view.py
from operator import attrgetter
from adisp import process
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyBoostersUrl
from gui.Scaleform.daapi.view.meta.StorageCategoryPersonalReservesViewMeta import StorageCategoryPersonalReservesViewMeta
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS as BC
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.goodies.goodie_items import BOOSTERS_ORDERS, BOOSTER_QUALITY_NAMES, MAX_ACTIVE_BOOSTERS_COUNT
from gui.shared.event_dispatcher import showWebShop
from gui.shared.formatters import text_styles, getItemPricesVO
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.utils import decorators
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency, int2roman
from helpers.i18n import makeString as _ms
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IBoostersController

class StorageCategoryPersonalReservesView(StorageCategoryPersonalReservesViewMeta):
    _QUALITY_TO_LEVEL = {BOOSTER_QUALITY_NAMES.SMALL: 1,
     BOOSTER_QUALITY_NAMES.MEDIUM: 2,
     BOOSTER_QUALITY_NAMES.BIG: 3}
    boosters = dependency.descriptor(IBoostersController)
    eventsCache = dependency.descriptor(IEventsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        super(StorageCategoryPersonalReservesView, self).__init__()
        self._boosters = []
        self.__activeBoostersCount = 0

    def navigateToStore(self):
        showWebShop(getBuyBoostersUrl())

    @process
    def activateReserve(self, boosterID):
        newBooster = self.goodiesCache.getBooster(boosterID)
        curBooster = self.__getActiveBoosterByType(newBooster.boosterType)
        shouldActivated = False
        if curBooster is None:
            shouldActivated |= (yield self.__canActivate(newBooster.description))
        else:
            shouldActivated |= (yield self.__canReplace(curBooster.description, newBooster.description))
        if shouldActivated:
            self.__activateBoosterRequest(newBooster)
        return

    def __canActivate(self, newBoosterDescription):
        return DialogsInterface.showDialog(I18nConfirmDialogMeta(BC.BOOSTER_ACTIVATION_CONFORMATION_TEXT_KEY, messageCtx={'newBoosterName': text_styles.middleTitle(newBoosterDescription)}, focusedID=DIALOG_BUTTON_ID.CLOSE))

    def __canReplace(self, curBoosterDescription, newBoosterDescription):
        return DialogsInterface.showDialog(I18nConfirmDialogMeta(BC.BOOSTER_REPLACE_CONFORMATION_TEXT_KEY, messageCtx={'newBoosterName': text_styles.middleTitle(newBoosterDescription),
         'curBoosterName': text_styles.middleTitle(curBoosterDescription)}, focusedID=DIALOG_BUTTON_ID.CLOSE))

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StorageCategoryPersonalReservesView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BOOSTERS_PANEL:
            viewPy.setSlotProps({'slotsCount': MAX_ACTIVE_BOOSTERS_COUNT,
             'slotWidth': 50,
             'paddings': 64,
             'groupPadding': 18,
             'ySlotPosition': 5,
             'offsetSlot': -2,
             'useOnlyLeftBtn': True})

    def _populate(self):
        super(StorageCategoryPersonalReservesView, self)._populate()
        g_clientUpdateManager.addCallbacks({'goodies': self.__onUpdateBoosters,
         'shop': self.__onUpdateBoosters})
        self.boosters.onBoosterChangeNotify += self.__onUpdateBoosters
        self.eventsCache.onSyncCompleted += self.__onQuestsUpdate
        self.__onUpdateBoosters()
        self.__updateActiveBoostersCount()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.boosters.onBoosterChangeNotify -= self.__onUpdateBoosters
        self.eventsCache.onSyncCompleted -= self.__onQuestsUpdate
        super(StorageCategoryPersonalReservesView, self)._dispose()

    def _update(self, *args):
        self.__onUpdateBoosters()

    def __onUpdateBoosters(self, *args):
        self.__updateActiveBoostersCount()
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT | REQ_CRITERIA.BOOSTER.ENABLED
        boosters = self.goodiesCache.getBoosters(criteria=criteria).values()
        if boosters:
            dataProviderValues = []
            for booster in sorted(boosters, cmp=self.__sort):
                mainText = text_styles.main(booster.getBonusDescription(valueFormatter=text_styles.neutral))
                romanLvl = self._QUALITY_TO_LEVEL.get(booster.quality)
                vo = createStorageDefVO(booster.boosterID, mainText, mainText, booster.count, getItemPricesVO(booster.getSellPrice())[0], booster.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL), booster.getShopIcon(), 'altimage', enabled=booster.isReadyToActivate, level=int2roman(romanLvl) if romanLvl is not None else '')
                dataProviderValues.append(vo)

            self._dataProvider.buildList(*dataProviderValues)
        else:
            self.as_showDummyScreenS(True)
        return

    def __onQuestsUpdate(self, *args):
        self.__onUpdateBoosters()

    def __sort(self, a, b):
        return cmp(a.quality, b.quality) or cmp(BOOSTERS_ORDERS[a.boosterType], BOOSTERS_ORDERS[b.boosterType]) or cmp(b.effectValue, a.effectValue) or cmp(b.effectTime, a.effectTime)

    @classmethod
    def __getActiveBoosterByType(cls, bType):
        criteria = REQ_CRITERIA.BOOSTER.ACTIVE | REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([bType])
        activeBoosters = cls.goodiesCache.getBoosters(criteria=criteria).values()
        return max(activeBoosters, key=attrgetter('effectValue')) if activeBoosters else None

    @decorators.process('loadStats')
    def __activateBoosterRequest(self, booster):
        result = yield BoosterActivator(booster).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __updateActiveBoostersCount(self):
        activeBoostersCount = len(self.goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values())
        totalBoostersCount = sum((x.count for x in self.goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_ACCOUNT).values()))
        self.as_initS({'activeText': text_styles.main(_ms(STORAGE.PERSONALRESERVES_ACTIVECOUNTLABEL, activeCount=text_styles.error(activeBoostersCount) if activeBoostersCount == 0 else text_styles.stats(activeBoostersCount), totalCount=MAX_ACTIVE_BOOSTERS_COUNT)),
         'totalText': text_styles.main(_ms(STORAGE.PERSONALRESERVES_TOTALCOUNTLABEL, totalCount=text_styles.error(totalBoostersCount) if totalBoostersCount == 0 else text_styles.stats(totalBoostersCount))),
         'hasActiveReserve': activeBoostersCount != 0})
