# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/postmortem_info_panel.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.battle.postmortem_panel.postmortem_panel_view import PostmortemPanelView

class PostmortemInfoPanel(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = PostmortemPanelView()
        return self.__view
