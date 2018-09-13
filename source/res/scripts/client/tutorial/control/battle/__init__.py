# Embedded file name: scripts/client/tutorial/control/battle/__init__.py
from tutorial.data.chapter import Effect
from tutorial.control import ControlsFactory, functional as core_func
from tutorial.control.battle import functional
from tutorial.control.battle import context

class BattleControlsFactory(ControlsFactory):

    def __init__(self):
        funcEffects = {Effect.ACTIVATE: core_func.FunctionalActivateEffect,
         Effect.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         Effect.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         Effect.FINISH_TRAINING: core_func.FunctionalFinishTrainingEffect,
         Effect.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         Effect.SHOW_MESSAGE: core_func.FunctionalShowMessageEffect,
         Effect.INVOKE_PLAYER_CMD: core_func.FunctionalPlayerCommandEffect,
         Effect.SHOW_DIALOG: functional.FunctionalShowBattleDialogEffect,
         Effect.REQUEST_BONUS: functional.FunctionalRequestBonusEffect,
         Effect.NEXT_CHAPTER: functional.FunctionalNextChapterEffect,
         Effect.SHOW_MARKER: functional.FunctionalShowMarker,
         Effect.REMOVE_MARKER: functional.FunctionalRemoveMarker,
         Effect.NEXT_TASK: functional.FunctionalNextTaskEffect,
         Effect.SHOW_HINT: functional.FunctionalShowHintEffect,
         Effect.TELEPORT: functional.FunctionalTeleportEffect,
         Effect.SHOW_GREETING: functional.FunctionalShowGreeting,
         Effect.REFUSE_TRAINING: functional.FunctionalRefuseTrainingEffect,
         Effect.ENABLE_CAMERA_ZOOM: functional.FunctionalEnableCameraZoomEffect,
         Effect.DISABLE_CAMERA_ZOOM: functional.FunctionalDisableCameraZoomEffect}
        ControlsFactory.__init__(self, funcEffects, {})

    def createBonuses(self, completed):
        return context.BattleBonusesRequester(completed)

    def createSoundPlayer(self):
        return context.BattleSoundPlayer()

    def createFuncScene(self, sceneModel):
        return functional.FunctionalBattleScene(sceneModel)

    def createFuncInfo(self):
        return functional.FunctionalBattleChapterInfo()
