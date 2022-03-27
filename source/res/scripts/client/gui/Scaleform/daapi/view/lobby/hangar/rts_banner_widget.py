# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/rts_banner_widget.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.rts.tutorial.rts_tutorial_banner_view import RTSTutorialBannerView

class RTSBannerWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return RTSTutorialBannerView()
