# Embedded file name: scripts/client/tutorial/control/offbattle/__init__.py
from tutorial.data.effects import EFFECT_TYPE
from tutorial.control import ControlsFactory
from tutorial.control import context as core_ctx
from tutorial.control import functional as core_func
from tutorial.control.lobby import functional as lobby_func
from tutorial.control.offbattle import context
from tutorial.control.offbattle import functional
from tutorial.control.offbattle import queries

class OffbattleControlsFactory(ControlsFactory):

    def __init__(self):
        effects = {EFFECT_TYPE.ACTIVATE: core_func.FunctionalActivateEffect,
         EFFECT_TYPE.DEACTIVATE: core_func.FunctionalDeactivateEffect,
         EFFECT_TYPE.GLOBAL_ACTIVATE: core_func.FunctionalGlobalActivateEffect,
         EFFECT_TYPE.GLOBAL_DEACTIVATE: core_func.FunctionalGlobalDeactivateEffect,
         EFFECT_TYPE.RUN_TRIGGER: core_func.FunctionalRunTriggerEffect,
         EFFECT_TYPE.REQUEST_BONUS: core_func.FunctionalRequestBonusEffect,
         EFFECT_TYPE.INVOKE_PLAYER_CMD: core_func.FunctionalPlayerCommandEffect,
         EFFECT_TYPE.SHOW_DIALOG: core_func.FunctionalShowDialogEffect,
         EFFECT_TYPE.SHOW_WINDOW: core_func.FunctionalShowWindowEffect,
         EFFECT_TYPE.SHOW_MESSAGE: functional.FunctionalShowMessage4QueryEffect,
         EFFECT_TYPE.REFUSE_TRAINING: functional.FunctionalRefuseTrainingEffect,
         EFFECT_TYPE.REQUEST_ALL_BONUSES: functional.FunctionalRequestAllBonusesEffect,
         EFFECT_TYPE.ENTER_QUEUE: functional.FunctionalEnterQueueEffect,
         EFFECT_TYPE.EXIT_QUEUE: functional.FunctionalExitQueueEffect,
         EFFECT_TYPE.PLAY_MUSIC: functional.FunctionalPlayMusicEffect,
         EFFECT_TYPE.OPEN_INTERNAL_BROWSER: functional.FunctionalOpenInternalBrowser}
        _queries = {'greeting': queries.GreetingContent,
         'queue': queries.TutorialQueueText,
         'final': queries.BattleFinalStatistic,
         'resultMessage': queries.BattleResultMessage}
        ControlsFactory.__init__(self, effects, _queries)

    def createBonuses(self, completed):
        return context.OffbattleBonusesRequester(completed)

    def createSoundPlayer(self):
        return core_ctx.NoSound()

    def createFuncScene(self, sceneModel):
        return core_func.FunctionalScene(sceneModel)

    def createFuncInfo(self):
        return lobby_func.FunctionalLobbyChapterInfo()
