# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/elen.py
import constants
from CurrentVehicle import g_currentVehicle
from gui.event_boards.event_boards_timer import FORMAT_MINUTE_STR
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.prb_control.prb_getters import getSupportedCurrentArenaBonusType
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.prb_control.entities.listener import IGlobalListener
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.event_boards_controllers import IEventBoardController
from gui.event_boards.event_boards_items import EVENT_DATE_TYPE
from gui.prb_control import prb_getters
from skeletons.gui.shared import IItemsCache

class ElenPreviewTooltipData(BlocksTooltipData, IGlobalListener):
    _eventsController = dependency.descriptor(IEventBoardController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, context):
        super(ElenPreviewTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setContentMargin(top=2, left=3, bottom=3, right=3)
        self._setMargins(afterBlock=0)
        self._setWidth(297)

    def _packBlocks(self, *args, **kwargs):
        eventsController = self._eventsController
        items = super(ElenPreviewTooltipData, self)._packBlocks()
        vehicle = g_currentVehicle.item
        eventsData = eventsController.getEventsSettingsData()
        currentEvent = eventsData.getEventForVehicle(vehicle.intCD)
        isRegistered = self._eventsController.getHangarFlagData().isRegistered(currentEvent.getEventID())
        items.append(self._getHeader(currentEvent))
        primeTimes = currentEvent.getPrimeTimes()
        if not primeTimes.isEmpty() and isRegistered:
            items.append(self._getPrimeTimes(primeTimes))
        items.append(self._getBottom(currentEvent))
        return items

    def _getHeader(self, currentEvent):
        eventID = currentEvent.getEventID()
        isRegistered = self._eventsController.getHangarFlagData().isRegistered(eventID)
        isRegistrationNeeded = currentEvent.getLimits().getIsRegistrationNeeded()
        if isRegistrationNeeded and not isRegistered:
            if currentEvent.isRegistrationFinishSoon():
                flagIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON)
            else:
                flagIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_FLAG_ICON)
            textData = currentEvent.getFormattedRemainingTime(EVENT_DATE_TYPE.PARTICIPANTS_FREEZE)
            msgText = TOOLTIPS.HANGAR_ELEN_HEADER_TOENDOFREGISTRATION
            time = textData[0] if textData[0] is not 0 else 1
            timeText = textData[1] if textData[1] else FORMAT_MINUTE_STR
            timeName = EVENT_BOARDS.time_period(str(timeText))
            text = '{} {} {} {}'.format(flagIcon, text_styles.tutorial(_ms(msgText)), text_styles.tutorial(time), text_styles.tutorial(timeName))
        else:
            textData = currentEvent.getFormattedRemainingTime(EVENT_DATE_TYPE.END)
            msgText = TOOLTIPS.HANGAR_ELEN_HEADER_TOEND
            time = textData[0] if textData[0] is not 0 else 1
            timeText = textData[1] if textData[1] else FORMAT_MINUTE_STR
            timeName = EVENT_BOARDS.time_period(str(timeText))
            if currentEvent.isEndSoon():
                flagIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_TIME_ICON)
                text = '{} {} {} {}'.format(flagIcon, text_styles.tutorial(_ms(msgText)), text_styles.tutorial(time), text_styles.tutorial(timeName))
            else:
                flagIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_EVENTBOARDS_FLAGICONS_FLAG_ICON)
                text = '{} {} {} {}'.format(flagIcon, text_styles.main(_ms(msgText)), text_styles.stats(time), text_styles.stats(timeName))
        return formatters.packImageTextBlockData(title=text_styles.highTitle(_ms(TOOLTIPS.HANGAR_ELEN_HEADER_NAME, name=currentEvent.getName())), img=currentEvent.getKeyArtSmall(), txtPadding=formatters.packPadding(top=22), txtOffset=20, txtGap=-8, desc=text)

    def _getPrimeTimes(self, primeTimes):

        def getPrimeTimeBlock(pt):
            periphery = int(pt.getServer())
            name = str(self._lobbyContext.getPeripheryName(periphery, False))
            name += ':'
            return '{0} {1}'.format(text_styles.main(name), text_styles.standard('{} - {}'.format(pt.getStartLocalTime(), pt.getEndLocalTime())))

        def getSortedPrimeTimes(primeTimes):
            primeTimes = sorted(primeTimes, key=lambda p: int(p.getServer()))
            times = [ getPrimeTimeBlock(pt) for pt in primeTimes ]
            return times

        primeTimesData = primeTimes.getPrimeTimes()
        validTimes = set((pt for pt in primeTimesData if pt.isActive()))
        invalidTimes = set(primeTimesData) - validTimes
        blocks = []
        if validTimes:
            result = ''
            bottomPadding = 20 if invalidTimes else 18
            for primeTime in getSortedPrimeTimes(validTimes):
                result += primeTime + '\n'

            blocks.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(TOOLTIPS.HANGAR_ELEN_PRIMETIME_VALID), desc=result, padding=formatters.packPadding(left=20, top=3, bottom=bottomPadding)))
        if invalidTimes:
            topPadding = -8 if validTimes else 3
            result = ''
            for primeTime in getSortedPrimeTimes(invalidTimes):
                result += primeTime + '\n'

            blocks.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(TOOLTIPS.HANGAR_ELEN_PRIMETIME_INVALID), desc=result, padding=formatters.packPadding(left=20, top=topPadding, bottom=18)))
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def _getBottom(self, currentEvent):
        noserver = not currentEvent.isAvailableServer(self._connectionMgr.peripheryID)
        isRegistered = self._eventsController.getHangarFlagData().isRegistered(currentEvent.getEventID())
        battleType = currentEvent.getBattleType()
        wrongBattleType = getSupportedCurrentArenaBonusType() != battleType
        if battleType == constants.ARENA_BONUS_TYPE.REGULAR:
            battleTypeText = TOOLTIPS.HANGAR_ELEN_BOTTOM_WRONGBATTLETYPE_RANDOM
            battleTypeBodyText = TOOLTIPS.HANGAR_ELEN_BOTTOM_ALLPERIPHERY_BODY
        elif battleType == constants.ARENA_BONUS_TYPE.RANKED:
            battleTypeText = TOOLTIPS.HANGAR_ELEN_BOTTOM_WRONGBATTLETYPE_RANKED
            battleTypeBodyText = TOOLTIPS.HANGAR_ELEN_BOTTOM_ALLPERIPHERY_NOTRANDOM_BODY
        else:
            battleTypeText = ''
            battleTypeBodyText = ''
        inSquadState = self.prbDispatcher.getFunctionalState().isInUnit(constants.PREBATTLE_TYPE.SQUAD)
        if inSquadState:
            unit = prb_getters.getUnit(safe=True)
            if len(unit.getMembers()) == 1:
                inSquadState = False
        wrongSquadState = inSquadState and not currentEvent.getIsSquadAllowed()
        if not isRegistered:
            return formatters.packTextBlockData(text=text_styles.neutral(_ms(TOOLTIPS.HANGAR_ELEN_BOTTOM_GOREGISTER)), padding=formatters.packPadding(left=20, top=3, bottom=16))
        if noserver:
            return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
             'message': text_styles.critical(_ms(TOOLTIPS.HANGAR_ELEN_BOTTOM_UNAVAILABLE))}), padding=formatters.packPadding(top=3, bottom=16))
        if wrongBattleType:
            return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
             'message': text_styles.critical(_ms(battleTypeText))}), padding=formatters.packPadding(top=3, bottom=16))
        return formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
         'message': text_styles.critical(_ms(TOOLTIPS.HANGAR_ELEN_BOTTOM_WRONGSQUADSTATE))}), padding=formatters.packPadding(top=3, bottom=16)) if wrongSquadState else formatters.packImageTextBlockData(title='', desc=text_styles.standard(_ms(battleTypeBodyText)), padding=formatters.packPadding(left=20, right=20, top=3, bottom=16))


class BadgeTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(BadgeTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(380)

    def _packBlocks(self, badgeID):
        blocks = super(BadgeTooltipData, self)._packBlocks()
        badge = self.__itemsCache.items.getBadges()[badgeID]
        tooltipData = [formatters.packImageTextBlockData(title=text_styles.middleTitle(badge.getUserName()), desc=text_styles.main(badge.getUserDescription()), img=badge.getBigIcon(), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, txtPadding=formatters.packPadding(left=8), padding=formatters.packPadding(bottom=-5, top=5))]
        blocks.append(formatters.packBuildUpBlockData(tooltipData))
        blocks.append(formatters.packTextBlockData(text_styles.standard(EVENT_BOARDS.BADGE_TOOLTIP_DESCRIPTION), padding=formatters.packPadding(top=-10, bottom=-5)))
        return blocks


class BabgesGroupTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BabgesGroupTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)
        self._setWidth(380)

    def _packBlocks(self, *args, **kwargs):
        blocks = super(BabgesGroupTooltipData, self)._packBlocks()
        blocks.append(formatters.packTextBlockData(text_styles.highTitle(EVENT_BOARDS.BADGESGROUP_TOOLTIP_HEADER), padding=formatters.packPadding(top=5, bottom=-5)))
        for bonus in args:
            blocks.append(formatters.packRendererTextBlockData(rendererType='AwardItemExUI', dataType='net.wg.gui.data.AwardItemVO', title=text_styles.middleTitle(bonus.name), rendererData={'imgSource': bonus.imgSource}, desc=text_styles.main(bonus.desc), txtPadding=formatters.packPadding(left=8), padding=formatters.packPadding(top=-5, bottom=5)))

        return blocks
