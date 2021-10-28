# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_buff_notification_panel.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EventBuffNotificationSystemMeta import EventBuffNotificationSystemMeta
from gui.shared import EVENT_BUS_SCOPE, events
from gui.impl import backport
from gui.impl.gen import R
from helpers.CallbackDelayer import CallbackDelayer
NOTIFICATION_SHOW_TIME = 4

class EventBuffsNotificationSystem(EventBuffNotificationSystemMeta):

    def __init__(self):
        super(EventBuffsNotificationSystem, self).__init__()
        self._callbackDelayer = CallbackDelayer()

    def _populate(self):
        self.addListener(events.BuffUiEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.BuffUiEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.BuffUiEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.BuffUiEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self._callbackDelayer.destroy()

    def __handleBuffApply(self, event):
        player = BigWorld.player()
        if player and not player.isVehicleAlive:
            return
        tooltipTextTag = event.ctx['tooltipTextTag']
        tooltipObj = R.strings.event.tooltip.buffs.dyn(tooltipTextTag)
        titleRes = tooltipObj.dyn('title')
        time1 = tooltipObj.dyn('value')
        desc1 = tooltipObj.dyn('effect')
        time2 = tooltipObj.dyn('value2')
        desc2 = tooltipObj.dyn('effect2')
        data = {'iconSource': backport.image(R.images.gui.maps.icons.event.buffs.dyn(event.ctx['tooltipTextTag'])()),
         'title': backport.text(titleRes()) if titleRes.exists() else tooltipTextTag,
         'timeDescription1': backport.text(time1()) if time1.exists() else '',
         'description1': backport.text(desc1()) if desc1.exists() else '',
         'timeDescription2': backport.text(time2()) if time2.exists() else '',
         'description2': backport.text(desc2()) if desc2.exists() else ''}
        self.as_showBuffNotificationS(data)
        self._callbackDelayer.delayCallback(NOTIFICATION_SHOW_TIME, self.__handleBuffUnApply)

    def __handleBuffUnApply(self, *_):
        self.as_hideBuffNotificationS()
