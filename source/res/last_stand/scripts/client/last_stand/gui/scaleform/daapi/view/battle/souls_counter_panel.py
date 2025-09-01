# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/souls_counter_panel.py
import weakref
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils.graphics import isLowPreset
from last_stand.gui.scaleform.daapi.view.meta.PointCounterMeta import PointCounterMeta
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID

class LSSoulsCounter(PointCounterMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LSSoulsCounter, self).__init__()
        self.prevSoulsCount = 0
        self.capacity = -1
        self._soulsContainer = None
        return

    def _populate(self):
        super(LSSoulsCounter, self)._populate()
        lsBattleGuiCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onSoulsContainerReady += self._onSoulsContainerReady

    def _dispose(self):
        lsBattleGuiCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onSoulsContainerReady -= self._onSoulsContainerReady
        soulsContainer = self._soulsContainer() if self._soulsContainer is not None else None
        if soulsContainer is not None:
            soulsContainer.onChangeSoulsCount -= self.__onSoulsChanged
        self._soulsContainer = None
        super(LSSoulsCounter, self)._dispose()
        return

    def _onSoulsContainerReady(self, vehicleSoulsContainer):
        self._soulsContainer = weakref.ref(vehicleSoulsContainer)
        lsBattleGuiCtrl = self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)
        if lsBattleGuiCtrl:
            lsBattleGuiCtrl.onSoulsContainerReady -= self._onSoulsContainerReady
        self.__enableAnimation()
        self.capacity = vehicleSoulsContainer.capacity
        self.as_setSoulsCapS(vehicleSoulsContainer.capacity)
        self.__onSoulsChanged(vehicleSoulsContainer.souls, 0)
        vehicleSoulsContainer.onChangeSoulsCount += self.__onSoulsChanged

    def __onSoulsChanged(self, newCount, reason):
        vehicleSoulsContainer = self._soulsContainer()
        if vehicleSoulsContainer and self.capacity != vehicleSoulsContainer.capacity:
            self.capacity = vehicleSoulsContainer.capacity
            self.as_setSoulsCapS(self.capacity)
        self.as_updateCountS(newCount, reason)
        if newCount > self.prevSoulsCount:
            self.__sessionProvider.shared.messages.onShowPlayerMessageByKey('LS_PICKUP_SOULS', {'souls': newCount - self.prevSoulsCount})
        self.prevSoulsCount = newCount

    def __enableAnimation(self):
        self.as_enableAnimationS(not isLowPreset())
