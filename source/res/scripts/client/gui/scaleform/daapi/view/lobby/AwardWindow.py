# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/AwardWindow.py
from gui.Scaleform.daapi.view.meta.MissionAwardWindowMeta import MissionAwardWindowMeta
from gui.Scaleform.daapi.view.meta.AwardWindowMeta import AwardWindowMeta
from gui.server_events.pm_constants import PERSONAL_MISSIONS_SILENT_SOUND_SPACE

class AwardWindow(AwardWindowMeta):

    def onOKClick(self):
        self._award.handleOkButton()
        self.onWindowClose()

    def onCloseClick(self):
        self._award.handleCloseButton()
        self.onWindowClose()

    def onTakeNextClick(self):
        self._award.handleBodyButton()
        self.onWindowClose()

    def _getTypeSpecificFields(self):
        okBtn, closeBtn, bodyBtn = self._award.getButtonStates()
        result = {'useBackAnimation': self._award.useBackgroundAnimation(),
         'backAnimationData': self._award.getBackgroundAnimationData(),
         'awardImage': self._award.getAwardImage(),
         'additionalText': self._award.getAdditionalText(),
         'isDashLineEnabled': self._award.getHasDashedLine(),
         'buttonText': self._award.getOkButtonText(),
         'closeBtnLabel': self._award.getCloseButtonText(),
         'takeNextBtnLabel': self._award.getBodyButtonText(),
         'textAreaIconPath': self._award.getTextAreaIconPath(),
         'textAreaIconIsShow': self._award.getTextAreaIconIsShow(),
         'isOKBtnEnabled': okBtn,
         'isCloseBtnEnabled': closeBtn,
         'isTakeNextBtnEnabled': bodyBtn,
         'bodyBtnLinkage': self._award.getBodyButtonLinkage()}
        result.update(self._award.getExtraFields())
        ribbonInfo = self._award.getRibbonInfo()
        if ribbonInfo is not None:
            result.update({'awardsBlock': ribbonInfo._asdict()})
        return result


class MissionAwardWindow(MissionAwardWindowMeta):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SILENT_SOUND_SPACE

    def onCurrentQuestClick(self):
        self._award.handleNextButton()
        self.onWindowClose()

    def onNextQuestClick(self):
        self._award.handleCurrentButton()
        self.onWindowClose()

    def _getTypeSpecificFields(self):
        return {'ribbonImage': self._award.getRibbonImage(),
         'currentQuestHeader': self._award.getCurrentQuestHeader(),
         'currentQuestConditions': self._award.getCurrentQuestConditions(),
         'nextQuestHeader': self._award.getNextQuestHeader(),
         'nextQuestConditionsHeader': self._award.getNextQuestConditionsHeader(),
         'nextQuestConditions': self._award.getNextQuestConditions(),
         'additionalStatusText': self._award.getAdditionalStatusText(),
         'mainStatusText': self._award.getMainStatusText(),
         'availableText': self._award.getAvailableText(),
         'additionalStatusIcon': self._award.getAdditionalStatusIcon(),
         'mainStatusIcon': self._award.getMainStatusIcon(),
         'nextButtonText': self._award.getNextButtonText(),
         'nextButtonTooltip': self._award.getNextButtonTooltip(),
         'awards': self._award.getAwards(),
         'conditions': None,
         'isPersonalQuest': self._award.isPersonal(),
         'availableNextQuest': self._award.isNextAvailable(),
         'isLastQuest': self._award.isLast()}
