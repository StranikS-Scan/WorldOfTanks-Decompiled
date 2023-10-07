# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/crew_panel_inject.py
from gui.Scaleform.daapi.view.meta.CrewPanelInjectMeta import CrewPanelInjectMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.prb_control.entities.listener import IGlobalListener

class CrewPanelInject(InjectComponentAdaptor, CrewPanelInjectMeta, IGlobalListener):

    def _makeInjectView(self):
        from gui.impl.lobby.crew.hangar_crew_widget import HangarCrewWidget
        return HangarCrewWidget()

    def updateTankmen(self):
        self._injectView.updateTankmen()
