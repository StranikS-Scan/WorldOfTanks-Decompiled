# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/page/comp7_platoon_presenter.py
from __future__ import absolute_import
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.page.platoon_presenter import PlatoonPresenter
from gui.prb_control import prb_getters
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController, IComp7Controller

class Comp7PlatoonPresenter(PlatoonPresenter):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def _getEvents(self):
        events = [(self.__comp7Controller.onQualificationStateUpdated, self._onUpdatePlatoon), (self.__comp7Controller.onModeConfigChanged, self._onUpdatePlatoon), (self.__comp7Controller.onBanUpdated, self._onUpdatePlatoon)]
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr is not None and unitMgr.unit is not None:
            events.append((unitMgr.unit.onSquadSizeChanged, self._onUpdatePlatoon))
        events.extend(super(Comp7PlatoonPresenter, self)._getEvents())
        return events

    def _initialize(self, *args, **kwargs):
        super(Comp7PlatoonPresenter, self)._initialize(args, kwargs)
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryUpdate})

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(Comp7PlatoonPresenter, self)._finalize()

    def _onInventoryUpdate(self, *args):
        self._onUpdatePlatoon()
