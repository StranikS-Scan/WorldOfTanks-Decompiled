# Embedded file name: scripts/client/tutorial/control/lobby/__init__.py
from tutorial.control import ControlsFactory, functional as core_func
from tutorial.control import context as core_ctx
from tutorial.control.lobby import functional
from tutorial.control.lobby import context
from tutorial.control.lobby import queries
from tutorial.data.chapter import Effect

class LobbyControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {Effect.ACTIVATE: core_func.FunctionalActivateEffect,
         Effect.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         Effect.SHOW_HINT: functional.FunctionalShowHintEffect,
         Effect.CLOSE_HINT: functional.FunctionalCloseHintEffect,
         Effect.SHOW_DIALOG: core_func.FunctionalShowDialogEffect,
         Effect.REFUSE_TRAINING: core_func.FunctionalRefuseTrainingEffect,
         Effect.NEXT_CHAPTER: core_func.FunctionalNextChapterEffect,
         Effect.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         Effect.REQUEST_BONUS: core_func.FunctionalRequestBonusEffect,
         Effect.SET_ITEM_PROPS: core_func.FunctionalGuiItemSetPropertiesEffect,
         Effect.FINISH_TRAINING: core_func.FunctionalFinishTrainingEffect,
         Effect.DEFINE_GUI_ITEM: core_func.FunctionalDefineGuiItem,
         Effect.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         Effect.SET_FILTER: functional.FunctionalSetFilterEffect,
         Effect.SHOW_MESSAGE: core_func.FunctionalShowMessageEffect}
        _queries = {'vehicleItemInfo': queries.VehicleItemParams,
         'tankmanSkill': queries.TankmanSkillParams}
        ControlsFactory.__init__(self, effects, _queries)

    def createBonuses(self, completed):
        return context.LobbyBonusesRequester(completed)

    def createSoundPlayer(self):
        return core_ctx.NoSound()

    def createFuncScene(self, sceneModel):
        return core_func.FunctionalScene(sceneModel)

    def createFuncInfo(self):
        return functional.FunctionalLobbyChapterInfo()
