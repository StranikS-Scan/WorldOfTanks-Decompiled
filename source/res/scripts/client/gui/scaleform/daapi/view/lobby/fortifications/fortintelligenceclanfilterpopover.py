# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortIntelligenceClanFilterPopover.py
import time
from gui.LobbyContext import g_lobbyContext
from gui.shared.formatters import text_styles
from gui.shared.fortifications.fort_helpers import adjustDefenceHoursListToLocal
from helpers import time_utils
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortIntelligenceClanFilterPopoverMeta import FortIntelligenceClanFilterPopoverMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from FortifiedRegionBase import NOT_ACTIVATED

class FortIntelligenceClanFilterPopover(FortIntelligenceClanFilterPopoverMeta, FortViewHelper):

    def __init__(self, _ = None):
        super(FortIntelligenceClanFilterPopover, self).__init__()

    def _populate(self):
        super(FortIntelligenceClanFilterPopover, self)._populate()
        headerText = text_styles.highTitle(_ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_HEADER))
        clanLevelText = text_styles.standard(_ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_CLANLEVEL))
        startHourRangeText = text_styles.standard(_ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_STARTHOURRANGE))
        self.as_setDescriptionsTextS(headerText, clanLevelText, startHourRangeText)
        defaultButtonText = _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_DEFAULTBUTTONTEXT)
        applyButtonText = _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_APPLYBUTTONTEXT)
        cancelButtonText = _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_CANCELBUTTONTEXT)
        self.as_setButtonsTextS(defaultButtonText, applyButtonText, cancelButtonText)
        defaultButtonTooltip = TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANFILTERPOPOVER_DEFAULT
        applyButtonTooltip = TOOLTIPS.FORTIFICATION_FORTINTELLIGENCECLANFILTERPOPOVER_APPLY
        self.as_setButtonsTooltipsS(defaultButtonTooltip, applyButtonTooltip)
        minClanLevel = FORTIFICATION_ALIASES.CLAN_FILTER_MIN_LEVEL
        maxClanLevel = FORTIFICATION_ALIASES.CLAN_FILTER_MAX_LEVEL
        startDefenseHour = FORTIFICATION_ALIASES.CLAN_FILTER_MIN_HOUR
        startDefenseMin = 0
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            minClanLevel, maxClanLevel, startDefenseHour, availability = cache.getDefaultFilterData()
            selectedDate = time.localtime(time_utils.getTimeForLocal(time_utils.getCurrentTimestamp(), max(0, startDefenseHour)))
            startDefenseMin = selectedDate.tm_min
        data = {'minClanLevel': minClanLevel,
         'maxClanLevel': maxClanLevel,
         'startDefenseHour': startDefenseHour,
         'startDefenseMinutes': startDefenseMin,
         'isTwelveHoursFormat': self.app.utilsManager.isTwelveHoursFormat(),
         'isWrongLocalTime': self._isWrongLocalTime(),
         'skipValues': adjustDefenceHoursListToLocal(g_lobbyContext.getServerSettings().getForbiddenFortDefenseHours())}
        defenceStart, _ = self.fortCtrl.getFort().getLocalDefenceHour()
        if defenceStart != NOT_ACTIVATED:
            data['yourOwnClanStartDefenseHour'] = defenceStart
        self.as_setDataS(data)

    def getAvailabilityProvider(self):
        return [{'label': _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_AVAILABILITY_ITEM_TOMORROW),
          'data': FORTIFICATION_ALIASES.CLAN_FILTER_DAY_TOMORROW}, {'label': _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_AVAILABILITY_ITEM_DAYAFTERTOMORROW),
          'data': FORTIFICATION_ALIASES.CLAN_FILTER_DAY_DAY_AFTER_TOMORROW}, {'label': _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_AVAILABILITY_ITEM_ANY),
          'data': FORTIFICATION_ALIASES.CLAN_FILTER_DAY_ANY}]

    def useFilter(self, value, isDefaultData):
        if isDefaultData:
            self.fireEvent(FortEvent(FortEvent.ON_INTEL_FILTER_RESET), EVENT_BUS_SCOPE.FORT)
        else:
            self.fireEvent(FortEvent(FortEvent.ON_INTEL_FILTER_APPLY), EVENT_BUS_SCOPE.FORT)
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            if isDefaultData:
                cache.resetFilters()
            else:
                cache.setDefaultFilterData(value.minClanLevel, value.maxClanLevel, value.startDefenseHour)
            cache.request()
            self.fireEvent(FortEvent(FortEvent.ON_INTEL_FILTER_DO_REQUEST), EVENT_BUS_SCOPE.FORT)

    def onWindowClose(self):
        self.destroy()
