# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/AwardWindow.py
from collections import namedtuple
from debug_utils import LOG_DEBUG
from helpers import i18n
from gui.Scaleform.daapi.view.meta.AwardWindowMeta import AwardWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
AwardsRibbonInfo = namedtuple('AwardsRibbonInfo', ['awardForCompleteText',
 'isAwardForCompleteVisible',
 'awardReceivedText',
 'isAwardsReceivedVisible',
 'ribbonSource',
 'awards'])

def packRibbonInfo(awards = None, awardForCompleteText = '', awardReceivedText = ''):
    return AwardsRibbonInfo(awardForCompleteText=awardForCompleteText, isAwardForCompleteVisible=bool(len(awardForCompleteText)), awardReceivedText=awardReceivedText, isAwardsReceivedVisible=bool(len(awardReceivedText)), ribbonSource=RES_ICONS.MAPS_ICONS_QUESTS_AWARDRIBBON, awards=awards or [])


class AwardAbstract(AppRef):

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

    def getExtraFields(self):
        return {}

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


class AwardWindow(View, AbstractWindowView, AwardWindowMeta, AppRef):

    def __init__(self, ctx):
        super(AwardWindow, self).__init__()
        raise 'award' in ctx and isinstance(ctx['award'], AwardAbstract) or AssertionError
        self.__award = ctx['award']

    def onWindowClose(self):
        self.destroy()

    def onOKClick(self):
        self.onWindowClose()
        return self.__award.handleOkButton()

    def onCloseClick(self):
        self.onWindowClose()
        return self.__award.handleCloseButton()

    def onTakeNextClick(self):
        self.onWindowClose()
        return self.__award.handleBodyButton()

    def _populate(self):
        super(AwardWindow, self)._populate()
        okBtn, closeBtn, bodyBtn = self.__award.getButtonStates()
        data = {'windowTitle': self.__award.getWindowTitle(),
         'backImage': self.__award.getBackgroundImage(),
         'awardImage': self.__award.getAwardImage(),
         'header': self.__award.getHeader(),
         'description': self.__award.getDescription(),
         'additionalText': self.__award.getAdditionalText(),
         'isDashLineEnabled': False,
         'buttonText': self.__award.getOkButtonText(),
         'closeBtnLabel': self.__award.getCloseButtonText(),
         'takeNextBtnLabel': self.__award.getBodyButtonText(),
         'isOKBtnEnabled': okBtn,
         'isCloseBtnEnabled': closeBtn,
         'isTakeNextBtnEnabled': bodyBtn}
        data.update(self.__award.getExtraFields())
        ribbonInfo = self.__award.getRibbonInfo()
        if ribbonInfo is not None:
            data.update({'awardsBlock': ribbonInfo._asdict()})
        self.as_setDataS(data)
        return
