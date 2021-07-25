# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_post_progression/battle_cooldown_manager.py
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE

class BattleCooldownManager(RequestCooldownManager):

    def __init__(self, default=0.5):
        super(BattleCooldownManager, self).__init__(REQUEST_SCOPE.BATTLE_ACTION)
        self.__default = default

    def lookupName(self, rqTypeID):
        pass

    def getDefaultCoolDown(self):
        return self.__default

    def _showSysMessage(self, msg):
        pass
