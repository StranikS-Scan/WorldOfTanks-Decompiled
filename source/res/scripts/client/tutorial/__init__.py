# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/__init__.py
from __future__ import absolute_import
from skeletons.tutorial import ITutorialLoader

def getTutorialConfig(manager):
    from tutorial.loader import TutorialLoader
    loader = TutorialLoader()
    loader.init()
    manager.addInstance(ITutorialLoader, loader, finalizer='fini')
