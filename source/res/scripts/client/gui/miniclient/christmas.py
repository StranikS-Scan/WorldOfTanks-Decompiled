# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/christmas.py
from gui.Scaleform.locale.MENU import MENU
from helpers import aop

class _FalseGetter(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return False


class _WarningTextGetter(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return (MENU.AWARDWINDOW_CHRISTMAS_MINICLIENT_WARNING, MENU.AWARDWINDOW_CHRISTMAS_MINICLIENT_WARNINGLINK)


class _ButtonStatedGetter(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return (False, False, False)


def initChristmasPointcut():
    aop.Pointcut('gui.christmas.christmas_controller', '_ChristmasController', 'isEventInProgress', aspects=(_FalseGetter,))


def initAwardAutoAnimationStartPointcut():
    aop.Pointcut('gui.awards.special_achievement_awards', 'ChristmasAward', 'getAutoAnimationStart', aspects=(_FalseGetter,))


def initAwardgWarningTextsPointcut():
    aop.Pointcut('gui.awards.special_achievement_awards', 'ChristmasAward', 'getWarningTexts', aspects=(_WarningTextGetter,))


def initAwardgButtonStatesPointcut():
    aop.Pointcut('gui.awards.special_achievement_awards', 'ChristmasAward', 'getButtonStates', aspects=(_ButtonStatedGetter,))


def initAwardgCheckBoxPointcut():
    aop.Pointcut('gui.awards.special_achievement_awards', 'ChristmasAward', 'hasCheckBox', aspects=(_FalseGetter,))
