# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/AwardWindow.py
from collections import namedtuple
from gui.Scaleform.daapi.view.meta.MissionAwardWindowMeta import MissionAwardWindowMeta
from helpers import i18n
from gui.Scaleform.daapi.view.meta.AwardWindowMeta import AwardWindowMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.AWARDWINDOW_CONSTANTS import AWARDWINDOW_CONSTANTS
BOTTOM_BUTTONS_PADDING = 23
HEADER_TEXT_OFFSET = 269
MIN_WINDOW_HEIGHT = 427
AwardsRibbonInfo = namedtuple('AwardsRibbonInfo', ['awardForCompleteText',
 'isAwardForCompleteVisible',
 'awardReceivedText',
 'isAwardsReceivedVisible',
 'awardBonusStrText',
 'isAwardBonusStrVisible',
 'useHtmlInBonusStr',
 'ribbonSource',
 'awards'])

def packRibbonInfo(awards=None, awardForCompleteText='', awardReceivedText='', awardBonusStrText='', useHtmlInBonusStr=True):
    return AwardsRibbonInfo(awardForCompleteText=awardForCompleteText, isAwardForCompleteVisible=bool(len(awardForCompleteText)), awardReceivedText=awardReceivedText, isAwardsReceivedVisible=bool(len(awardReceivedText)), awardBonusStrText=awardBonusStrText, isAwardBonusStrVisible=bool(len(awardBonusStrText)), useHtmlInBonusStr=useHtmlInBonusStr, ribbonSource=RES_ICONS.MAPS_ICONS_QUESTS_AWARDRIBBON, awards=awards or [])


class AwardAbstract(object):

    def getWindowTitle(self):
        pass

    def getBackgroundImage(self):
        pass

    def useBackgroundAnimation(self):
        return False

    def forceUseBackImage(self):
        return False

    def autoControlBackAnimation(self):
        return True

    def useEndedBackAnimation(self):
        return False

    def getBackgroundAnimationData(self):
        return None

    def getBackgroundAnimationVoName(self):
        return None

    def getAwardImage(self):
        return None

    def getPackImage(self):
        return None

    def getHeader(self):
        pass

    def getDescription(self):
        pass

    def getAdditionalText(self):
        pass

    def getTextAreaIconPath(self):
        pass

    def getTextAreaIconIsShow(self):
        return False

    def getExtraFields(self):
        return {}

    def hasDashedLine(self):
        return False

    def isNeedAdditionalBodyClick(self):
        return False

    def getMinWindowHeight(self):
        return MIN_WINDOW_HEIGHT

    def getHeaderTextOffset(self):
        return HEADER_TEXT_OFFSET

    def getBottomButtonsPadding(self):
        return BOTTOM_BUTTONS_PADDING

    def getButtonStates(self):
        return (True, False, False)

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_OKBUTTON)

    def getCloseButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_CLOSEBUTTON)

    def hasCheckBox(self):
        return False

    def getCheckBoxData(self):
        return (False, '')

    def getBodyButtonText(self):
        pass

    def getChristmasBodyButtonText(self):
        pass

    def getAutoAnimationStart(self):
        return False

    def getWarningTexts(self):
        pass

    def getRibbonInfo(self):
        return None

    def handleOkButton(self):
        pass

    def handleCloseButton(self):
        pass

    def handleBodyButton(self):
        pass

    def handleAdditionalBodyBtnClick(self):
        pass

    def handleCheckBoxSelect(self, isSelected):
        pass

    def handleWarningHyperlinkClick(self):
        pass

    def clear(self):
        pass

    @staticmethod
    def getEffectSound():
        return None


class MissionAwardAbstract(AwardAbstract):

    def getRibbonImage(self):
        pass

    def getCurrentQuestHeader(self):
        pass

    def getCurrentQuestConditions(self):
        return None

    def getCurrentQuestConditionsText(self):
        pass

    def getNextQuestHeader(self):
        pass

    def getNextQuestConditions(self):
        pass

    def getAdditionalStatusText(self):
        pass

    def getMainStatusText(self):
        pass

    def getMainStatusIcon(self):
        pass

    def getAvalableText(self):
        pass

    def getAdditionalStatusIcon(self):
        pass

    def getNextButtonText(self):
        pass

    def getNextButtonTooltip(self):
        pass

    def isNextAvailable(self):
        return False

    def isLast(self):
        return False

    def isPersonal(self):
        return False

    def getAwards(self):
        return []

    def handleNextButton(self):
        pass

    def handleCurrentButton(self):
        pass


class ExplosionBackAward(AwardAbstract):

    def __init__(self, useAnimation=True):
        super(ExplosionBackAward, self).__init__()
        self.__useAnimation = useAnimation

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getBackgroundAnimationVoName(self):
        return AWARDWINDOW_CONSTANTS.ANIMATION_DATA_CLASS

    def useBackgroundAnimation(self):
        return self.__useAnimation

    def getBackgroundAnimationData(self):
        return {'image': self.getAwardImage(),
         'animationPath': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_PATH,
         'animationLinkage': AWARDWINDOW_CONSTANTS.EXPLOSION_BACK_ANIMATION_LINKAGE} if self.__useAnimation else None


