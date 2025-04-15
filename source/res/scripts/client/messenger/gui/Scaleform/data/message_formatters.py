# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/data/message_formatters.py
from gui.battle_control.controllers.dyn_squad_functional import DYN_SQUAD_TYPE
from messenger import g_settings
from messenger.gui.Scaleform import FILL_COLORS
from messenger.proto.shared_messages import ACTION_MESSAGE_TYPE

class BaseMessageFormatter(object):

    def __init__(self, actionMessage):
        self._actionMessage = actionMessage

    def getFormattedMessage(self):
        return self._actionMessage.getMessage()

    def getFillColor(self):
        return FILL_COLORS.BLACK


class WarningMessageFormatter(BaseMessageFormatter):
    FONT_COLOR_GENERAL = '#FFC364'

    def __init__(self, actionMessage):
        BaseMessageFormatter.__init__(self, actionMessage)

    def getFormattedMessage(self):
        formatted = g_settings.htmlTemplates.format('battleWarningMessage', ctx={'fontColor': self.FONT_COLOR_GENERAL,
         'message': self._actionMessage.getMessage()})
        return formatted


class ErrorMessageFormatter(BaseMessageFormatter):

    def getFormattedMessage(self):
        formatted = g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': self._actionMessage.getMessage()})
        return formatted


class DynamicSquadMessageFormatter(WarningMessageFormatter):
    _DYN_SQUAD_IMAGE = 'squad_silver_{0}'
    FONT_COLOR_GENERAL = '#FFC364'
    FONT_COLOR_TEAM_SIDE_BASED = '#999999'

    def getFormattedMessage(self):
        fontColor = self.FONT_COLOR_GENERAL
        if self._actionMessage.squadType in (DYN_SQUAD_TYPE.ENEMY, DYN_SQUAD_TYPE.ALLY):
            fontColor = self.FONT_COLOR_TEAM_SIDE_BASED
        formatted = g_settings.htmlTemplates.format('battleWarningMessage', ctx={'fontColor': fontColor,
         'message': self._actionMessage.getMessage()})
        if self._actionMessage.squadNum is not None and self._actionMessage.squadType != DYN_SQUAD_TYPE.OWN:
            formatted = '{0}{1}'.format(g_settings.htmlTemplates.format('battleWarningMessageImage', ctx={'image': self._DYN_SQUAD_IMAGE.format(self._actionMessage.squadNum)}), formatted)
        return formatted

    def getFillColor(self):
        fillColor = FILL_COLORS.BLACK
        if self._actionMessage.squadType == DYN_SQUAD_TYPE.ENEMY:
            fillColor = FILL_COLORS.RED
        if self._actionMessage.squadType == DYN_SQUAD_TYPE.ALLY:
            fillColor = FILL_COLORS.GREEN
        return fillColor


class FairplayWarningMessageFormatter(BaseMessageFormatter):

    def getFormattedMessage(self):
        return g_settings.htmlTemplates.format(self._actionMessage.getTemplateKey())


class CommendationsMessageFormatter(BaseMessageFormatter):

    def getFormattedMessage(self):
        formatted = g_settings.htmlTemplates.format('commendationsWarningMessage', ctx={'image': self._actionMessage.getIconName(),
         'message': self._actionMessage.getMessage()})
        return formatted

    def getFillColor(self):
        return FILL_COLORS.BLACK


_MESSAGE_FORMATTERS_MAP = {ACTION_MESSAGE_TYPE.WARNING: WarningMessageFormatter,
 ACTION_MESSAGE_TYPE.ERROR: ErrorMessageFormatter,
 ACTION_MESSAGE_TYPE.FAIRPLAY_WARNING: FairplayWarningMessageFormatter,
 ACTION_MESSAGE_TYPE.DYN_SQUAD: DynamicSquadMessageFormatter,
 ACTION_MESSAGE_TYPE.COMMENDATIONS: CommendationsMessageFormatter}

def getMessageFormatter(actionMessage):
    return _MESSAGE_FORMATTERS_MAP.get(actionMessage.getType(), BaseMessageFormatter)(actionMessage)
