# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/presenters/base_child_presenter.py
from __future__ import absolute_import
from gui.impl.lobby.user_missions.hangar_widget.services import IUserMissionWidgetService
from helpers import dependency

class UserMissionChildPresenter(object):
    GROUP = ''
    _widgetService = dependency.descriptor(IUserMissionWidgetService)

    def isVisible(self):
        return True

    def _notifyVisibilityChanged(self):
        if not self.GROUP:
            return
        self._widgetService.setGroupVisibility(self.GROUP, self.isVisible())
