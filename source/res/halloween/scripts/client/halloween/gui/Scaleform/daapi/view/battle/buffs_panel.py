# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/buffs_panel.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EventBuffsPanelMeta import EventBuffsPanelMeta
from gui.shared import EVENT_BUS_SCOPE
from halloween.gui.shared import events as hw_events
from gui.impl.gen import R
from gui.impl import backport
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'

class HWBuffsPanel(EventBuffsPanelMeta):

    def __init__(self):
        super(HWBuffsPanel, self).__init__()
        self._buffs = []

    def _populate(self):
        super(HWBuffsPanel, self)._populate()
        self.addListener(hw_events.BuffGUIEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(hw_events.BuffGUIEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        super(HWBuffsPanel, self)._dispose()
        self.removeListener(hw_events.BuffGUIEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(hw_events.BuffGUIEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def __isValidPlayer(self, vehicleID):
        player = BigWorld.player()
        return player and vehicleID == player.playerVehicleID

    def __handleBuffUnApply(self, event):
        if not self.__isValidPlayer(event.ctx['vehicleID']):
            return
        buff = event.ctx['id']
        if buff in self._buffs:
            self.as_removeBuffSlotS(buff)
            self._buffs.remove(buff)

    def __handleBuffApply(self, event):
        if not self.__isValidPlayer(event.ctx['vehicleID']):
            return
        tooltip = event.ctx['tooltip']
        headerRes = R.strings.hw_tooltips.buffsPanel.dyn(tooltip['tag']).dyn('header')
        descrRes = R.strings.hw_tooltips.buffsPanel.dyn(tooltip['tag']).dyn('descr')
        tooltipText = TOOLTIP_FORMAT.format(backport.text(headerRes()) if headerRes.exists() else tooltip['tag'], backport.text(descrRes(), **tooltip['params']) if descrRes.exists() else tooltip['tag'])
        buff = event.ctx['id']
        if buff not in self._buffs:
            self._buffs.append(buff)
            self.as_addBuffSlotS(buff, event.ctx['iconName'], tooltipText)
