# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/wt_event_countdown_entry_point.py
from adisp import process
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.daapi.view.meta.WTEventEntryPointMeta import WTEventEntryPointMeta
from helpers import dependency, time_utils
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGameEventController
_EXTENDED_RENDER_PIPELINE_SETTING = 0

class WTEventCountdownEntryPoint(WTEventEntryPointMeta):
    _settingsCore = dependency.descriptor(ISettingsCore)
    __gameEventController = dependency.descriptor(IGameEventController)

    def _populate(self):
        super(WTEventCountdownEntryPoint, self)._populate()
        renderPipelineSetting = self._settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        isAnimationEnabled = renderPipelineSetting == _EXTENDED_RENDER_PIPELINE_SETTING
        self.as_setAnimationEnabledS(isAnimationEnabled)
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__setEndDate()

    def _dispose(self):
        self._settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(WTEventCountdownEntryPoint, self)._dispose()

    def onEntryClick(self):
        self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)

    def __onSettingsChanged(self, diff):
        if GRAPHICS.RENDER_PIPELINE in diff:
            isAnimationEnabled = diff.get(GRAPHICS.RENDER_PIPELINE)
            self.as_setAnimationEnabledS(isAnimationEnabled)

    def __setEndDate(self):
        endDate = None
        currentSeason = self.__gameEventController.getCurrentSeason()
        if currentSeason is not None:
            endDate = currentSeason.getEndDate()
        if endDate is None:
            return
        else:
            timeStruct = time_utils.getTimeStructInUTC(endDate)
            endDateText = backport.text(R.strings.wt_event.WTEventsEntryWidgetView.date(), day=str(timeStruct.tm_mday), month=backport.text(R.strings.menu.dateTime.months.num(timeStruct.tm_mon)()))
            self.as_setEndDateS(endDateText)
            return

    @process
    def __doSelectAction(self, actionName):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            yield dispatcher.doSelectAction(PrbAction(actionName))
        return
