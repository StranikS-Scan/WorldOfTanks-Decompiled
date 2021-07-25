# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_view_adaptor.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.veh_post_progression.post_progression_cfg_component import PostProgressionCfgComponentView
from gui.impl.lobby.veh_post_progression.post_progression_cmp_component import PostProgressionCmpComponentView

class VehiclePostProgressionViewAdaptor(InjectComponentAdaptor):
    __slots__ = ('__ctx',)

    def __init__(self, ctx):
        super(VehiclePostProgressionViewAdaptor, self).__init__()
        self.__ctx = ctx

    def _makeInjectView(self):
        parentAlias = self.__ctx['parentAlias']
        if parentAlias == VIEW_ALIAS.VEH_POST_PROGRESSION:
            return PostProgressionCfgComponentView(**self.__ctx)
        return PostProgressionCmpComponentView(**self.__ctx) if parentAlias == VIEW_ALIAS.VEH_POST_PROGRESSION_CMP else None
