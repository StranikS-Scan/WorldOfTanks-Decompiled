# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/game_control/__init__.py
from battle_royale_progression.gui.game_control.awards_controller import BRProgressionStageHandler
from battle_royale_progression.gui.game_control.progression_controller import BRProgressionController
from chat_shared import SYS_MESSAGE_TYPE
from gui.shared.system_factory import registerAwardControllerHandler, registerGameControllers
from soft_exception import SoftException

def registerBRGameControllers():
    from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
    registerGameControllers([(IBRProgressionOnTokensController, BRProgressionController, False)])


def registerBRProgressionAwardControllers():
    try:
        SYS_MESSAGE_TYPE.BRProgressionNotification.index()
    except AttributeError:
        raise SoftException('No index for {attr} found. Use registerSystemMessagesTypes before')

    registerAwardControllerHandler(BRProgressionStageHandler)
