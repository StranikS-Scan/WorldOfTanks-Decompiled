# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCAmmunitionPanel.py
from gui.Scaleform.daapi.view.lobby.hangar.AmmunitionPanel import AmmunitionPanel
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class BCAmmunitionPanel(AmmunitionPanel):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(BCAmmunitionPanel, self).__init__()
        self._observer = None
        return

    def updateVisibleComponents(self, visibleSettings):
        if self._observer is not None:
            self._observer.as_setBootcampDataS(visibleSettings)
        return

    def showNewElements(self, newElements):
        if self._observer is not None:
            self._observer.as_showAnimatedS(newElements)
        return

    def _populate(self):
        super(BCAmmunitionPanel, self)._populate()
        self._observer = self.app.bootcampManager.getObserver('BCAmmunitionPanelObserver')
        if self._observer is not None:
            visibleSettings = self.bootcampCtrl.getLobbySettings()
            self._observer.as_setBootcampDataS(visibleSettings)
        return

    def _dispose(self):
        self._observer = None
        super(BCAmmunitionPanel, self)._dispose()
        return
