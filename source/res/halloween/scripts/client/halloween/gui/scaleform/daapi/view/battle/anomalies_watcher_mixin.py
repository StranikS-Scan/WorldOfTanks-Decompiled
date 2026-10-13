# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/anomalies_watcher_mixin.py
from __future__ import absolute_import
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class AnomaliesWatcherMixin(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(AnomaliesWatcherMixin, self).__init__(*args, **kwargs)
        self.needToShow = False
        self.__isDisplayAllowed = True

    def updateVisibility(self):
        self.as_setVisibleS(self.__isDisplayAllowed and self.needToShow)

    @property
    def isDisplayAllowed(self):
        return self.__isDisplayAllowed

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def _populate(self):
        super(AnomaliesWatcherMixin, self)._populate()
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility += self.__onChangeAnomaliesViewVisibility

    def _dispose(self):
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility -= self.__onChangeAnomaliesViewVisibility
        super(AnomaliesWatcherMixin, self)._dispose()

    def __onChangeAnomaliesViewVisibility(self, isVisible):
        self.__isDisplayAllowed = not isVisible
        self.updateVisibility()
