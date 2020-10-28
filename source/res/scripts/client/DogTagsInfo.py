# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DogTagsInfo.py
import typing
import BigWorld
import Event
if typing.TYPE_CHECKING:
    from typing import List, Tuple

class DogTagsInfo(BigWorld.DynamicScriptComponent):

    def __init__(self):
        self.__eManager = Event.EventManager()
        self.onUsedComponentsUpdated = Event.Event(self.__eManager)

    def setSlice_usedDogTagsComponents(self, changePath, oldValue):
        begin, end = changePath[0]
        newComponents = self.usedDogTagsComponents[begin:end]
        self.onUsedComponentsUpdated(newComponents)
