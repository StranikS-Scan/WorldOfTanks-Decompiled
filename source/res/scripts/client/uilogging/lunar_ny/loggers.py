# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/lunar_ny/loggers.py
import typing
import logging
from wotdecorators import noexcept
from uilogging.base.logger import BaseLogger, ifUILoggingEnabled
from uilogging.core.core_constants import LogLevels
from uilogging.lunar_ny.constants import FEATURE, LogGroups, LogActions, ParentSreen, AdditionalInfo, OPEN_INFO_BY_COUNT
from lunar_ny.lunar_ny_constants import EnvelopeTypes
from uilogging.lunar_ny.constants import getAdditionalInfoByEnvelopeType
_logger = logging.getLogger(__name__)

class _LunarNYLogger(BaseLogger):

    def __init__(self, group):
        super(_LunarNYLogger, self).__init__(FEATURE, group.value)

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, parentScreen, additionalArgument=None, loglevel=LogLevels.INFO):
        data = {'parent_screen': parentScreen.value}
        if additionalArgument is not None:
            data['additional_info'] = additionalArgument.value
        super(_LunarNYLogger, self).log(action=action.value, loglevel=loglevel, **data)
        return

    def _logClick(self, parentScreen, additional=None):
        self.log(LogActions.CLICK, parentScreen, additional)

    @noexcept
    def _logOpenLootBox(self, count, lootBox, parentScreen):
        additional = AdditionalInfo.OPEN_REMAINDER
        if count in OPEN_INFO_BY_COUNT and count < lootBox.getInventoryCount():
            additional = OPEN_INFO_BY_COUNT[count]
        self.log(LogActions.CLICK, parentScreen, additional)

    @noexcept
    def _logEnvelopeClick(self, envelope):
        if envelope is not None:
            self._logClick(ParentSreen.HANGAR, getAdditionalInfoByEnvelopeType(EnvelopeTypes(envelope)))
        else:
            _logger.warning('Invalid envelope type')
        return


class LunarWidgetLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarWidgetLogger, self).__init__(LogGroups.MAIN_WIDGET)

    @ifUILoggingEnabled()
    def logClick(self):
        self._logClick(ParentSreen.HANGAR)


class LunarHistoryLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarHistoryLogger, self).__init__(LogGroups.HISTORY_BUTTON)

    @ifUILoggingEnabled()
    def logClick(self):
        self._logClick(ParentSreen.STORAGE_VIEW)


class LunarSelectableObject3dLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarSelectableObject3dLogger, self).__init__(LogGroups.SELECTABLE_OBJECT_3D)

    @ifUILoggingEnabled()
    def logClick(self):
        self._logClick(ParentSreen.HANGAR)


class LunarPopoverBuyBtnLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarPopoverBuyBtnLogger, self).__init__(LogGroups.POPOVER_BUY_BUTTON)

    @ifUILoggingEnabled()
    def logBuyBtnClick(self, envelope):
        self._logEnvelopeClick(envelope)


class LunarPopoverSendBtn(_LunarNYLogger):

    def __init__(self):
        super(LunarPopoverSendBtn, self).__init__(LogGroups.POPOVER_SEND_BUTTON)

    @ifUILoggingEnabled()
    def logSendBtnClick(self, envelope):
        self._logEnvelopeClick(envelope)


class LunarSideBarLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarSideBarLogger, self).__init__(LogGroups.SIDE_BAR_TAB)

    @ifUILoggingEnabled()
    def logClick(self):
        self._logClick(ParentSreen.LUNAR_NY_LOBBY, AdditionalInfo.STORAGE_VIEW)


class LunarOpenEnvelopeLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarOpenEnvelopeLogger, self).__init__(LogGroups.OPEN_ENVELOPE_BUTTON)

    @noexcept
    @ifUILoggingEnabled()
    def logOpenFromNotification(self, notification):
        if notification.onlyPopUp():
            additionalInfo = AdditionalInfo.POP_UP_NOTIFICATION
        else:
            additionalInfo = AdditionalInfo.NOTIFICATION_CENTER
        self._logClick(ParentSreen.HANGAR, additionalInfo)

    @ifUILoggingEnabled()
    def logOpenFromStorage(self, count, lootBox):
        self._logOpenLootBox(count, lootBox, ParentSreen.STORAGE_VIEW)


class LunarOpenCommonBtnLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarOpenCommonBtnLogger, self).__init__(LogGroups.OPEN_COMMON_BUTTON)

    @ifUILoggingEnabled()
    def logOpenFromStorage(self, count, lootBox):
        self._logOpenLootBox(count, lootBox, ParentSreen.STORAGE_VIEW)


class LunarBuyBtnLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarBuyBtnLogger, self).__init__(LogGroups.BUY_BUTTON)

    @ifUILoggingEnabled()
    def logClick(self, envelopeType):
        self._logClick(ParentSreen.SEND_ENVELOPES_VIEW, getAdditionalInfoByEnvelopeType(EnvelopeTypes(envelopeType)))


class LunarBuyAdditionalBtnLogger(_LunarNYLogger):

    def __init__(self):
        super(LunarBuyAdditionalBtnLogger, self).__init__(LogGroups.BUY_ADDITIONAL_BUTTON)

    @ifUILoggingEnabled()
    def logClick(self):
        self._logClick(ParentSreen.SEND_ENVELOPES_VIEW)
