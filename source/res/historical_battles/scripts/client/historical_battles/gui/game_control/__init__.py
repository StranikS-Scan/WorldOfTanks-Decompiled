# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/game_control/__init__.py
from chat_shared import SYS_MESSAGE_TYPE
from gui.shared.system_factory import registerAwardControllerHandlers
from soft_exception import SoftException
from historical_battles.gui.game_control.awards_controller import HBProgressionStageHandler, HBQuestsAwardHandler, HBFairplayHandler
from historical_battles.gui.gui_constants import SM_TYPE_HB_PROGRESSION

def registerHBProgressionAwardControllers():
    try:
        SYS_MESSAGE_TYPE.__getattr__(SM_TYPE_HB_PROGRESSION).index()
    except AttributeError:
        raise SoftException('No index for {attr} found. Use registerSystemMessagesTypes before')

    registerAwardControllerHandlers((HBProgressionStageHandler, HBQuestsAwardHandler, HBFairplayHandler))
