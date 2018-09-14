# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/AwardWindow.py
from collections import namedtuple
from helpers import i18n
from gui.Scaleform.daapi.view.meta.AwardWindowMeta import AwardWindowMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
AwardsRibbonInfo = namedtuple('AwardsRibbonInfo', ['awardForCompleteText',
 'isAwardForCompleteVisible',
 'awardReceivedText',
 'isAwardsReceivedVisible',
 'awardBonusStrText',
 'isAwardBonusStrVisible',
 'ribbonSource',
 'awards'])

def packRibbonInfo(awards = None, awardForCompleteText = '', awardReceivedText = '', awardBonusStrText = ''):
    return AwardsRibbonInfo(awardForCompleteText=awardForCompleteText, isAwardForCompleteVisible=bool(len(awardForCompleteText)), awardReceivedText=awardReceivedText, isAwardsReceivedVisible=bool(len(awardReceivedText)), awardBonusStrText=awardBonusStrText, isAwardBonusStrVisible=bool(len(awardBonusStrText)), ribbonSource=RES_ICONS.MAPS_ICONS_QUESTS_AWARDRIBBON, awards=awards or [])


class AwardAbstract(object):

    def getWindowTitle(self):
        return ''

    def getBackgroundImage(self):
        return ''

    def getAwardImage(self):
        return None

    def getHeader(self):
        return ''

    def getDescription(self):
        return ''

    def getAdditionalText(self):
        return ''

    def getTextAreaIconPath(self):
        return ''

    def getTextAreaIconIsShow(self):
        return False

    def getExtraFields(self):
        return {}

    def getHasDashedLine(self):
        return False

    def getButtonStates(self):
        return (True, False, False)

    def getOkButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_OKBUTTON)

    def getCloseButtonText(self):
        return i18n.makeString(MENU.AWARDWINDOW_CLOSEBUTTON)

    def getBodyButtonText(self):
        return ''

    def getRibbonInfo(self):
        return None

    def handleOkButton(self):
        pass

    def handleCloseButton(self):
        pass

    def handleBodyButton(self):
        pass

    def clear(self):
        pass


class AwardWindow(AwardWindowMeta):

    def __init__(self, ctx):
        super(AwardWindow, self).__init__()
        raise 'award' in ctx and isinstance(ctx['award'], AwardAbstract) or AssertionError
        self.__award = ctx['award']

    def onWindowClose(self):
        self.destroy()

    def onOKClick(self):
        self.__award.handleOkButton()
        self.onWindowClose()

    def onCloseClick(self):
        self.__award.handleCloseButton()
        self.onWindowClose()

    def onTakeNextClick(self):
        self.__award.handleBodyButton()
        self.onWindowClose()

    def _populate(self):
        super(AwardWindow, self)._populate()
        okBtn, closeBtn, bodyBtn = self.__award.getButtonStates()
        data = {'windowTitle': self.__award.getWindowTitle(),
         'backImage': self.__award.getBackgroundImage(),
         'awardImage': self.__award.getAwardImage(),
         'header': self.__award.getHeader(),
         'description': self.__award.getDescription(),
         'additionalText': self.__award.getAdditionalText(),
         'isDashLineEnabled': self.__award.getHasDashedLine(),
         'buttonText': self.__award.getOkButtonText(),
         'closeBtnLabel': self.__award.getCloseButtonText(),
         'takeNextBtnLabel': self.__award.getBodyButtonText(),
         'textAreaIconPath': self.__award.getTextAreaIconPath(),
         'textAreaIconIsShow': self.__award.getTextAreaIconIsShow(),
         'isOKBtnEnabled': okBtn,
         'isCloseBtnEnabled': closeBtn,
         'isTakeNextBtnEnabled': bodyBtn}
        data.update(self.__award.getExtraFields())
        ribbonInfo = self.__award.getRibbonInfo()
        if ribbonInfo is not None:
            data.update({'awardsBlock': ribbonInfo._asdict()})
        self.as_setDataS(data)
        return

    def _dispose(self):
        if self.__award is not None:
            self.__award.clear()
            self.__award = None
        super(AwardWindow, self)._dispose()
        return
