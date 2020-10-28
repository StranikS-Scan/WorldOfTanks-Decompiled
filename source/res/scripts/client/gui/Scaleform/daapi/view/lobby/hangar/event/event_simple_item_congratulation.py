# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_simple_item_congratulation.py
import GUI
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.event.event_confirmation import EventConfirmationCloser
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.server_events.awards_formatters import getSimpleItemsFormatter, EventItemsSizes, AWARDS_SIZES
from helpers import dependency
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.meta.EventItemsTradeCongratulationMeta import EventItemsTradeCongratulationMeta
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from skeletons.gui.game_event_controller import IGameEventController
from shared_utils import first

class EventSimpleItemCongratulationTab(EventItemsTradeCongratulationMeta, EventConfirmationCloser):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, ctx=None, *args, **kwargs):
        super(EventSimpleItemCongratulationTab, self).__init__(*args, **kwargs)
        self.__shop = self.gameEventController.getShop()
        self.__blur = GUI.WGUIBackgroundBlur()
        self._ctx = ctx
        self._item = self._ctx.get('item')

    def onButtonConfirmationClick(self):
        self.closeView()

    def closeView(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_ITEMS_FOR_TOKENS)), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(EventSimpleItemCongratulationTab, self)._populate()
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.__blur.enable = True
        self._update()

    def _dispose(self):
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.__blur.enable = False
        super(EventSimpleItemCongratulationTab, self)._dispose()

    def _update(self):
        bonuses = self._item.getBonuses()
        formattedBonus = first(getSimpleItemsFormatter().format(bonuses))
        data = {'header': backport.text(R.strings.event.shop.simpleItemCongratulation.header()),
         'title': formattedBonus.userName,
         'description': backport.text(R.strings.event.shop.simpleItemCongratulation.description()),
         'btnLabel': backport.text(R.strings.event.shop.simpleItemCongratulation.btnLabel()),
         'item': formattedBonus.images.get(EventItemsSizes.HUGE),
         'multiplier': formattedBonus.label,
         'sign': formattedBonus.getOverlayIcon(AWARDS_SIZES.BIG)}
        self.as_setDataS(data)
