# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/messenger/formatters/service_channel.py
import logging
import typing
from fun_random.gui.feature.fun_constants import FunNotificationType
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression, hasSpecifiedSubModes
from fun_random.notification.decorators import FunRandomNewSubModesMessageDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.models.notifications import FunNotification
_logger = logging.getLogger(__name__)
_INFO_HEADER_TEMPLATE = 'InformationHeaderSysMessage'
_NEW_SUB_MODES_TEMPLATE = 'FunRandomNewSubModes'
_WARNING_HEADER_TEMPLATE = 'WarningHeaderSysMessage'

class FunRandomNotificationsFormatter(ServiceChannelFormatter, FunProgressionWatcher, FunSubModesWatcher):
    _DECORATOR = {FunNotificationType.NEW_SUB_MODES: FunRandomNewSubModesMessageDecorator}
    _PRIORITY = {FunNotificationType.NEW_SUB_MODES: NotificationPriorityLevel.HIGH,
     FunNotificationType.SWITCH_OFF_SUB_MODES: NotificationPriorityLevel.HIGH,
     FunNotificationType.SWITCH_ON_SUB_MODES: NotificationPriorityLevel.HIGH}
    _TEMPLATE = {FunNotificationType.NEW_SUB_MODES: _NEW_SUB_MODES_TEMPLATE,
     FunNotificationType.SWITCH_OFF_SUB_MODES: _WARNING_HEADER_TEMPLATE}

    def canBeEmpty(self):
        return True

    def format(self, message, *_):
        notificationType = message.notificationType
        decorator = self._DECORATOR.get(notificationType)
        template = self._TEMPLATE.get(notificationType, _INFO_HEADER_TEMPLATE)
        priority = self._PRIORITY.get(notificationType, NotificationPriorityLevel.MEDIUM)
        messageText = self._getMessageText(notificationType, message)
        messageHeader = backport.text(R.strings.fun_random.notification.title())
        ctx = {'header': messageHeader,
         'text': messageText}
        return [MessageData(g_settings.msgTemplates.format(template, ctx=ctx, data={'savedData': {'message': message}}), self._getGuiSettings(None, key=template, priorityLevel=priority, decorator=decorator))] if messageText else []

    @classmethod
    def _getSubModesText(cls, subModesIDs, textRes):
        subModes = cls.getSubModes(subModesIDs=subModesIDs, isOrdered=True)
        if not subModes:
            _logger.error('Empty sub modes. Check hasAnySubMode defence.')
            return None
        elif len(subModes) > 1:
            separator = backport.text(R.strings.fun_random.notification.subModesSeparator())
            return backport.text(textRes.multiple(), subModesNames=separator.join([ backport.text(subMode.getLocalsResRoot().userName.quoted()) for subMode in subModes ]))
        else:
            singleSubModeName = backport.text(subModes[0].getLocalsResRoot().userName.quoted())
            return backport.text(textRes.single(), subModeName=singleSubModeName)

    def _getMessageText(self, notificationType, message):
        messageText = None
        if notificationType == FunNotificationType.NEW_PROGRESSION:
            messageText = self._formatNewProgression()
        elif notificationType == FunNotificationType.NEW_SUB_MODES:
            messageText = self._formatNewSubModes(message.subModesIDs, message.isNewProgression)
        elif notificationType == FunNotificationType.STOP_SUB_MODES:
            messageText = self._formatStopSubModes(message.subModesIDs, message.isNewProgression)
        elif notificationType == FunNotificationType.SWITCH_ON_SUB_MODES:
            messageText = self._formatSwitchOnSubModes(message.subModesIDs)
        elif notificationType == FunNotificationType.SWITCH_OFF_SUB_MODES:
            messageText = self._formatSwitchOffSubModes(message.subModesIDs)
        elif notificationType == FunNotificationType.STOP_ALL_SUB_MODES:
            messageText = backport.text(R.strings.fun_random.notification.finishSubModes())
        return messageText

    @hasActiveProgression()
    def _formatNewProgression(self):
        return backport.text(R.strings.fun_random.notification.newProgression())

    @hasSpecifiedSubModes()
    def _formatNewSubModes(self, subModesIDs, isNewProgression):
        textRes = R.strings.fun_random.notification.newSubModes
        textRes = textRes.withProgression if isNewProgression else textRes.withoutProgression
        return self._getSubModesText(subModesIDs, textRes)

    @hasSpecifiedSubModes()
    def _formatStopSubModes(self, subModesIDs, isNewProgression):
        textRes = R.strings.fun_random.notification.finishSubModes
        textRes = textRes.withProgression if isNewProgression else textRes.withoutProgression
        return self._getSubModesText(subModesIDs, textRes)

    @hasSpecifiedSubModes()
    def _formatSwitchOnSubModes(self, subModesIDs):
        return self._getSubModesText(subModesIDs, R.strings.fun_random.notification.switchOnSubModes)

    @hasSpecifiedSubModes()
    def _formatSwitchOffSubModes(self, subModesIDs):
        return self._getSubModesText(subModesIDs, R.strings.fun_random.notification.switchOffSubModes)
