# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/messenger/formatters/service_channel.py
import logging
import typing
from fun_random.gui.feature.fun_constants import FunNotificationType
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression, hasSpecifiedSubModes
from fun_random.notification.decorators import FunRandomNewSubModesMessageDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.game_control import ILimitedUIController
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.models.notifications import FunNotification
_logger = logging.getLogger(__name__)
_INFO_HEADER_TEMPLATE = 'InformationHeaderSysMessage'
_NEW_SUB_MODES_TEMPLATE = 'FunRandomNewSubModes'
_WARNING_HEADER_TEMPLATE = 'WarningHeaderSysMessage'

class FunRandomNotificationsFormatter(ServiceChannelFormatter, FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher):
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __DECORATOR = {FunNotificationType.NEW_SUB_MODES: FunRandomNewSubModesMessageDecorator}
    __LIMITED_UI = {FunNotificationType.NEW_SUB_MODES: LuiRules.FUN_RANDOM_NOTIFICATIONS,
     FunNotificationType.NEW_PROGRESSION: LuiRules.FUN_RANDOM_NOTIFICATIONS}
    __PRIORITY = {FunNotificationType.NEW_SUB_MODES: NotificationPriorityLevel.HIGH,
     FunNotificationType.SWITCH_OFF_SUB_MODES: NotificationPriorityLevel.HIGH,
     FunNotificationType.SWITCH_ON_SUB_MODES: NotificationPriorityLevel.HIGH}
    __TEMPLATE = {FunNotificationType.NEW_SUB_MODES: _NEW_SUB_MODES_TEMPLATE,
     FunNotificationType.SWITCH_OFF_SUB_MODES: _WARNING_HEADER_TEMPLATE}

    def canBeEmpty(self):
        return True

    def format(self, message, *_):
        notificationType = message.notificationType
        decorator = self.__DECORATOR.get(notificationType)
        template = self.__TEMPLATE.get(notificationType, _INFO_HEADER_TEMPLATE)
        priority = self.__PRIORITY.get(notificationType, NotificationPriorityLevel.MEDIUM)
        luiRule = self.__LIMITED_UI.get(notificationType)
        messageHeader = self.getModeUserName()
        messageText = self._getMessageText(notificationType, message)
        isEnabledByLUI = luiRule is None or self.__limitedUIController.isRuleCompleted(luiRule)
        ctx = {'header': messageHeader,
         'text': messageText}
        return [MessageData(g_settings.msgTemplates.format(template, ctx=ctx, data={'savedData': {'message': message}}), self._getGuiSettings(None, key=template, priorityLevel=priority, decorator=decorator))] if messageText and isEnabledByLUI else []

    @classmethod
    def _getSubModesText(cls, subModesIDs, multipleTextRes, singleTextRes):
        subModes = cls.getSubModes(subModesIDs=subModesIDs, isOrdered=True)
        if not subModes:
            _logger.error('Empty sub modes. Check hasAnySubMode defence.')
            return None
        elif len(subModes) > 1:
            separator = backport.text(R.strings.fun_random.notification.subModesSeparator())
            return backport.text(multipleTextRes(), subModesNames=separator.join([ backport.text(subMode.getLocalsResRoot().userName.quoted()) for subMode in subModes ]))
        else:
            singleSubModeName = backport.text(subModes[0].getLocalsResRoot().userName.quoted())
            return backport.text(singleTextRes(), subModeName=singleSubModeName)

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
            messageText = self._formatStopAllSubModes()
        return messageText

    @hasActiveProgression()
    def _formatNewProgression(self):
        return backport.text(R.strings.fun_random.notification.newProgression())

    @hasSpecifiedSubModes()
    def _formatNewSubModes(self, subModesIDs, isNewProgression):
        return self._getSubModesText(subModesIDs, self.__addProgressionPath(R.strings.fun_random.notification.newSubModes, isNewProgression), self.__addProgressionPath(self.getModeLocalsResRoot().notification.newSubModes, isNewProgression))

    @hasSpecifiedSubModes()
    def _formatStopSubModes(self, subModesIDs, isNewProgression):
        return self._getSubModesText(subModesIDs, self.__addProgressionPath(R.strings.fun_random.notification.finishSubModes, isNewProgression), self.__addProgressionPath(self.getModeLocalsResRoot().notification.finishSubModes, isNewProgression))

    @hasSpecifiedSubModes()
    def _formatSwitchOnSubModes(self, subModesIDs):
        return self._getSubModesText(subModesIDs, R.strings.fun_random.notification.switchOnSubModes, self.getModeLocalsResRoot().notification.switchOnSubModes)

    @hasSpecifiedSubModes()
    def _formatSwitchOffSubModes(self, subModesIDs):
        return self._getSubModesText(subModesIDs, R.strings.fun_random.notification.switchOffSubModes, self.getModeLocalsResRoot().notification.switchOffSubModes)

    def _formatStopAllSubModes(self):
        return backport.text(R.strings.fun_random.notification.finishSubModes(), modeName=self.getModeUserName())

    def __addProgressionPath(self, textRes, isNewProgression):
        return textRes.withProgression if isNewProgression else textRes.withoutProgression
