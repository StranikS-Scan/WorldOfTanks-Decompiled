# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/extension_stubs/new_year.py
import logging
from skeletons.gui.impl import INewYearNavigation
_logger = logging.getLogger(__name__)

class NewYearNavigationStub(INewYearNavigation):

    @classmethod
    def showMainView(cls, objectName, instantly=False, viewAlias=None, *args, **kwargs):
        pass

    @classmethod
    def showInfoView(cls, previousViewAlias=None, *args, **kwargs):
        pass

    @classmethod
    def switchToIntro(cls):
        pass

    @classmethod
    def switchByAnchorName(cls, anchorName):
        pass

    @classmethod
    def switchFromStyle(cls, objectName, viewAlias=None, tabName=None, *args, **kwargs):
        pass

    @classmethod
    def switchToQuests(cls, *args, **kwargs):
        pass

    @classmethod
    def getCurrentViewName(cls):
        pass

    @classmethod
    def getPreviousObject(cls):
        pass

    @classmethod
    def switchToView(cls, aliasName, tabName=None, instantly=False, *args, **kwargs):
        pass

    @classmethod
    def clear(cls):
        pass

    @classmethod
    def getCurrentObject(cls):
        return None

    @classmethod
    def switchTo(cls, objectName, instantly=False, viewAlias=None, withFade=False, *args, **kwargs):
        _logger.warning('NewYearNavigationStub:switchByAnchorName objectName=%s', objectName)

    @classmethod
    def closeMainView(cls, switchCamera=False):
        return None
