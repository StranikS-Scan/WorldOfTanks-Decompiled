# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/postmortem_info_panel.py
from gui.impl.battle.postmortem_panel.postmortem_panel_view import PostmortemPanelView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.shared.system_factory import collectPostmortemInfoView
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class PostmortemInfoPanel(InjectComponentAdaptor):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _makeInjectView(self, *args):
        arenaGuiType = self.__sessionProvider.arenaVisitor.getArenaGuiType()
        viewCls = collectPostmortemInfoView(arenaGuiType)
        infoPanelViewCls = viewCls if viewCls is not None else PostmortemPanelView
        self.__view = infoPanelViewCls()
        return self.__view
