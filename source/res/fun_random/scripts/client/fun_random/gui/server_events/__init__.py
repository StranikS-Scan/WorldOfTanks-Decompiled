# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/server_events/__init__.py
from fun_random.gui.server_events.event_items import FunProgressionTriggerQuestBuilder
from gui.shared.system_factory import registerQuestBuilder

def registerFunRandomQuests():
    registerQuestBuilder(FunProgressionTriggerQuestBuilder)
