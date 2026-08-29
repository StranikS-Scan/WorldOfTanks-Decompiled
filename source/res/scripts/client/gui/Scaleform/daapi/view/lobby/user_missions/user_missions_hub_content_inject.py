# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/user_missions/user_missions_hub_content_inject.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.meta.UserMissionsHubContentInjectMeta import UserMissionsHubContentInjectMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor

class UserMissionsHubContentInject(InjectComponentAdaptor, UserMissionsHubContentInjectMeta):

    def __init__(self, tabID, questId, challengeId):
        super(UserMissionsHubContentInject, self).__init__()
        self.tabID = tabID
        self.questId = questId
        self.challengeId = challengeId

    def _makeInjectView(self):
        from gui.impl.lobby.user_missions.hub.hub_view import HubView
        return HubView(self.tabID, self.questId, self.challengeId)
