# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/plugins/__init__.py
from __future__ import absolute_import
from helpers import dependency
from gui.impl.lobby.user_missions.hangar_widget.services import IMissionsContainerService

class IUserMissionPlugin(object):
    _missionsContainerService = dependency.descriptor(IMissionsContainerService)

    @classmethod
    def getPathToResource(cls):
        raise NotImplementedError

    @classmethod
    def getDependencies(cls):
        raise NotImplementedError

    @classmethod
    def getViewAlias(cls):
        raise NotImplementedError

    @classmethod
    def isPluginEnabled(cls):
        raise NotImplementedError

    @classmethod
    def startListening(cls):
        raise NotImplementedError

    @classmethod
    def stopListening(cls):
        raise NotImplementedError

    @classmethod
    def _onUpdate(cls, *args, **kwargs):
        raise NotImplementedError