class AwardWindow(AwardWindowMeta):

    def __init__(self, ctx):
        super(AwardWindow, self).__init__()
        assert 'award' in ctx and isinstance(ctx['award'], AwardAbstract)
        self.__award = ctx['award']

    def onWindowClose(self):
        self.__award.handleCloseButton()
        self.destroy()

    def onOKClick(self):
        self.__award.handleOkButton()
        self.onWindowClose()

    def onCloseClick(self):
        self.__award.handleCloseButton()
        self.onWindowClose()

    def onTakeNextClick(self):
        if self.__award.isNeedAdditionalBodyClick():
            self.__award.handleAdditionalBodyBtnClick()
            self.__setTakeNextBtn()
            if not self.__award.autoControlBackAnimation():
                self.as_startAnimationS()
        else:
            self.__award.handleBodyButton()
            self.onWindowClose()

    def onCheckBoxSelect(self, isSelected):
        self.__award.handleCheckBoxSelect(isSelected)

    def onWarningHyperlinkClick(self):
        self.__award.handleWarningHyperlinkClick()

    def onAnimationStart(self):
        effectSound = self.__award.getEffectSound()
        if effectSound is not None:
            self.app.soundManager.playEffectSound(effectSound)
        return

    def _populate(self):
        super(AwardWindow, self)._populate()
        okBtn, closeBtn, _ = self.__award.getButtonStates()
        warningText, warningHyperlinkText = self.__award.getWarningTexts()
        isCheckBoxSelected, checkBoxLabel = self.__award.getCheckBoxData()
        data = {'windowTitle': self.__award.getWindowTitle(),
         'backImage': self.__award.getBackgroundImage(),
         'forceUseBackImage': self.__award.forceUseBackImage(),
         'useBackAnimation': self.__award.useBackgroundAnimation(),
         'autoControlBackAnimation': self.__award.autoControlBackAnimation(),
         'useEndedBackAnimation': self.__award.useEndedBackAnimation(),
         'backAnimationData': self.__packAnimationData(),
         'awardImage': self.__award.getAwardImage(),
         'packImage': self.__award.getPackImage(),
         'header': self.__award.getHeader(),
         'description': self.__award.getDescription(),
         'additionalText': self.__award.getAdditionalText(),
         'isDashLineEnabled': self.__award.hasDashedLine(),
         'buttonText': self.__award.getOkButtonText(),
         'closeBtnLabel': self.__award.getCloseButtonText(),
         'hasCheckBox': self.__award.hasCheckBox(),
         'isCheckBoxSelected': isCheckBoxSelected,
         'checkBoxLabel': checkBoxLabel,
         'textAreaIconPath': self.__award.getTextAreaIconPath(),
         'textAreaIconIsShow': self.__award.getTextAreaIconIsShow(),
         'isOKBtnEnabled': okBtn,
         'isCloseBtnEnabled': closeBtn,
         'warningText': warningText,
         'warningHyperlinkText': warningHyperlinkText,
         'minWindowHeight': self.__award.getMinWindowHeight(),
         'headerTextOffset': self.__award.getHeaderTextOffset(),
         'bottomButtonsPadding': self.__award.getBottomButtonsPadding()}
        self.__setTakeNextBtn()
        data.update(self.__award.getExtraFields())
        ribbonInfo = self.__award.getRibbonInfo()
        if ribbonInfo is not None:
            data.update({'awardsBlock': ribbonInfo._asdict()})
        self.as_setDataS(data)
        if self.__award.getAutoAnimationStart():
            self.__award.handleAdditionalBodyBtnClick()
            self.as_endAnimationS()
        return

    def __setTakeNextBtn(self):
        _, _, bodyBtn = self.__award.getButtonStates()
        self.as_setTakeNextBtnS({'isTakeNextBtnEnabled': bodyBtn,
         'takeNextBtnLabel': self.__award.getBodyButtonText(),
         'christmasTakeNextBtnLabel': self.__award.getChristmasBodyButtonText()})

    def __packAnimationData(self):
        data = self.__award.getBackgroundAnimationData()
        return {'voClassName': self.__award.getBackgroundAnimationVoName(),
         'voData': data} if data else None

    def _dispose(self):
        if self.__award is not None:
            self.__award.clear()
            self.__award = None
        super(AwardWindow, self)._dispose()
        return


class MissionAwardWindow(MissionAwardWindowMeta):

    def __init__(self, ctx):
        super(MissionAwardWindow, self).__init__()
        assert 'award' in ctx and isinstance(ctx['award'], AwardAbstract)
        self.__award = ctx['award']

    def onWindowClose(self):
        self.destroy()

    def onCurrentQuestClick(self):
        self.__award.handleNextButton()
        self.onWindowClose()

    def onNextQuestClick(self):
        self.__award.handleCurrentButton()
        self.onWindowClose()

    def _populate(self):
        super(MissionAwardWindow, self)._populate()
        data = {'windowTitle': self.__award.getWindowTitle(),
         'backImage': self.__award.getBackgroundImage(),
         'ribbonImage': self.__award.getRibbonImage(),
         'header': self.__award.getHeader(),
         'description': self.__award.getDescription(),
         'currentQuestHeader': self.__award.getCurrentQuestHeader(),
         'currentQuestConditions': self.__award.getCurrentQuestConditionsText(),
         'nextQuestHeader': self.__award.getNextQuestHeader(),
         'nextQuestConditions': self.__award.getNextQuestConditions(),
         'additionalStatusText': self.__award.getAdditionalStatusText(),
         'mainStatusText': self.__award.getMainStatusText(),
         'availableText': self.__award.getAvalableText(),
         'additionalStatusIcon': self.__award.getAdditionalStatusIcon(),
         'mainStatusIcon': self.__award.getMainStatusIcon(),
         'nextButtonText': self.__award.getNextButtonText(),
         'nextButtonTooltip': self.__award.getNextButtonTooltip(),
         'awards': self.__award.getAwards(),
         'conditions': self.__award.getCurrentQuestConditions(),
         'isPersonalQuest': self.__award.isPersonal(),
         'availableNextQuest': self.__award.isNextAvailable(),
         'isLastQuest': self.__award.isLast()}
        self.as_setDataS(data)

    def _dispose(self):
        self.__award.clear()
        self.__award = None
        super(MissionAwardWindow, self)._dispose()
        return
