# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarFairplayMessageComponent.py
import logging
from BigWorld import DynamicScriptComponent
import SoundGroups
from gui.shared.utils import showAFKWarningInWindowsBar
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_messages import ClientActionTemplateMessage, ACTION_MESSAGE_TYPE
_logger = logging.getLogger(__name__)
AFK_WARNING_MESSAGE_SOUND = 'afk_warning_message'

class AvatarFairplayMessageComponent(DynamicScriptComponent):

    def showWarningMessage(self, templateKey):
        _logger.debug('AvatarFairplayMessageComponent.showMessage: %s', templateKey)
        message = ClientActionTemplateMessage(templateKey, ACTION_MESSAGE_TYPE.FAIRPLAY_WARNING)
        g_messengerEvents.onWarningReceived(message)
        showAFKWarningInWindowsBar()
        SoundGroups.g_instance.playSound2D(AFK_WARNING_MESSAGE_SOUND)
