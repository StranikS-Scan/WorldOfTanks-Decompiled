# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/tutorial.py
from __future__ import absolute_import
import typing
if typing.TYPE_CHECKING:
    from tutorial.data.client_triggers import ClientTriggers
    from tutorial.gui import IGuiImpl
    from tutorial.core import Tutorial
    ComponentID = str

class IGuiController(object):

    def init(self, guiProviders):
        raise NotImplementedError

    def setup(self, isEnabled=False, path=''):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def lastHangarMenuButtonsOverride(self):
        raise NotImplementedError

    @property
    def lastHeaderMenuButtonsOverride(self):
        raise NotImplementedError

    @property
    def hangarHeaderEnabled(self):
        raise NotImplementedError

    @property
    def lastBattleSelectorHintOverride(self):
        raise NotImplementedError

    def setHintsWithClientTriggers(self, clientTriggers):
        raise NotImplementedError

    def getViewTutorialID(self, name):
        raise NotImplementedError

    def getFoundComponentsIDs(self):
        raise NotImplementedError

    def setCriteria(self, name, value):
        raise NotImplementedError

    def setViewCriteria(self, componentID, viewUniqueName):
        raise NotImplementedError

    def setTriggers(self, componentID, triggers):
        raise NotImplementedError

    def clearTriggers(self, componentID):
        raise NotImplementedError

    def showInteractiveHint(self, componentID, content, triggers=None, silent=False):
        raise NotImplementedError

    def closeInteractiveHint(self, componentID):
        raise NotImplementedError

    def setComponentProps(self, componentID, props):
        raise NotImplementedError

    def playComponentAnimation(self, componentID, animType):
        raise NotImplementedError

    def stopComponentAnimation(self, componentID, animType):
        raise NotImplementedError

    def showBootcampHint(self, componentID):
        raise NotImplementedError

    def hideBootcampHint(self, componentID):
        raise NotImplementedError

    def setupViewContextHints(self, viewTutorialID, hintsData):
        raise NotImplementedError

    def overrideHangarMenuButtons(self, buttonsList=None):
        raise NotImplementedError

    def overrideHeaderMenuButtons(self, buttonsList=None):
        raise NotImplementedError

    def setHangarHeaderEnabled(self, enabled):
        raise NotImplementedError

    def overrideBattleSelectorHint(self, overrideType=None):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class ITutorialLoader(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def tutorial(self):
        raise NotImplementedError

    @property
    def tutorialID(self):
        raise NotImplementedError

    @property
    def isRunning(self):
        raise NotImplementedError

    @property
    def gui(self):
        raise NotImplementedError

    def isTutorialStopped(self):
        raise NotImplementedError

    def run(self, settingsID, state=None):
        raise NotImplementedError

    def stop(self, restore=True):
        raise NotImplementedError

    def refuse(self):
        raise NotImplementedError
