# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/TweenManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class TweenManagerMeta(BaseDAAPIModule):

    def createTween(self, tween):
        self._printOverrideError('createTween')

    def disposeTween(self, tween):
        self._printOverrideError('disposeTween')

    def disposeAll(self):
        self._printOverrideError('disposeAll')

    def as_setDataFromXmlS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDataFromXml(data)
