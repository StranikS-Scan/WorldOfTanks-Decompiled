# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/__init__.py


def registerComp7LightLobby():
    from comp7_light_constants import PREBATTLE_TYPE
    from comp7_light.gui.comp7_light_constants import SELECTOR_BATTLE_TYPES
    from comp7_light.gui.game_control.award_controller import Comp7LightProgressionStageHandler, Comp7LightPunishWindowHandler
    from gui.game_control.platoon_controller import PlatoonController
    from gui.Scaleform.daapi.view.lobby.formatters.tooltips import _MODENAME_TO_PO_FILE
    from gui.shared.system_factory import registerAwardControllerHandlers
    registerAwardControllerHandlers((Comp7LightProgressionStageHandler, Comp7LightPunishWindowHandler))
    PlatoonController.SQUAD_SIZE_SELECT_PREBATTLE_TYPES.append(PREBATTLE_TYPE.COMP7_LIGHT)
    _MODENAME_TO_PO_FILE.update({SELECTOR_BATTLE_TYPES.COMP7_LIGHT: 'comp7_light'})
