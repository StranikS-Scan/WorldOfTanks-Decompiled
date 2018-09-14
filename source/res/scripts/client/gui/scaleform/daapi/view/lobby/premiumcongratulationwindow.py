# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/PremiumCongratulationWindow.py
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardAbstract
from gui.Scaleform.daapi.view.meta.PremiumCongratulationWindowMeta import PremiumCongratulationWindowMeta
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
BUTTON_WIDTH = 120
BG_PADDING = -64
CLOSE_ACTION = 'closeAction'

class PremiumCongratulationWindow(PremiumCongratulationWindowMeta):

    def __init__(self, ctx = None):
        super(PremiumCongratulationWindow, self).__init__()
        raise 'award' in ctx and isinstance(ctx['award'], AwardAbstract) or AssertionError
        self.__award = ctx['award']

    def onBtnClick(self, action):
        if action == CLOSE_ACTION:
            self.onWindowClose()

    def onToBuyClick(self):
        self.onWindowClose()
        self.__award.handleBodyButton()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(PremiumCongratulationWindow, self)._populate()
        self.as_setImageS(self.__award.getBackgroundImage(), BG_PADDING)
        self.as_setWindowTitleS(self.__award.getWindowTitle())
        self.as_setTextS(self.__award.getHeader(), self.__award.getDescription())
        self.as_setDataS(self.__award.getAwardImage(), self.__award.getPercentDiscount(), self.__award.getBodyButtonText())
        self.as_setButtonsS(self.__getBtnData(), TEXT_ALIGN.RIGHT, BUTTON_WIDTH)

    def _dispose(self):
        super(PremiumCongratulationWindow, self)._dispose()

    def __getBtnData(self):
        return [{'label': self.__award.getCloseButtonText(),
          'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK,
          'action': CLOSE_ACTION,
          'isFocused': False,
          'tooltip': ''}]
