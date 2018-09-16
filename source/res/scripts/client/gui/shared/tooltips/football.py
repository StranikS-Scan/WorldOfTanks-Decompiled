# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/football.py
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.elen import ElenPreviewTooltipData
from helpers.i18n import makeString as _ms
from helpers import int2roman
from gui import makeHtmlString
from gui.event_boards.event_boards_items import EVENT_DATE_TYPE
from gui.event_boards.event_boards_timer import FORMAT_MINUTE_STR, getTimeStatus
from CurrentVehicle import g_currentVehicle

class FootballBuffonTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(FootballBuffonTooltipData, self).__init__(context, TOOLTIP_TYPE.FOOTBALL)
        self._setContentMargin(top=0, left=0, bottom=3, right=0)
        self._setMargins(afterBlock=0)
        self._setWidth(362)

    def _packBlocks(self, *args, **kwargs):
        items = super(FootballBuffonTooltipData, self)._packBlocks()
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(_ms(FOOTBALL2018.CARDCOLLECTION_BUFFON_INFOTIP_TITLE)), img=RES_ICONS.MAPS_ICONS_FE18_TOOLTIPS_FOOTBALLBUFFONTOOLTIPHEADER, txtPadding=formatters.packPadding(top=20), txtOffset=20))
        items.append(formatters.packTextBlockData(text=text_styles.main(FOOTBALL2018.CARDCOLLECTION_BUFFON_INFOTIP_DESC), padding=formatters.packPadding(left=20, right=10, top=-10, bottom=10)))
        return items


class GreenFlagTooltipData(ElenPreviewTooltipData):

    def __init__(self, context):
        super(GreenFlagTooltipData, self).__init__(context)
        self._setContentMargin(top=2, left=0, bottom=3, right=0)

    def _isRegistered(self, currentEvent):
        return currentEvent.isActive()

    def _primeTimeTitleValid(self):
        return FOOTBALL2018.HANGAR_GREENFLAG_TOOLTIP_PRIMETIME_NOW

    def _primeTimeTitleInvalid(self):
        return FOOTBALL2018.HANGAR_GREENFLAG_TOOLTIP_PRIMETIME_FUTURE

    def _getCurrentEvent(self):
        eventsData = self._eventsController.getFootballSettingsData()
        for event in eventsData.getEvents():
            if event.isActive():
                return event
            value, _ = getTimeStatus(event.getStartDate())
            if value > 0:
                return event

        vehicle = g_currentVehicle.item
        return eventsData.getEventForVehicle(vehicle.intCD)

    def _getHeader(self, currentEvent):
        if currentEvent.isActive():
            eventId = currentEvent.getEventID()
            try:
                val = int2roman(int(eventId[-1]))
            except ValueError:
                val = eventId

            stageName = text_styles.neutral(_ms(FOOTBALL2018.HANGAR_GREENFLAG_TOOLTIP_STAGE_STAGENAME, stageNum=val))
            text = text_styles.main(_ms(FOOTBALL2018.HANGAR_GREENFLAG_TOOLTIP_STAGE_INPROGRESS, stageName=stageName))
        else:
            flagIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON)
            textData = currentEvent.getFormattedRemainingTime(EVENT_DATE_TYPE.START)
            msgText = FOOTBALL2018.HANGAR_GREENFLAG_TOOLTIP_STAGE_BEFOREBEGINNING
            time = textData[0] if textData[0] is not 0 else 1
            timeText = textData[1] if textData[1] else FORMAT_MINUTE_STR
            timeName = EVENT_BOARDS.time_period(str(timeText))
            text = '{} {} {} {}'.format(flagIcon, text_styles.main(_ms(msgText)), text_styles.neutral(time), text_styles.neutral(timeName))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(FOOTBALL2018.HANGAR_GREENFLAG_TOOLTIP_EVENT_NAME), img=currentEvent.getKeyArtSmall(), txtPadding=formatters.packPadding(top=22), txtOffset=20, txtGap=0, desc=text)

    def _getBottom(self, currentEvent):
        if not currentEvent.isActive():
            return formatters.packTextBlockData(text=text_styles.main(FOOTBALL2018.HANGAR_GREENFLAG_TOOLTIP_BOTTOM), padding=formatters.packPadding(left=20, top=8, bottom=20, right=20))
        else:
            return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
             'message': text_styles.critical(_ms(TOOLTIPS.HANGAR_ELEN_BOTTOM_UNAVAILABLE))}), padding=formatters.packPadding(top=3, bottom=16)) if not currentEvent.isAvailableServer(self._connectionMgr.peripheryID) else None
