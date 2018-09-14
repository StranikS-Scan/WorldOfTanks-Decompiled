# Embedded file name: scripts/client/tutorial/control/battle/__init__.py
from tutorial.data.effects import EFFECT_TYPE
from tutorial.control import ControlsFactory, functional as core_func
from tutorial.control.battle import functional
from tutorial.control.battle import context

class BattleControlsFactory(ControlsFactory):

    def __init__(self):
        funcEffects = {EFFECT_TYPE.ACTIVATE: core_func.FunctionalActivateEffect,
         EFFECT_TYPE.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         EFFECT_TYPE.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         EFFECT_TYPE.FINISH_TRAINING: core_func.FunctionalFinishTrainingEffect,
         EFFECT_TYPE.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         EFFECT_TYPE.SHOW_MESSAGE: core_func.FunctionalShowMessageEffect,
         EFFECT_TYPE.INVOKE_PLAYER_CMD: core_func.FunctionalPlayerCommandEffect,
         EFFECT_TYPE.SHOW_DIALOG: functional.FunctionalShowBattleDialogEffect,
         EFFECT_TYPE.REQUEST_BONUS: functional.FunctionalRequestBonusEffect,
         EFFECT_TYPE.NEXT_CHAPTER: functional.FunctionalNextChapterEffect,
         EFFECT_TYPE.SHOW_MARKER: functional.FunctionalShowMarker,
         EFFECT_TYPE.REMOVE_MARKER: functional.FunctionalRemoveMarker,
         EFFECT_TYPE.NEXT_TASK: functional.FunctionalNextTaskEffect,
         EFFECT_TYPE.SHOW_HINT: functional.FunctionalShowHintEffect,
         EFFECT_TYPE.TELEPORT: functional.FunctionalTeleportEffect,
         EFFECT_TYPE.SHOW_GREETING: functional.FunctionalShowGreeting,
         EFFECT_TYPE.REFUSE_TRAINING: functional.FunctionalRefuseTrainingEffect,
         EFFECT_TYPE.ENABLE_CAMERA_ZOOM: functional.FunctionalEnableCameraZoomEffect,
         EFFECT_TYPE.DISABLE_CAMERA_ZOOM: functional.FunctionalDisableCameraZoomEffect}
        ControlsFactory.__init__(self, funcEffects, {})

    def createBonuses(self, completed):
        return context.BattleBonusesRequester(completed)

    def createSoundPlayer(self):
        return context.BattleSoundPlayer()

    def createFuncScene(self, sceneModel):
        return functional.FunctionalBattleScene(sceneModel)

    def createFuncInfo(self):
        return functional.FunctionalBattleChapterInfo()
