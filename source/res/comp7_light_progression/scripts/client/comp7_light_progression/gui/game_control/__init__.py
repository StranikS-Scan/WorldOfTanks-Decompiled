# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/gui/game_control/__init__.py
from comp7_light_progression.gui.game_control.awards_controller import Comp7LightProgressionStageHandler
from comp7_light_progression.gui.game_control.progression_controller import Comp7LightProgressionController
from comp7_light_progression.gui.gui_constants import SM_TYPE_COMP7_LIGHT_PROGRESSION
from chat_shared import SYS_MESSAGE_TYPE
from gui.shared.system_factory import registerAwardControllerHandler, registerGameControllers
from soft_exception import SoftException

def registerComp7LightGameControllers():
    from comp7_light_progression.skeletons.game_controller import IComp7LightProgressionOnTokensController
    registerGameControllers([(IComp7LightProgressionOnTokensController, Comp7LightProgressionController, False)])


def registerComp7LightProgressionAwardControllers():
    try:
        SYS_MESSAGE_TYPE.__getattr__(SM_TYPE_COMP7_LIGHT_PROGRESSION).index()
    except AttributeError:
        raise SoftException('No index for {attr} found. Use registerSystemMessagesTypes before')

    registerAwardControllerHandler(Comp7LightProgressionStageHandler)
