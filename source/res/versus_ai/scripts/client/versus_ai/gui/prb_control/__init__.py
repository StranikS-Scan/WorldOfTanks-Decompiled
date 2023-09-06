# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/prb_control/__init__.py
from constants import QUEUE_TYPE
from gui.shared.system_factory import registerPrbStorage
from gui.prb_control.storages import makeQueueName
from versus_ai.gui.prb_control.storages.versus_ai_storage import VersusAIStorage

def registerVersusAIStorage():
    registerPrbStorage(makeQueueName(QUEUE_TYPE.VERSUS_AI), VersusAIStorage())
