# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/overtime_panel.py
import BigWorld
import logging
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.cgf_components import wt_helpers
from white_tiger.gui.white_tiger_gui_constants import OVERTIME_COMPONENT_NAME
from gui.shared.utils.graphics import isLowPreset
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerOvertimeMeta import WhiteTigerOvertimeMeta
_logger = logging.getLogger(__name__)

class WhiteTigerOvertimePanel(WhiteTigerOvertimeMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(WhiteTigerOvertimePanel, self)._populate()
        self._setOvertimeInfo()
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        overtimeComp = getattr(componentSystem, OVERTIME_COMPONENT_NAME, None)
        if overtimeComp is None:
            _logger.error('Expected OvertimeComponent not present!')
            return
        else:
            overtimeComp.onOvertimeStart += self.__onOvertimeStart
            overtimeComp.onOvertimeOver += self.__onOvertimeEnd
            return

    def _dispose(self):
        super(WhiteTigerOvertimePanel, self)._dispose()
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        component = getattr(componentSystem, OVERTIME_COMPONENT_NAME, None)
        if component is not None:
            component.onOvertimeStart -= self.__onOvertimeStart
            component.onOvertimeOver -= self.__onOvertimeEnd
        return

    def __onOvertimeStart(self, endTime):
        timeLeft = int(endTime - BigWorld.serverTime())
        self.as_updateOvertimeTimerS(timeLeft)

    def __onOvertimeEnd(self):
        self.as_updateOvertimeTimerS(0)

    def _setOvertimeInfo(self):
        self.as_getOvertimeInfoS(wt_helpers.isBoss(), isLowPreset())
