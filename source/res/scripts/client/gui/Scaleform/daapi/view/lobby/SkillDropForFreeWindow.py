# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/SkillDropForFreeWindow.py
import time
from chat_shared import SYS_MESSAGE_TYPE
from constants import SwitchState, DROP_SKILL_OPTIONS, FREE_DROP_SKILL_TOKEN
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.SkillDropForFreeMeta import SkillDropForFreeMeta
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS
from gui.shared import events
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.processors.tankman import TankmanDropSkills
from gui.shared.gui_items.serializers import packTankman, repackTankmanWithSkinData
from gui.shared.money import Money, Currency
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils import decorators
from helpers import dependency, time_utils
from items import tankmen
from messenger import MessengerEntry
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_switchToWindowState = {SwitchState.ENABLED.value: SKILLS_CONSTANTS.RECERTIFICATION_USABLE,
 SwitchState.DISABLED.value: SKILLS_CONSTANTS.RECERTIFICATION_HIDDEN,
 SwitchState.INACTIVE.value: SKILLS_CONSTANTS.RECERTIFICATION_VISIBLE_DISABLED}

class SkillDropForFreeWindow(SkillDropForFreeMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self, ctx=None):
        super(SkillDropForFreeWindow, self).__init__()
        self.tmanInvID = ctx.get('tankmanID')

    def __setData(self, *args):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        if tankman is None:
            self.onWindowClose()
            return
        else:
            dropSkillsCost = []
            for k in sorted(items.shop.dropSkillsCost.keys()):
                skillCost = items.shop.dropSkillsCost[k]
                defaultSkillCots = items.shop.defaults.dropSkillsCost[k]
                price = Money(**skillCost)
                defaultPrice = Money(**defaultSkillCots)
                action = None
                if price != defaultPrice:
                    key = '{}DropSkillsCost'.format(price.getCurrency(byWeight=True))
                    action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, key, True, price, defaultPrice)
                skillCost['action'] = action
                dropSkillsCost.append(skillCost)

            dropSkillsCost.append({'action': None,
             'xpReuseFraction': 1.0,
             'gold': 0,
             'credits': 0})
            skills_count = tankmen.getSkillsConfig().getNumberOfActiveSkills()
            lenSkills = len(tankman.skills)
            availableSkillsCount = skills_count - lenSkills
            hasNewSkills = tankman.roleLevel == tankmen.MAX_SKILL_LEVEL and availableSkillsCount and (tankman.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not lenSkills)
            tankmanData = packTankman(tankman, isCountPermanentSkills=False)
            repackTankmanWithSkinData(tankman, tankmanData)
            expiryTime = self.itemsCache.items.tokens.getTokenExpiryTime(FREE_DROP_SKILL_TOKEN)
            self.as_setDataS({'tankman': tankmanData,
             'dropSkillsCost': dropSkillsCost,
             'hasNewSkills': hasNewSkills,
             'newSkills': tankman.newSkillCount,
             'blanks': 0,
             'timeLeft': expiryTime - time_utils.getServerUTCTime()})
            return

    def _populate(self):
        super(SkillDropForFreeWindow, self)._populate()
        self.__setData()
        self.itemsCache.onSyncCompleted += self.__setData
        g_clientUpdateManager.addCallbacks({'inventory.8.compDescr': self.onTankmanChanged,
         'cache.mayConsumeWalletResources': self.__setData})

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__setData
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(SkillDropForFreeWindow, self)._dispose()

    def onTankmanChanged(self, data):
        if self.tmanInvID in data:
            if data[self.tmanInvID] is None:
                self.onWindowClose()
                return
            self.__setData()
        return

    def onWindowClose(self):
        self.destroy()

    def dropSkills(self):
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        self.__processDrop(tankman, DROP_SKILL_OPTIONS.FREE_DROP_WITH_TOKEN_INDEX, 0)

    @decorators.adisp_process('deleting')
    def __processDrop(self, tankman, dropSkillCostIdx, price):
        proc = TankmanDropSkills(tankman, dropSkillCostIdx, False)
        result = yield proc.request()
        if not result.success:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        elif result.success:
            data = {'currencyType': Currency.GOLD,
             'count': price}
            action = {'sentTime': time.time(),
             'data': {'type': SYS_MESSAGE_TYPE.recertificationResetUsed.index(),
                      'data': data}}
            MessengerEntry.g_instance.protos.BW.serviceChannel.onReceivePersonalSysMessage(action)
            self.onWindowClose()
            self.fireEvent(events.SkillDropEvent(events.SkillDropEvent.SKILL_DROPPED_SUCCESSFULLY))
