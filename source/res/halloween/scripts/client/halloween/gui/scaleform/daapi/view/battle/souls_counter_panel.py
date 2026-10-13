# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/souls_counter_panel.py
from __future__ import absolute_import
import weakref
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils.graphics import isLowPreset
from halloween.gui.scaleform.daapi.view.meta.PointCounterMeta import PointCounterMeta
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID

class HWSoulsCounter(PointCounterMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __INFINITE_CAPACITY = 1000

    def __init__(self):
        super(HWSoulsCounter, self).__init__()
        self.prevSoulsCount = 0
        self.capacity = -1
        self._soulsContainer = None
        return

    def _populate(self):
        super(HWSoulsCounter, self)._populate()
        hwBattleGuiCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onSoulsContainerReady += self._onSoulsContainerReady

    def _dispose(self):
        hwBattleGuiCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onSoulsContainerReady -= self._onSoulsContainerReady
        soulsContainer = self._soulsContainer() if self._soulsContainer is not None else None
        if soulsContainer is not None:
            soulsContainer.onChangeSoulsCount -= self.__onSoulsChanged
        self._soulsContainer = None
        super(HWSoulsCounter, self)._dispose()
        return

    def _onSoulsContainerReady(self, vehicleSoulsContainer):
        self._soulsContainer = weakref.ref(vehicleSoulsContainer)
        hwBattleGuiCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onSoulsContainerReady -= self._onSoulsContainerReady
        self.__enableAnimation()
        self.capacity = vehicleSoulsContainer.capacity
        self._updateSoulsCaps(vehicleSoulsContainer.capacity)
        self.__onSoulsChanged(vehicleSoulsContainer.souls, 0)
        vehicleSoulsContainer.onChangeSoulsCount += self.__onSoulsChanged

    def _updateSoulsCaps(self, capacity):
        self.as_setSoulsCapS(capacity if capacity < self.__INFINITE_CAPACITY else 1)

    def __onSoulsChanged(self, newCount, reason):
        vehicleSoulsContainer = self._soulsContainer()
        if vehicleSoulsContainer and self.capacity != vehicleSoulsContainer.capacity:
            self.capacity = vehicleSoulsContainer.capacity
            self._updateSoulsCaps(self.capacity)
        self.as_updateCountS(newCount, reason)
        if newCount > self.prevSoulsCount:
            self.__sessionProvider.shared.messages.onShowPlayerMessageByKey('PICKUP_SOULS', {'souls': newCount - self.prevSoulsCount})
        self.prevSoulsCount = newCount

    def __enableAnimation(self):
        self.as_enableAnimationS(not isLowPreset())
