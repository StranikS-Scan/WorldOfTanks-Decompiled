# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: newbie_start_page/scripts/client/NewbieStartPageComponent.py
import BigWorld
import AccountCommands

class NewbieStartPageComponent(BigWorld.StaticScriptComponent):

    def setInitialPlayerExperienceLevel(self, expLevel, callback=None):
        self.entity._doCmdInt(AccountCommands.CMD_SET_INITIAL_PLAYER_EXPERIENCE_LEVEL, expLevel, callback)
