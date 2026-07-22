# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/server_events/__init__.py
from gui.shared.system_factory import registerQuestBuilder
from tank_academy.gui.server_events.event_items import TankAcademyGroupQuestBuilder, TankAcademyTokenQuestBuilder, TankAcademyQuestBuilder

def registerTankAcademyQuests():
    registerQuestBuilder(TankAcademyQuestBuilder, index=0)
    registerQuestBuilder(TankAcademyTokenQuestBuilder, index=0)
    registerQuestBuilder(TankAcademyGroupQuestBuilder, index=0)
