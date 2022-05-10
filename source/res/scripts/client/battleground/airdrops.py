# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/airdrops.py
from constants import AirdropType
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from arena_component_system.client_arena_component_system import ClientArenaComponent
from battleground.bot_drop_object import BotAirdrop
from battleground.loot_drop_object import PlaneLootAirdrop

class Airdrops(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def scheduleLoot(self, dropID, position, serverTime):
        planeObj = PlaneLootAirdrop(dropID, position, serverTime)
        planeObj.start()

    def scheduleBot(self, dropID, position, teamID, yawAxis, serverTime, airdropType=AirdropType.BOT):
        botObj = BotAirdrop(dropID, position, teamID, yawAxis, serverTime, airdropType)
        botObj.start()


class AirdropsComponent(ClientArenaComponent, Airdrops):

    def __init__(self, componentSystem):
        Airdrops.__init__(self)
        ClientArenaComponent.__init__(self, componentSystem)
