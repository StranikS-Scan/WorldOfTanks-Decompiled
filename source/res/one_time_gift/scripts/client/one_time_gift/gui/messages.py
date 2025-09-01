# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/messages.py
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages

@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushOTGNotActiveErrorNotification(systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientSysMessage(backport.text(R.strings.one_time_gift_messenger.serviceChannelMessages.eventEndedError.body()), SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushOTGRewardReceivedErrorNotification(systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientSysMessage(backport.text(R.strings.one_time_gift_messenger.serviceChannelMessages.rewardReceived.body()), SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushOTGNotAvailableErrorNotification(systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientSysMessage(backport.text(R.strings.one_time_gift_messenger.serviceChannelMessages.notAvailableError.body()), SystemMessages.SM_TYPE.ErrorSimple, priority=NotificationPriorityLevel.MEDIUM)
