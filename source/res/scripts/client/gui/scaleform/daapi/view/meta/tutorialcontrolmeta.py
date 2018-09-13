# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TutorialControlMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TutorialControlMeta(DAAPIModule):

    def restart(self):
        self._printOverrideError('restart')

    def refuse(self):
        self._printOverrideError('refuse')

    def as_setupS(self, config):
        if self._isDAAPIInited():
            return self.flashObject.as_setup(config)

    def as_setPlayerXPLevelS(self, level):
        if self._isDAAPIInited():
            return self.flashObject.as_setPlayerXPLevel(level)

    def as_setChapterInfoS(self, title, description):
        if self._isDAAPIInited():
            return self.flashObject.as_setChapterInfo(title, description)

    def as_clearChapterInfoS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_clearChapterInfo()

    def as_setRunModeS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_setRunMode()

    def as_setRestartModeS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_setRestartMode()

    def as_setDisabledS(self, flag):
        if self._isDAAPIInited():
            return self.flashObject.as_setDisabled(flag)
