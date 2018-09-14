# Embedded file name: scripts/client/tutorial/control/lobby/__init__.py
from tutorial.control import ControlsFactory, functional as core_func
from tutorial.control import context as core_ctx
from tutorial.control.lobby import functional
from tutorial.control.lobby import context
from tutorial.control.lobby import queries
from tutorial.data.effects import EFFECT_TYPE

class LobbyControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {EFFECT_TYPE.ACTIVATE: core_func.FunctionalActivateEffect,
         EFFECT_TYPE.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         EFFECT_TYPE.SHOW_HINT: functional.FunctionalShowHintEffect,
         EFFECT_TYPE.CLOSE_HINT: functional.FunctionalCloseHintEffect,
         EFFECT_TYPE.SHOW_DIALOG: core_func.FunctionalShowDialogEffect,
         EFFECT_TYPE.REFUSE_TRAINING: core_func.FunctionalRefuseTrainingEffect,
         EFFECT_TYPE.NEXT_CHAPTER: core_func.FunctionalNextChapterEffect,
         EFFECT_TYPE.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         EFFECT_TYPE.REQUEST_BONUS: core_func.FunctionalRequestBonusEffect,
         EFFECT_TYPE.SET_ITEM_PROPS: core_func.FunctionalGuiItemSetPropertiesEffect,
         EFFECT_TYPE.FINISH_TRAINING: core_func.FunctionalFinishTrainingEffect,
         EFFECT_TYPE.INVOKE_GUI_CMD: core_func.FunctionalGuiCommandEffect,
         EFFECT_TYPE.SHOW_MESSAGE: core_func.FunctionalShowMessageEffect}
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
