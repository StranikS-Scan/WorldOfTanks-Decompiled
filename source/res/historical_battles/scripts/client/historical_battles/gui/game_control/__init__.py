# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/game_control/__init__.py
from historical_battles.gui.game_control.awards_controller import HBProgressionStageHandler, HBLastAwardHandler
from historical_battles.gui.gui_constants import SM_TYPE_HB_PROGRESSION
from chat_shared import SYS_MESSAGE_TYPE
from gui.shared.system_factory import registerAwardControllerHandler
from soft_exception import SoftException

def registerHBProgressionAwardControllers():
    try:
        SYS_MESSAGE_TYPE.__getattr__(SM_TYPE_HB_PROGRESSION).index()
    except AttributeError:
        raise SoftException('No index for {attr} found. Use registerSystemMessagesTypes before')

    registerAwardControllerHandler(HBProgressionStageHandler)
    registerAwardControllerHandler(HBLastAwardHandler)
