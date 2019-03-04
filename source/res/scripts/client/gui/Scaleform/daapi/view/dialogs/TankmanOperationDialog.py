# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/TankmanOperationDialog.py
import constants
import nations
from account_helpers import isLongDisconnectedFromCenter
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.TankmanOperationDialogMeta import TankmanOperationDialogMeta
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.SKILLS_CONSTANTS import SKILLS_CONSTANTS
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.shared.formatters import text_styles, icons, currency
from gui.shared.formatters.tankmen import formatDeletedTankmanStr
from gui.shared.gui_items.Tankman import getCrewSkinIconBig
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.serializers import packTankman
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils, dependency
from helpers.i18n import makeString as _ms
from items.components.crewSkins_constants import NO_CREW_SKIN_ID
from items.tankmen import MAX_SKILL_LEVEL
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

class _TankmanOperationDialogBase(TankmanOperationDialogMeta):
    restore = dependency.descriptor(IRestoreController)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self, meta, handler):
        super(_TankmanOperationDialogBase, self).__init__(text_styles.middleTitle(meta.getMessage()), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self._tankman = meta.getTankman()
        self._isDismissState = True
        self._showPeriodEndWarning = meta.showPeriodEndWarning

    def _populate(self):
        super(_TankmanOperationDialogBase, self)._populate()
        self._setTankmanData()

    def _dispose(self):
        super(_TankmanOperationDialogBase, self)._dispose()
        self._tankman = None
        return

    def _buildVO(self):
        return NotImplemented

    def _setTankmanData(self):
        packedTankman = packTankman(self._tankman)
        nation = nations.NAMES[packedTankman['nationID']]
        tankmanIcon = packedTankman['icon']['big']
        roleIcon = packedTankman['iconRole']['small']
        skinID = self._tankman.skinID
        if skinID != NO_CREW_SKIN_ID and self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            skinItem = self.itemsCache.items.getCrewSkin(skinID)
            tankmanIcon = getCrewSkinIconBig(skinItem.getIconID())
            tankmanName = localizedFullName(skinItem)
        else:
            tankmanName = self._tankman.fullUserName
        skills = packedTankman['skills']
        lastSkillIcon = ''
        lastSkillLevel = 0
        skillsCount = len(skills)
        if skillsCount > 0:
            lastSkill = skills[-1]
            lastSkillIcon = lastSkill['icon']['small']
            lastSkillLevel = lastSkill['level']
        preLastSkillIcon = ''
        if skillsCount > 1:
            preLastSkillIcon = skills[-2]['icon']['small']
        roleLevel = packedTankman['roleLevel']
        hasNewSkill = self._tankman.hasNewSkill(useCombinedRoles=True)
        isSkilledTankmen = roleLevel == MAX_SKILL_LEVEL or lastSkillIcon != '' or hasNewSkill
        isProtectedState = self._isDismissState and isSkilledTankmen
        if not isSkilledTankmen:
            skillsCount = -1
        newSkillsCount, lastNewSkillLevel = self._tankman.newSkillCount
        if skillsCount == 0 and hasNewSkill:
            skillsCount = newSkillsCount
            preLastSkillIcon = SKILLS_CONSTANTS.TYPE_NEW_SKILL
            lastSkillIcon = SKILLS_CONSTANTS.TYPE_NEW_SKILL
            lastSkillLevel = lastNewSkillLevel
            hasNewSkill = False
        tankmanBlockVO = {'nation': nation,
         'tankmanName': tankmanName,
         'tankmanIcon': tankmanIcon,
         'roleIcon': roleIcon,
         'skillsCount': skillsCount,
         'lastSkill': lastSkillIcon,
         'lastSkillLevel': lastSkillLevel,
         'preLastSkill': preLastSkillIcon,
         'hasNewSkill': hasNewSkill,
         'newSkillsCount': newSkillsCount,
         'lastNewSkillLevel': lastNewSkillLevel,
         'roleLevel': roleLevel}
        vo = self._buildVO()
        vo.update({'isProtectedState': isProtectedState,
         'tankmanBlockVO': tankmanBlockVO})
        self.as_setDataS(vo)


class DismissTankmanDialog(_TankmanOperationDialogBase):

    def _populate(self):
        self._isDismissState = True
        super(DismissTankmanDialog, self)._populate()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if len(self._tankman.skills) < 1:
            if self._tankman.roleLevel < 100:
                controlNumber = 0
                question = _ms(DIALOGS.DISMISSTANKMAN_MESSAGE)
            else:
                controlNumber = self._tankman.roleLevel
                question = _ms(DIALOGS.PROTECTEDDISMISSTANKMAN_MAINMESSAGE, roleLevel=text_styles.warning(str(controlNumber)))
        else:
            lastSkill = self._tankman.skills[-1]
            if lastSkill.isPerk:
                skillType = DIALOGS.PROTECTEDDISMISSTANKMAN_ADDITIONALMESSAGE_ISPERK
            else:
                skillType = DIALOGS.PROTECTEDDISMISSTANKMAN_ADDITIONALMESSAGE_ISABILLITY
            question = _ms(DIALOGS.PROTECTEDDISMISSTANKMAN_ADDITIONALMESSAGE, skillType=_ms(skillType), skillName=text_styles.neutral(lastSkill.userName), roleLevel=text_styles.warning(str(lastSkill.level)))
            controlNumber = lastSkill.level
        viewPy.setControlNumbers(str(controlNumber))
        viewPy.questionBody = text_styles.main(question)
        viewPy.errorMsg = text_styles.error(DIALOGS.PROTECTEDDISMISSTANKMAN_ERRORMESSAGE)

    def _buildVO(self):
        deletedTankmen = self.restore.getTankmenBeingDeleted()
        alertImgSrc = ''
        alertText = ''
        alertTooltip = ''
        if not self._tankman.isRestorable():
            alertText = text_styles.alert(icons.alert() + _ms(DIALOGS.PROTECTEDDISMISSTANKMAN_ALERT))
            alertTooltip = TOOLTIPS.DISMISSTANKMANDIALOG_CANTRESTORALERT
        elif deletedTankmen:
            alertImgSrc = RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON
            alertTooltip = makeTooltip(TOOLTIPS.DISMISSTANKMANDIALOG_BUFFERISFULL_HEADER, _ms(TOOLTIPS.DISMISSTANKMANDIALOG_BUFFERISFULL_BODY, placeCount=self.restore.getMaxTankmenBufferLength(), currCount=len(self.restore.getDismissedTankmen()), tankmanNew=self._tankman.fullUserName, tankmanOld=formatDeletedTankmanStr(deletedTankmen[0])))
        return {'alertText': alertText,
         'alertTooltip': alertTooltip,
         'alertImgSrc': alertImgSrc,
         'questionText': text_styles.main(_ms(DIALOGS.DISMISSTANKMAN_MESSAGE))}


class RestoreTankmanDialog(_TankmanOperationDialogBase):
    _CURRENCY_TO_TEXT_FRAME = {Currency.GOLD: ICON_TEXT_FRAMES.GOLD,
     Currency.CREDITS: ICON_TEXT_FRAMES.CREDITS}
    itemsCache = dependency.descriptor(IItemsCache)

    def _populate(self):
        self._isDismissState = False
        super(RestoreTankmanDialog, self)._populate()
        self.restore.onTankmenBufferUpdated += self.__onTankmenBufferUpdated
        restorePrice, _ = getTankmenRestoreInfo(self._tankman)
        isEnabled = True
        if self.itemsCache.items.stats.money.getShortage(restorePrice):
            isEnabled = False
        if isLongDisconnectedFromCenter():
            isEnabled = False
        self.as_setButtonEnablingS(DIALOG_BUTTON_ID.SUBMIT, isEnabled)
        if not isEnabled:
            self.as_setButtonFocusS(DIALOG_BUTTON_ID.CLOSE)

    def _dispose(self):
        super(RestoreTankmanDialog, self)._dispose()
        self.restore.onTankmenBufferUpdated -= self.__onTankmenBufferUpdated

    def _buildVO(self):
        actionPriceVO = None
        restorePrice, lengthInHours = getTankmenRestoreInfo(self._tankman)
        warningTexts = []
        if not restorePrice:
            currencyTextFrame = ICON_TEXT_FRAMES.EMPTY
            restorePriceStr = text_styles.success(_ms(DIALOGS.RESTORETANKMAN_FORFREE))
            isEnoughMoney = True
        else:
            currencyName = restorePrice.getCurrency()
            currencyTextFrame = self._CURRENCY_TO_TEXT_FRAME[currencyName]
            restorePriceStr = str(currency.getBWFormatter(currencyName)(restorePrice.getSignValue(currencyName)))
            isEnoughMoney = self.itemsCache.items.stats.money.get(currencyName, 0) >= restorePrice.get(currencyName, 0)
            if self._showPeriodEndWarning and restorePrice.isSet(Currency.GOLD):
                daysCount = lengthInHours / time_utils.HOURS_IN_DAY
                warningTexts.append(text_styles.alert(_ms(DIALOGS.RESTORETANKMAN_NEWPERIODWARNING, daysCount=daysCount)))
            if constants.IS_KOREA and restorePrice.isSet(Currency.GOLD):
                warningTexts.append(text_styles.standard(DIALOGS.BUYVEHICLEDIALOG_WARNING))
        if isLongDisconnectedFromCenter():
            warningTexts.append(text_styles.error(DIALOGS.RESTORETANKMAN_DISCONNECTEDFROMCENTER))
        return {'questionText': text_styles.stats(_ms(DIALOGS.RESTORETANKMAN_PRICE)),
         'restoreCurrency': currencyTextFrame,
         'restorePrice': restorePriceStr,
         'isEnoughMoneyForRestore': isEnoughMoney,
         'actionPriceVO': actionPriceVO,
         'warningText': '\n\n'.join(warningTexts)}

    def __onTankmenBufferUpdated(self, *args):
        self._setTankmanData()
