# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GameLoadingMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.meta.DAAPISimpleContainerMeta import DAAPISimpleContainerMeta

class GameLoadingMeta(DAAPISimpleContainerMeta):

    def as_setLocaleS(self, locale):
        return self.flashObject.as_setLocale(locale) if self._isDAAPIInited() else None

    def as_setVersionS(self, version):
        return self.flashObject.as_setVersion(version) if self._isDAAPIInited() else None

    def as_setInfoS(self, info):
        return self.flashObject.as_setInfo(info) if self._isDAAPIInited() else None

    def as_setProgressS(self, progress):
        return self.flashObject.as_setProgress(progress) if self._isDAAPIInited() else None

    def as_updateStageS(self, width, height, scale):
        return self.flashObject.as_updateStage(width, height, scale) if self._isDAAPIInited() else None
