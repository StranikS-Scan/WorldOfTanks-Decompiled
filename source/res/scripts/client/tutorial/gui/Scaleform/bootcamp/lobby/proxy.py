# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/bootcamp/lobby/proxy.py
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.gui.Scaleform import effects_player as shared_effects
from tutorial.gui.Scaleform.lobby import SfLobbyProxy
from tutorial.gui.Scaleform.bootcamp.lobby import settings, effects as bc_effects

class SfBootcampLobbyProxy(SfLobbyProxy):

    def __init__(self):
        effects = {GUI_EFFECT_NAME.SHOW_WINDOW: shared_effects.ShowWindowEffect(settings.WINDOW_ALIAS_MAP),
         GUI_EFFECT_NAME.SHOW_DIALOG: shared_effects.ShowDialogEffect(settings.DIALOG_ALIAS_MAP, settings.GAMEFACE_ALIAS_MAP),
         GUI_EFFECT_NAME.SET_CRITERIA: shared_effects.SetCriteriaEffect(),
         GUI_EFFECT_NAME.SET_VIEW_CRITERIA: shared_effects.SetViewCriteriaEffect(),
         GUI_EFFECT_NAME.SET_TRIGGER: shared_effects.SetTriggerEffect(),
         GUI_EFFECT_NAME.SET_ITEM_PROPS: shared_effects.SetItemPropsEffect(),
         GUI_EFFECT_NAME.PLAY_ANIMATION: shared_effects.PlayAnimationEffect(),
         GUI_EFFECT_NAME.SHOW_HINT: bc_effects.ShowHint()}
        super(SfBootcampLobbyProxy, self).__init__(shared_effects.EffectsPlayer(effects))

    def getViewSettings(self):
        return settings.BOOTCAMP_LOBBY_VIEW_SETTINGS
