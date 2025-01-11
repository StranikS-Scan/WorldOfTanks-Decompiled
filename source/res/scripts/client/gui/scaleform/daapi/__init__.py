# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/__init__.py
from gui.Scaleform.framework.entities.View import View
from gui.shared.ny_vignette_settings_switcher import checkVignetteSettings

class LobbySubView(View):
    __background_alpha__ = 0.6

    def setEnvironment(self, app):
        checkVignetteSettings(self.uniqueName)
        app.setBackgroundAlpha(self.__background_alpha__)
        super(LobbySubView, self).setEnvironment(app)
