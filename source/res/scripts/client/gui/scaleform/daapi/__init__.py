# Embedded file name: scripts/client/gui/Scaleform/daapi/__init__.py
from gui.Scaleform.framework.entities.View import View

class LobbySubView(View):
    __background_alpha__ = 0.6

    def seEnvironment(self, app):
        app.setBackgroundAlpha(self.__background_alpha__)
        super(LobbySubView, self).seEnvironment(app)
