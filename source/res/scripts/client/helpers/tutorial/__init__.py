# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/tutorial/__init__.py
from helpers.tutorial.stubs import StubTutorialLoader
from skeletons.tutorial import ITutorialLoader

def getTutorialConfig(manager):
    manager.addInstance(ITutorialLoader, StubTutorialLoader(), finalizer='fini')
