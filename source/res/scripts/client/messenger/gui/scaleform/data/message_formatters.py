# Embedded file name: scripts/client/messenger/gui/Scaleform/data/message_formatters.py
from gui.battle_control.dyn_squad_functional import DYN_SQUAD_TYPE
from messenger import g_settings
from messenger.gui.Scaleform import FILL_COLORS
from messenger.proto.shared_messages import ACTION_MESSAGE_TYPE

class _WARNING_FONT_COLOR(object):
    GENERAL = '#FFC364'
    TEAM_SIDE_BASED = '#999999'


_DYN_SQUAD_IMAGE = 'squad{0}s'

def getMessageFormatter(actionMessage):
    if actionMessage.getType() == ACTION_MESSAGE_TYPE.WARNING:
        return WarningMessageFormatter(actionMessage)
    else:
        return BaseMessageFormatter(actionMessage)


class BaseMessageFormatter(object):

    def __init__(self, actionMessage):
        self._actionMessage = actionMessage

    def getFormattedMessage(self):
        return self._actionMessage.getMessage()

    def getFillColor(self):
        return FILL_COLORS.BLACK


class WarningMessageFormatter(BaseMessageFormatter):

    def __init__(self, actionMessage):
        BaseMessageFormatter.__init__(self, actionMessage)

    def getFormattedMessage(self):
        fontColor = _WARNING_FONT_COLOR.GENERAL
        if self._actionMessage.squadType in (DYN_SQUAD_TYPE.ENEMY, DYN_SQUAD_TYPE.ALLY):
            fontColor = _WARNING_FONT_COLOR.TEAM_SIDE_BASED
        formatted = g_settings.htmlTemplates.format('battleWarningMessage', ctx={'fontColor': fontColor,
         'message': ' ' + self._actionMessage.getMessage()})
        if self._actionMessage.squadNum is not None and self._actionMessage.squadType != DYN_SQUAD_TYPE.OWN:
            formatted = '{0}{1}'.format(g_settings.htmlTemplates.format('battleWarningMessageImage', ctx={'image': _DYN_SQUAD_IMAGE.format(self._actionMessage.squadNum)}), formatted)
        return formatted

    def getFillColor(self):
        fillColor = FILL_COLORS.BLACK
        if self._actionMessage.squadType == DYN_SQUAD_TYPE.ENEMY:
            fillColor = FILL_COLORS.RED
        if self._actionMessage.squadType == DYN_SQUAD_TYPE.ALLY:
            fillColor = FILL_COLORS.GREEN
        return fillColor
