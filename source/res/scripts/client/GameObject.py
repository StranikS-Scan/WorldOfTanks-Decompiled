# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/GameObject.py
import importlib
import BigWorld

class GameObject(BigWorld.Entity):

    def onEnterWorld(self, prereqs):
        module = importlib.import_module(self.clientScript)
        getattr(module, self.clientFunction)(self)
