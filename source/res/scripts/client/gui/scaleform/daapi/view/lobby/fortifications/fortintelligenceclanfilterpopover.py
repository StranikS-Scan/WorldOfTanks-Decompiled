# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortIntelligenceClanFilterPopover.py
from helpers.i18n import makeString as _ms
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_text import getText
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.meta.FortIntelligenceClanFilterPopoverMeta import FortIntelligenceClanFilterPopoverMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent

class FortIntelligenceClanFilterPopover(View, FortIntelligenceClanFilterPopoverMeta, SmartPopOverView, FortViewHelper, AppRef):

    def __init__(self, ctx = None):
        super(FortIntelligenceClanFilterPopover, self).__init__()
        self._orderID = str(ctx.get('data'))

    def _populate(self):
        super(FortIntelligenceClanFilterPopover, self)._populate()
        headerText = getText(fort_text.HIGH_TITLE, _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_HEADER))
        clanLevelText = getText(fort_text.STANDARD_TEXT, _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_CLANLEVEL))
        startHourRangeText = getText(fort_text.STANDARD_TEXT, _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_STARTHOURRANGE))
        availabilityText = getText(fort_text.STANDARD_TEXT, _ms(FORTIFICATIONS.FORTINTELLIGENCE_CLANFILTERPOPOVER_AVAILABILITY))
        self.as_setDescriptionsTextS(headerText, clanLevelText, startHourRangeText, availabilityText)
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
        availability = FORTIFICATION_ALIASES.CLAN_FILTER_DAY_ANY
        cache = self.fortCtrl.getPublicInfoCache()
        if cache:
            minClanLevel, maxClanLevel, startDefenseHour, availability = cache.getDefaultFilterData()
        data = {'minClanLevel': minClanLevel,
         'maxClanLevel': maxClanLevel,
         'startDefenseHour': startDefenseHour,
         'availability': availability}
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
            cache.setDefaultFilterData(value.minClanLevel, value.maxClanLevel, value.startDefenseHour, value.availability)
            cache.request()
            self.fireEvent(FortEvent(FortEvent.ON_INTEL_FILTER_DO_REQUEST), EVENT_BUS_SCOPE.FORT)

    def onWindowClose(self):
        self.destroy()
