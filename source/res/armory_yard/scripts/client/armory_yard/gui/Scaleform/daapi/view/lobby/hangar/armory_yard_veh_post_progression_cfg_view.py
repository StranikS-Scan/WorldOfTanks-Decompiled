# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/hangar/armory_yard_veh_post_progression_cfg_view.py
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_cfg_view import VehiclePostProgressionCfgView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.veh_post_progression.sounds import PP_VIEW_SOUND_SPACE
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController
from gui.shared.event_dispatcher import showHangar

class ArmoryYardVehiclePostProgressionCfgView(VehiclePostProgressionCfgView):
    _COMMON_SOUND_SPACE = PP_VIEW_SOUND_SPACE
    _PROGRESSION_INJECT_ALIAS = HANGAR_ALIASES.POST_PROGRESSION_INJECT
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, ctx=None):
        super(ArmoryYardVehiclePostProgressionCfgView, self).__init__(ctx)
        self.__isExit = False

    @property
    def alias(self):
        return VIEW_ALIAS.VEH_POST_PROGRESSION

    def _onExit(self):
        self.__isExit = True
        super(ArmoryYardVehiclePostProgressionCfgView, self)._onExit()

    def __checkExit(self):
        if not self.__armoryYardCtrl.isActive():
            self.__armoryYardCtrl.unloadScene()
            self.destroy()
            showHangar()

    def _populate(self):
        super(ArmoryYardVehiclePostProgressionCfgView, self)._populate()
        self.__armoryYardCtrl.updateVisibilityHangarHeaderMenu()
        self.__armoryYardCtrl.onUpdated += self.__checkExit

    def _dispose(self):
        self.__armoryYardCtrl.onUpdated -= self.__checkExit
        self.__armoryYardCtrl.updateVisibilityHangarHeaderMenu(isVisible=True)
        if not self.__isExit:
            self.__armoryYardCtrl.unloadScene()
        super(ArmoryYardVehiclePostProgressionCfgView, self)._dispose()
