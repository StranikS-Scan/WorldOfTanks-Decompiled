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
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles, icons, currency
from gui.shared.formatters.tankmen import formatDeletedTankmanStr
from gui.shared.gui_items.serializers import packTankman
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils, dependency
from helpers.i18n import makeString as _ms
from items.tankmen import MAX_SKILL_LEVEL
from skeletons.gui.game_control import IRestoreController

class _TankmanOperationDialogBase(TankmanOperationDialogMeta):
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, meta, handler):
        super(_TankmanOperationDialogBase, self).__init__(text_styles.middleTitle(meta.getMessage()), meta.getTitle(), meta.getButtonLabels(), meta.getCallbackWrapper(handler))
        self._tankman = meta.getTankman()
        self._isDismissState = True
        self._showPeriodEndWarning = meta.showPeriodEndWarning

    def _populate(self):
        super(_TankmanOperationDialogBase, self)._populate()
        self.__setTankmanData()

    def _dispose(self):
        super(_TankmanOperationDialogBase, self)._dispose()
        self._tankman = None
        return

    def _buildVO(self):
        return NotImplemented

    def __setTankmanData(self):
        packedTankman = packTankman(self._tankman)
        nation = nations.NAMES[packedTankman['nationID']]
        tankmanName = self._tankman.fullUserName
        tankmanIcon = packedTankman['icon']['big']
        roleIcon = packedTankman['iconRole']['small']
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
        isSkilledTankmen = roleLevel == MAX_SKILL_LEVEL or lastSkillIcon is not '' or hasNewSkill
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
        elif len(deletedTankmen) > 0:
            alertImgSrc = RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON
            alertTooltip = makeTooltip(TOOLTIPS.DISMISSTANKMANDIALOG_BUFFERISFULL_HEADER, _ms(TOOLTIPS.DISMISSTANKMANDIALOG_BUFFERISFULL_BODY, placeCount=self.restore.getMaxTankmenBufferLength(), currCount=len(self.restore.getDismissedTankmen()), tankmanNew=self._tankman.fullUserName, tankmanOld=formatDeletedTankmanStr(deletedTankmen[0])))
        return {'alertText': alertText,
         'alertTooltip': alertTooltip,
         'alertImgSrc': alertImgSrc,
         'questionText': text_styles.main(_ms(DIALOGS.DISMISSTANKMAN_MESSAGE))}


class RestoreTankmanDialog(_TankmanOperationDialogBase):

    def _populate(self):
        self._isDismissState = False
        super(RestoreTankmanDialog, self)._populate()
        restorePrice, _ = getTankmenRestoreInfo(self._tankman)
        isEnabled = True
        if g_itemsCache.items.stats.money.getShortage(restorePrice):
            isEnabled = False
        if isLongDisconnectedFromCenter():
            isEnabled = False
        self.as_setButtonEnablingS(DIALOG_BUTTON_ID.SUBMIT, isEnabled)
        if not isEnabled:
            self.as_setButtonFocusS(DIALOG_BUTTON_ID.CLOSE)

    def _buildVO(self):
        actionPriceVO = None
        restorePrice, lengthInHours = getTankmenRestoreInfo(self._tankman)
        warningTexts = []
        if restorePrice.credits == 0:
            restoreCurrency = ICON_TEXT_FRAMES.EMPTY
            restorePriceStr = text_styles.success(_ms(DIALOGS.RESTORETANKMAN_FORFREE))
        else:
            restoreCurrency = ICON_TEXT_FRAMES.CREDITS
            restorePriceStr = str(currency.getBWFormatter(Currency.CREDITS)(restorePrice.credits))
            if self._showPeriodEndWarning:
                daysCount = lengthInHours / time_utils.HOURS_IN_DAY
                warningTexts.append(text_styles.alert(_ms(DIALOGS.RESTORETANKMAN_NEWPERIODWARNING, daysCount=daysCount)))
            if constants.IS_KOREA and restorePrice.gold > 0:
                warningTexts.append(text_styles.standard(DIALOGS.BUYVEHICLEDIALOG_WARNING))
        if isLongDisconnectedFromCenter():
            warningTexts.append(text_styles.error(DIALOGS.RESTORETANKMAN_DISCONNECTEDFROMCENTER))
        return {'questionText': text_styles.stats(_ms(DIALOGS.RESTORETANKMAN_PRICE)),
         'restoreCurrency': restoreCurrency,
         'restorePrice': restorePriceStr,
         'isEnoughMoneyForRestore': g_itemsCache.items.stats.money.credits >= restorePrice.credits,
         'actionPriceVO': actionPriceVO,
         'warningText': '\n\n'.join(warningTexts)}
