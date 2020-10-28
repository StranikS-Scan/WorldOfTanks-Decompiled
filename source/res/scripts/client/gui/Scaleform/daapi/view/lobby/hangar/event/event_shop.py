# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_shop.py
import GUI
from constants import EventPackType
from gui.Scaleform import MENU
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers.time_utils import getTimeStructInLocal
from gui.Scaleform.daapi.view.lobby.hangar.event.event_confirmation import EventConfirmationCloser
from gui.Scaleform.daapi.view.meta.EventShopTabMeta import EventShopTabMeta
from gui.shared.formatters.text_styles import eventPackBought
from gui.server_events.awards_formatters import getEventPackIntroAwardFormatter
from helpers import dependency, i18n
from gui.impl.gen import R
from gui.impl import backport
from gui.server_events.events_dispatcher import showEventHangar
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from skeletons.gui.game_event_controller import IGameEventController
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings

class EventShopTab(EventShopTabMeta, EventConfirmationCloser):
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=VIEW_ALIAS.EVENT_SHOP, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_halloween_2019_hangar_metagame_music_shop', exitEvent='ev_halloween_2019_hangar_metagame_music_base')
    _BONUSES_ORDER = ('premium', 'goodies', 'battleToken')

    def __init__(self, *args, **kwargs):
        super(EventShopTab, self).__init__(*args, **kwargs)
        self.__shop = self.gameEventController.getShop()
        self.__blur = GUI.WGUIBackgroundBlur()

    def closeView(self):
        showEventHangar()

    def onMainBannerClick(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_STYLES_SHOP_PREVIEW), ctx={'itemIndex': 0}), scope=EVENT_BUS_SCOPE.LOBBY)

    def onPackBannerClick(self, index):
        viewAlias = VIEW_ALIAS.EVENT_PLAYER_PACK_CONFIRMATION if index == EventPackType.PLAYER.value else VIEW_ALIAS.EVENT_ITEM_PACK_CONFIRMATION
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(viewAlias), ctx={'index': index}), EVENT_BUS_SCOPE.LOBBY)

    def onItemsBannerClick(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_ITEMS_FOR_TOKENS)), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(EventShopTab, self)._populate()
        self.__blur.enable = True
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.gameEventController.getShop().onShopUpdated += self._onShopUpdated
        self._updateShop()

    def _dispose(self):
        self.__blur.enable = False
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.gameEventController.getShop().onShopUpdated -= self._onShopUpdated
        super(EventShopTab, self)._dispose()

    def _onShopUpdated(self):
        self._updateShop()

    def _getKeySortOrder(self, key):
        return self._BONUSES_ORDER.index(key) if key in self._BONUSES_ORDER else -1

    def _sortFunc(self, b1, b2):
        return cmp(self._getKeySortOrder(b1.bonusName), self._getKeySortOrder(b2.bonusName))

    def _getRewards(self, item):
        bonuses = getEventPackIntroAwardFormatter().format(item.getBonuses())
        rewards = [ {'name': bonus.userName,
         'count': bonus.label} for bonus in sorted(bonuses, cmp=self._sortFunc) ]
        if item.extraBonuses:
            rewards.append({'name': backport.text(R.strings.event.shop.bestDeal.num(item.packID).extraBonusDescr()),
             'count': str(item.getExtraBonusCount())})
        return rewards

    def _getPacksData(self):
        shop = self.__shop
        packs = []
        for item in shop.packItems.itervalues():
            if item.canBuy():
                buyQuantity = backport.text(R.strings.event.shop.available(), count=item.getBonusCount())
            else:
                buyQuantity = eventPackBought(backport.text(R.strings.event.shop.bought()))
            packs.append({'title': backport.text(R.strings.event.shop.bestDeal.num(item.packID)()),
             'price': item.price,
             'oldPrice': item.oldPrice,
             'discount': '-{}%'.format(item.discount),
             'id': item.packID,
             'description': backport.text(R.strings.event.shop.bestDeal.num(item.packID).description()),
             'rewards': self._getRewards(item),
             'buyQuantity': buyQuantity})

        return packs

    def _getFormattedEndDate(self):
        finishDate = self.eventsCache.getEventFinishTime()
        finishDateStruct = getTimeStructInLocal(finishDate)
        finishDateText = backport.text(R.strings.event.shop.endDate(), day=finishDateStruct.tm_mday, month=i18n.makeString(MENU.datetime_months(finishDateStruct.tm_mon)), year=finishDateStruct.tm_year)
        return finishDateText

    def _updateShop(self):
        shop = self.__shop
        if not shop.isEnabled():
            self.closeView()
            return
        packsData = self._getPacksData()
        self.as_setPackBannersDataS(packsData[0], packsData[1])
        self.as_setExpireDateS(self._getFormattedEndDate())
