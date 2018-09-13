# Embedded file name: scripts/client/tutorial/control/offbattle/__init__.py
from tutorial.data.chapter import Effect
from tutorial.control import ControlsFactory
from tutorial.control import context as core_ctx
from tutorial.control import functional as core_func
from tutorial.control.lobby import functional as lobby_func
from tutorial.control.offbattle import context
from tutorial.control.offbattle import functional
from tutorial.control.offbattle import queries

class OffbattleControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {Effect.ACTIVATE: core_func.FunctionalActivateEffect,
         Effect.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         Effect.GLOBAL_ACTIVATE: core_func.FunctionalGlobalActivateEffect,
         Effect.GLOBAL_DEACTIVATE: core_func.FunctionalGlobalDeactivateEffect,
         Effect.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         Effect.REQUEST_BONUS: core_func.FunctionalRequestBonusEffect,
         Effect.INVOKE_PLAYER_CMD: core_func.FunctionalPlayerCommandEffect,
         Effect.SHOW_DIALOG: core_func.FunctionalShowDialogEffect,
         Effect.SHOW_WINDOW: core_func.FunctionalShowWindowEffect,
         Effect.SHOW_MESSAGE: functional.FunctionalShowMessage4QueryEffect,
         Effect.REFUSE_TRAINING: functional.FunctionalRefuseTrainingEffect,
         Effect.REQUEST_ALL_BONUSES: functional.FunctionalRequestAllBonusesEffect,
         Effect.ENTER_QUEUE: functional.FunctionalEnterQueueEffect,
         Effect.EXIT_QUEUE: functional.FunctionalExitQueueEffect,
         Effect.PLAY_MUSIC: functional.FunctionalPlayMusicEffect}
        _queries = {'greeting': queries.GreetingContent,
         'queue': queries.TutorialQueueText,
         'final': queries.BattleFinalStatistic,
         'resultMessage': queries.BattleResultMessage,
         'video': queries.VideoContent}
        ControlsFactory.__init__(self, effects, _queries)

    def createBonuses(self, completed):
        return context.OffbattleBonusesRequester(completed)

    def createSoundPlayer(self):
        return core_ctx.NoSound()

    def createFuncScene(self, sceneModel):
        return core_func.FunctionalScene(sceneModel)

    def createFuncInfo(self):
        return lobby_func.FunctionalLobbyChapterInfo()
