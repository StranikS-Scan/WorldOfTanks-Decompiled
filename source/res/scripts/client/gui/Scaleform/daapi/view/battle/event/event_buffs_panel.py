# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_buffs_panel.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EventBuffsPanelMeta import EventBuffsPanelMeta
from gui.shared import EVENT_BUS_SCOPE, events
from gui.impl.gen import R
from gui.impl import backport
from gui import makeHtmlString
TOOLTIP_FORMAT = '{{HEADER}}{0:>s}{{/HEADER}}\n/{{BODY}}{1:>s}{{/BODY}}'

class EventBuffsPanel(EventBuffsPanelMeta):

    def __init__(self):
        super(EventBuffsPanel, self).__init__()
        self._buffs = []

    def _populate(self):
        self.addListener(events.BuffUiEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.BuffUiEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.BuffUiEvent.ON_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.BuffUiEvent.ON_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def __handleBuffUnApply(self, event):
        buff = event.ctx['id']
        if buff in self._buffs:
            self.as_removeBuffSlotS(buff)
            self._buffs.remove(buff)

    def __handleBuffApply(self, event):
        player = BigWorld.player()
        if player and not player.isVehicleAlive:
            return
        tooltipTextTag = event.ctx['tooltipTextTag']
        titleRes = R.strings.event.tooltip.buffs.dyn(tooltipTextTag).dyn('title')
        descriptionRes = R.strings.event.tooltip.buffs.dyn(tooltipTextTag).dyn('description')
        tooltipTitleText = backport.text(titleRes()) if titleRes.exists() else tooltipTextTag
        tooltipDescText = backport.text(descriptionRes()) if descriptionRes.exists() else tooltipTextTag
        anomalyText = backport.text(R.strings.event.tooltip.buffs.anomaly())
        header = makeHtmlString('html_templates:lobby/tooltips', 'tooltip_buff_header', {'iconName': tooltipTextTag,
         'header': tooltipTitleText})
        body = makeHtmlString('html_templates:lobby/tooltips', 'tooltip_buff_body', {'anomaly': anomalyText,
         'body': tooltipDescText})
        tooltip = TOOLTIP_FORMAT.format(header, body)
        buff = event.ctx['id']
        if buff not in self._buffs:
            self._buffs.append(buff)
            self.as_addBuffSlotS(buff, event.ctx['iconName'], tooltip)
