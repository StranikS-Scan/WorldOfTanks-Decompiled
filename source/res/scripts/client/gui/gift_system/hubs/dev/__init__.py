# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/dev/__init__.py
from gui import SystemMessages
from gui.shared.formatters import text_styles

class IDevMessagesPusher(object):

    @classmethod
    def _formatMessage(cls, message):
        return text_styles.stats(message)

    @classmethod
    def _pushClientMessage(cls, message):
        SystemMessages.pushMessage(cls._formatMessage(message), SystemMessages.SM_TYPE.MediumInfo)
