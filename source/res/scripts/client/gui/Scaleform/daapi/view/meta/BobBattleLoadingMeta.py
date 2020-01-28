# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BobBattleLoadingMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BobBattleLoadingMeta(BaseDAAPIComponent):

    def as_setBloggerIdsS(self, bloggerLeftId, bloggerRightId):
        return self.flashObject.as_setBloggerIds(bloggerLeftId, bloggerRightId) if self._isDAAPIInited() else None
