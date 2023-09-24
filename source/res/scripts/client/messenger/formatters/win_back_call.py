# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/win_back_call.py
import typing
from gui.shared.notifications import NotificationGuiSettings
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage

class SimpleFormatter(ServiceChannelFormatter):

    def __init__(self, templateName):
        self._template = templateName

    def format(self, message, *args):
        if message is None:
            return []
        else:
            formatted = g_settings.msgTemplates.format(self._template, ctx=self.getCtx(message, *args))
            return [MessageData(formatted, self._getGuiSettings(message, self._template))]

    def getCtx(self, message, *args):
        return None

    def _getGuiSettings(self, data, key=None, priorityLevel=None, messageType=None, messageSubtype=None, decorator=None, auxData=None):
        try:
            isAlert = data.isHighImportance and data.active
        except AttributeError:
            isAlert = False

        if priorityLevel is None:
            priorityLevel = g_settings.msgTemplates.priority(key)
        return NotificationGuiSettings(self.isNotify(), priorityLevel, isAlert, messageType=messageType, messageSubtype=messageSubtype, decorator=decorator, auxData=auxData, lifeTime=g_settings.msgTemplates.lifeTime(key))


class WinBackCallEntryFormatter(SimpleFormatter):
    __TEMPLATE = 'WinBackCallEntry'

    def __init__(self):
        super(WinBackCallEntryFormatter, self).__init__(self.__TEMPLATE)

    def format(self, message, *args):
        formatted = g_settings.msgTemplates.format(self._template, ctx=self.getCtx(message, *args))
        return [MessageData(formatted, self._getGuiSettings(message, self._template, messageType=message.type, priorityLevel=message.data.get('priority')))]
