# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/SkillDropWindow.py
import cPickle as pickle
import time
from typing import TYPE_CHECKING, Optional
from async import await, async
from chat_shared import SYS_MESSAGE_TYPE
from constants import SwitchState
from gui.impl.dialogs.dialogs import showDropSkillDialog
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shop import showBuyGoldForCrew
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
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n
from messenger import MessengerEntry
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
if TYPE_CHECKING:
    from gui.goodies.goodie_items import RecertificationForm
_switchToWindowState = {SwitchState.ENABLED.value: SKILLS_CONSTANTS.RECERTIFICATION_USABLE,
 SwitchState.DISABLED.value: SKILLS_CONSTANTS.RECERTIFICATION_HIDDEN,
 SwitchState.INACTIVE.value: SKILLS_CONSTANTS.RECERTIFICATION_VISIBLE_DISABLED}

class SkillDropWindow(SkillDropMeta):
    goodiesCache = dependency.descriptor(IGoodiesCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self, ctx=None):
        super(SkillDropWindow, self).__init__()
        self.tmanInvID = ctx.get('tankmanID')
        self._goldOptionIndex = None
        self._recertificationFormOptionIndex = None
        self._recertificationFormGoodie = None
        return

    def __setData(self, *args):
        items = self.itemsCache.items
        tankman = items.getTankman(self.tmanInvID)
        if tankman is None:
            self.onWindowClose()
            return
        else:
            dropSkillsCost = []
            for i, k in enumerate(sorted(items.shop.dropSkillsCost.keys())):
                skillCost = items.shop.dropSkillsCost[k]
                defaultSkillCots = items.shop.defaults.dropSkillsCost[k]
                if skillCost['gold'] > 0:
                    self._goldOptionIndex = i
                price = Money(**skillCost)
                defaultPrice = Money(**defaultSkillCots)
                action = None
                if price != defaultPrice:
                    key = '{}DropSkillsCost'.format(price.getCurrency(byWeight=True))
                    action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, key, True, price, defaultPrice)
                skillCost['action'] = action
                dropSkillsCost.append(skillCost)

            self._recertificationFormOptionIndex = len(dropSkillsCost)
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
            retrainButtonsData = packDropSkill(tankman)
            selectedButton = 0
            i = len(retrainButtonsData) - 1
            while i > 0:
                if retrainButtonsData[i]['enabled']:
                    selectedButton = i
                    break
                i -= 1

            self._recertificationFormGoodie = self.goodiesCache.getRecertificationForm(currency='gold')
            self.as_setDataS({'tankman': tankmanData,
             'dropSkillsCost': dropSkillsCost,
             'hasNewSkills': hasNewSkills,
             'newSkills': tankman.newSkillCount,
             'defaultSavingMode': selectedButton,
             'blanks': self._recertificationFormGoodie.count,
             'texts': self.__getTexts(),
             'recertificationStatus': self._getRecertificationStatus()})
            self.as_updateRetrainButtonsDataS(retrainButtonsData)
            return

    def __getTexts(self):
        ms = i18n.makeString
        percentText = text_styles.neutral(ms(MENU.SKILLDROPWINDOW_FREEDROPPERCENT))
        freeDropText = text_styles.main(ms(MENU.SKILLDROPWINDOW_FREEDROPLABEL, percent=percentText))
        return {'freeDrop': freeDropText}

    def _getRecertificationStatus(self):
        return SKILLS_CONSTANTS.RECERTIFICATION_HIDDEN if not self._recertificationFormGoodie.enabled else (_switchToWindowState[self.lobbyContext.getServerSettings().recertificationFormState()],)

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

    @async
    def dropSkills(self, flashDropSkillCostIdx):
        tankman = self.itemsCache.items.getTankman(self.tmanInvID)
        dropSkillCostIdx = int(flashDropSkillCostIdx)
        useRecertificationForm = flashDropSkillCostIdx == self._recertificationFormOptionIndex
        price = None
        freeDropSave100 = len(tankman.skills) == 1 and tankman.skills[0].level < 1
        if useRecertificationForm:
            dropSkillCostIdx = self._goldOptionIndex
        else:
            price = self.itemsCache.items.shop.dropSkillsCost[dropSkillCostIdx]
            dropSkillCost = self.itemsCache.items.shop.dropSkillsCost[dropSkillCostIdx].get(Currency.GOLD, 0)
            currentGold = self.itemsCache.items.stats.gold
            if currentGold < dropSkillCost and not freeDropSave100:
                showBuyGoldForCrew(dropSkillCost)
                return
        isOk, _ = yield await(showDropSkillDialog(tankman, price=price, isBlank=useRecertificationForm, freeDropSave100=freeDropSave100))
        if isOk:
            self.__processDrop(tankman, dropSkillCostIdx, price, freeDropSave100)
        return

    @decorators.process('deleting')
    def __processDrop(self, tankman, dropSkillCostIdx, price, freeDrop):
        useRecertificationForm = price is None
        proc = TankmanDropSkills(tankman, dropSkillCostIdx, useRecertificationForm)
        result = yield proc.request()
        if not result.success:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        elif result.success:
            data = {'currencyType': '',
             'count': 0}
            if not freeDrop:
                if useRecertificationForm:
                    data['currencyType'] = 'blanks'
                    data['count'] = 1
                elif price is not None:
                    gold = price.get(Currency.GOLD, 0)
                    credit = price.get(Currency.CREDITS, 0)
                    if gold > 0:
                        data['currencyType'] = Currency.GOLD
                        data['count'] = gold
                    elif credit > 0:
                        data['currencyType'] = Currency.CREDITS
                        data['count'] = credit
            messageType = SYS_MESSAGE_TYPE.recertificationResetUsed if data['currencyType'] else SYS_MESSAGE_TYPE.recertificationReset
            action = {'sentTime': time.time(),
             'data': {'type': messageType.index(),
                      'data': data}}
            MessengerEntry.g_instance.protos.BW.serviceChannel.onReceivePersonalSysMessage(action)
            self.onWindowClose()
            self.fireEvent(events.SkillDropEvent(events.SkillDropEvent.SKILL_DROPPED_SUCCESSFULLY))
        return
