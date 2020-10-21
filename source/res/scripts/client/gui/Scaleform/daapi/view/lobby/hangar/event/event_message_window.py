# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_message_window.py
from functools import partial
import BigWorld
from frameworks.wulf import WindowLayer
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.EventMessageWindowMeta import EventMessageWindowMeta
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.shared.money import Money
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace

class EventMessageWindow(EventMessageWindowMeta):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(EventMessageWindow, self).__init__()
        self.__callback = ctx.get('callback', None)
        self.__data = ctx.get('data', None)
        self.__blur = None
        self.__executiveBlurCallback = None
        return

    def onWindowClose(self):
        self.destroy()

    def setParentWindow(self, window):
        super(EventMessageWindow, self).setParentWindow(window)
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer, blurAnimRepeatCount=1)

    def onResult(self, ok):
        if self.__callback is not None:
            self.__callback(ok)
        self.destroy()
        return

    def _populate(self):
        super(EventMessageWindow, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateMoneyHandler)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__updateMoneyHandler})
        if self._hangarSpace.spaceInited:
            self.__onSpaceCreated()
        else:
            self._hangarSpace.onSpaceCreate += self.__onSpaceCreated

    def _dispose(self):
        if self.__executiveBlurCallback is not None:
            BigWorld.cancelCallback(self.__executiveBlurCallback)
            self.__executiveBlurCallback = None
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__blur.fini()
        self.__blur = None
        self.__setCameraDisabled(False)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.__callback = None
        self.__data = None
        super(EventMessageWindow, self)._dispose()
        return

    def __blurSpace(self):
        self.__updateDynamicData()
        self.as_setMessageDataS(self.__data)
        self.__executiveBlurCallback = None
        if self.__blur is None:
            self.__setCameraDisabled(True)
            self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
            self.as_blurOtherWindowsS(WindowLayer.TOP_WINDOW)
        return

    def __onSpaceCreated(self):
        if self.__executiveBlurCallback is None:
            self.__executiveBlurCallback = BigWorld.callback(0.1, partial(self.__blurSpace))
        return

    def __setCameraDisabled(self, disabled):
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': disabled}), EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, ctx={'disable': disabled}), EVENT_BUS_SCOPE.LOBBY)

    def __updateDynamicData(self):
        data = self.__data
        stats = self._itemsCache.items.stats
        integralFormat = backport.getIntegralFormat
        data['money'] = makeHtmlString('html_templates:lobby', 'moneyPanel', {'crystals': integralFormat(stats.actualCrystal),
         'gold': integralFormat(stats.actualGold),
         'credits': integralFormat(stats.actualCredits),
         'freeExp': integralFormat(stats.actualFreeXP)})
        if data['storageAmount'] or 'currency' not in data:
            data['isExecuteEnabled'] = True
            return
        currency = data['currency']
        value = data['costValue']
        style = getattr(text_styles, ''.join((currency, 'TextBig')))
        icon = getattr(icons, ''.join((currency, 'Big')))
        costString = text_styles.concatStylesWithSpace(text_styles.vehicleName(backport.text(R.strings.bootcamp.cost.messageViewBuy())), text_styles.concatStylesWithSpace(style(integralFormat(value)), icon()))
        price = Money.makeFrom(currency, value)
        shortage = self._itemsCache.items.stats.money.getShortage(price)
        data['isExecuteEnabled'] = not bool(shortage)
        data['costString'] = costString

    def __updateMoneyHandler(self, *args):
        self.__updateDynamicData()
        self.as_setMessageDataS(self.__data)
