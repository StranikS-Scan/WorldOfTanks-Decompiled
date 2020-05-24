# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/SkillDropWindow.py
import cPickle as pickle
from gui.shop import showBuyGoldForCrew
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from helpers import dependency
from items import tankmen
from gui import SystemMessages
from gui.shared.utils import decorators
from gui.shared.formatters import text_styles
from gui.shared.gui_items.serializers import packTankman, packDropSkill, repackTankmanWithSkinData
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.processors.tankman import TankmanDropSkills
from gui.shared.money import Money, Currency
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.Scaleform.daapi.view.meta.SkillDropMeta import SkillDropMeta
from gui.shared import events
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

class SkillDropWindow(SkillDropMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self, ctx=None):
        super(SkillDropWindow, self).__init__()
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

            skills_count = tankmen.getSkillsConfig().getNumberOfActiveSkills()
            lenSkills = len(tankman.skills)
            availableSkillsCount = skills_count - lenSkills
            hasNewSkills = tankman.roleLevel == tankmen.MAX_SKILL_LEVEL and availableSkillsCount and (tankman.descriptor.lastSkillLevel == tankmen.MAX_SKILL_LEVEL or not lenSkills)
            tankmanData = packTankman(tankman, isCountPermanentSkills=False)
            repackTankmanWithSkinData(tankman, tankmanData)
            self.as_setDataS({'tankman': tankmanData,
             'dropSkillsCost': dropSkillsCost,
             'hasNewSkills': hasNewSkills,
             'newSkills': tankman.newSkillCount,
             'defaultSavingMode': 0,
             'texts': self.__getTexts()})
            self.as_updateRetrainButtonsDataS(packDropSkill(tankman))
            return

    def __getTexts(self):
        ms = i18n.makeString
        percentText = text_styles.neutral(ms(MENU.SKILLDROPWINDOW_FREEDROPPERCENT))
        freeDropText = text_styles.main(ms(MENU.SKILLDROPWINDOW_FREEDROPLABEL, percent=percentText))
        return {'freeDrop': freeDropText}

    def _populate(self):
        super(SkillDropWindow, self)._populate()
        self.__setData()
        self.itemsCache.onSyncCompleted += self.__setData
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.__setData)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.__setData)
        g_clientUpdateManager.addCallbacks({'inventory.8.compDescr': self.onTankmanChanged,
         'cache.mayConsumeWalletResources': self.__setData})

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self.__setData
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(SkillDropWindow, self)._dispose()

    def onTankmanChanged(self, data):
        if self.tmanInvID in data:
            if data[self.tmanInvID] is None:
                self.onWindowClose()
                return
            self.__setData()
        return

    def onWindowClose(self):
        self.destroy()

    def calcDropSkillsParams(self, tmanCompDescrPickle, xpReuseFraction):
        tmanCompDescr = pickle.loads(tmanCompDescrPickle)
        tmanDescr = tankmen.TankmanDescr(tmanCompDescr)
        tmanDescr.dropSkills(xpReuseFraction)
        tankman = Tankman(tmanDescr.makeCompactDescr())
        return (tankman.roleLevel,) + tankman.newSkillCount

    @decorators.process('deleting')
    def dropSkills(self, dropSkillCostIdx):
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        dropSkillCost = self.itemsCache.items.shop.dropSkillsCost[dropSkillCostIdx].get(Currency.GOLD, 0)
        currentGold = self.itemsCache.items.stats.gold
        if currentGold < dropSkillCost:
            showBuyGoldForCrew(dropSkillCost)
            return
        proc = TankmanDropSkills(tankman, dropSkillCostIdx)
        result = yield proc.request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            self.onWindowClose()
            self.fireEvent(events.SkillDropEvent(events.SkillDropEvent.SKILL_DROPPED_SUCCESSFULLY))
