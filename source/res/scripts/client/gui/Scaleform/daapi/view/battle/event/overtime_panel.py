# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/overtime_panel.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.meta.EventOvertimeMeta import EventOvertimeMeta
from cgf_components import wt_helpers
from gui.shared.utils.graphics import isRendererPipelineDeferred

class EventOvertimePanel(EventOvertimeMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(EventOvertimePanel, self)._populate()
        feedback = self.sessionProvider.shared.feedback
        self._setOvertimeInfo()
        if feedback is not None:
            feedback.onOvertime += self.__onOvertimeNotification
        return

    def _dispose(self):
        super(EventOvertimePanel, self)._dispose()
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onOvertime -= self.__onOvertimeNotification
        return

    def __onOvertimeNotification(self, overtimeDuration):
        self.as_updateOvertimeTimerS(overtimeDuration)

    def _setOvertimeInfo(self):
        self.as_getOvertimeInfoS(wt_helpers.isBoss(), isRendererPipelineDeferred() is False)
