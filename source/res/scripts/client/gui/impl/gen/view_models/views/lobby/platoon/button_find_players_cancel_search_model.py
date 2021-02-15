# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/button_find_players_cancel_search_model.py
from gui.impl.gen.view_models.views.lobby.platoon.custom_sound_button_model import CustomSoundButtonModel

class ButtonFindPlayersCancelSearchModel(CustomSoundButtonModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=1):
        super(ButtonFindPlayersCancelSearchModel, self).__init__(properties=properties, commands=commands)

    def getIsLight(self):
        return self._getBool(5)

    def setIsLight(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ButtonFindPlayersCancelSearchModel, self)._initialize()
        self._addBoolProperty('isLight', True)
