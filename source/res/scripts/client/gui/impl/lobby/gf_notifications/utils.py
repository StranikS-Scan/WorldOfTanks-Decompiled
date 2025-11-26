# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/utils.py
import typing
import uuid
from gui.impl.lobby.gf_notifications.cache import getCache
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from gui.impl.lobby.gf_notifications.constants import GFNotificationTemplates

@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def pushGFNotification(gfTemplate, data, notificationGuiSettings=None, systemMessages=None):
    gfDataID = str(uuid.uuid4())
    getCache().setPayload(gfDataID, data)
    systemMessages.proto.serviceChannel.pushClientMessage({'data': {'gfDataID': gfDataID},
     'template': gfTemplate,
     'notificationGuiSettings': notificationGuiSettings if notificationGuiSettings else dict()}, msgType=SCH_CLIENT_MSG_TYPE.GF_SM_TYPE)
