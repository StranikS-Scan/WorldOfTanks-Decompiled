# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/crew_xp_panel_inject.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.crew.crew_header_view import CrewHeaderView
from gui.Scaleform.daapi.view.meta.CrewXPPanelInjectMeta import CrewXPPanelInjectMeta
from gui.prb_control.entities.listener import IGlobalListener

class CrewXPPanelInject(InjectComponentAdaptor, CrewXPPanelInjectMeta, IGlobalListener):

    def _makeInjectView(self):
        return CrewHeaderView()
