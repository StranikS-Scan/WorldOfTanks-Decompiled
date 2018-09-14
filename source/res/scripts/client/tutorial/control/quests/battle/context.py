# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/quests/battle/context.py
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.settings_constants import TUTORIAL
from constants import ARENA_GUI_TYPE, IS_DEVELOPMENT
from gui.battle_control import arena_info
from tutorial.control import context

class BattleQuestsStartReqs(context.StartReqs):

    def isEnabled(self):
        areSettingsInited = self.__areSettingsInited()
        arenaGuiTypes = [ARENA_GUI_TYPE.RANDOM, ARENA_GUI_TYPE.SANDBOX, ARENA_GUI_TYPE.RATED_SANDBOX]
        if IS_DEVELOPMENT:
            arenaGuiTypes.append(ARENA_GUI_TYPE.TRAINING)
        return arena_info.getArenaGuiType() in arenaGuiTypes and areSettingsInited

    def __areSettingsInited(self):
        validateSettings = (TUTORIAL.FIRE_EXTINGUISHER_INSTALLED, TUTORIAL.MEDKIT_INSTALLED, TUTORIAL.REPAIRKIT_INSTALLED)
        getter = AccountSettings.getSettings
        for setting in validateSettings:
            if getter(setting):
                return True

        return False

    def prepare(self, ctx):
        pass

    def process(self, descriptor, ctx):
        return True


class FakeBonusesRequester(context.BonusesRequester):

    def request(self, chapterID=None):
        pass
