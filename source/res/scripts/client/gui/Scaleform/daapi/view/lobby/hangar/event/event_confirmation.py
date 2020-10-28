# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_confirmation.py
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EventShopConfirmationMeta import EventShopConfirmationMeta
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.impl import backport
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class EventConfirmationView(EventShopConfirmationMeta):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None, *args, **kwargs):
        super(EventConfirmationView, self).__init__(*args, **kwargs)
        self._ctx = ctx

    def onCancelClick(self):
        self.destroy()

    def onBuyClick(self):
        if 'purchaseConfirmedCallback' in self._ctx:
            self._ctx['purchaseConfirmedCallback']()
        self.destroy()

    def _populate(self):
        super(EventConfirmationView, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateMoneyHandler)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__updateMoneyHandler})
        self._updateData()

    def _updateData(self):
        stats = self._itemsCache.items.stats
        ifmt = backport.getIntegralFormat
        self.as_setDataS({'title': self._ctx['title'],
         'descr': self._ctx['descr'],
         'rewards': self._ctx['rewards'],
         'giftTitle': self._ctx['giftTitle'],
         'giftDescr': self._ctx['giftDescr'],
         'gift': self._ctx['gift'],
         'price': ifmt(self._ctx['price']),
         'currency': self._ctx['currency'],
         'money': makeHtmlString('html_templates:lobby', 'moneyPanel', {'crystals': ifmt(stats.actualCrystal),
                   'gold': ifmt(stats.actualGold),
                   'credits': ifmt(stats.actualCredits),
                   'freeExp': ifmt(stats.actualFreeXP)})})

    def _dispose(self):
        super(EventConfirmationView, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)
        callbackProxy = self._ctx.get('closeCallback', None)
        if callbackProxy and callbackProxy.hasReference():
            callbackProxy()
        self._ctx = None
        return

    def __updateMoneyHandler(self, *args):
        self._updateData()


class EventConfirmationCloser(BaseDAAPIModule):
    __SUB_VIEWS_TO_CLOSE = ((WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.EVENT_CONFIRMATION),)

    def _dispose(self):
        for viewType, viewKey in self.__SUB_VIEWS_TO_CLOSE:
            windowContainer = self.app.containerManager.getContainer(viewType)
            if windowContainer is None:
                continue
            view = windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: viewKey})
            if view is not None and not view.isDisposed():
                view.destroy()

        super(EventConfirmationCloser, self)._dispose()
        return
