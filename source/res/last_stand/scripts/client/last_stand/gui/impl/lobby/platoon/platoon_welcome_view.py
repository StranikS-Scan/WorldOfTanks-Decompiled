# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/platoon/platoon_welcome_view.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_welcome_view import WelcomeView
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from last_stand.gui.impl.gen.view_models.views.lobby.ext_platoon_dropdown_model import ExtPlatoonDropdownModel
from last_stand.gui.ls_gui_constants import QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from last_stand.gui.impl.lobby.platoon.platoon_search_view import LSSearchView

class LSWelcomeView(WelcomeView):
    __platoonCtrl = dependency.descriptor(IPlatoonController)
    _layoutID = R.views.last_stand.lobby.PlatoonDropdown()

    @property
    def _viewModelClass(self):
        return ExtPlatoonDropdownModel

    def _setBattleTypeRelatedProps(self):
        queueType = self.__platoonCtrl.getQueueType()
        backgrounds = R.images.last_stand.gui.maps.icons.platoon.platoon_dropdown
        with self.viewModel.transaction() as model:
            levelInfo = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType]
            model.setBattleType(backport.text(R.strings.last_stand_lobby.headerButtons.battle.types.last_stand()))
            model.setBackgroundImage(backport.image(backgrounds.dyn('header_bg_difficulty_{}'.format(levelInfo))()))
            model.setSelectedDifficulty(levelInfo)

    def _onFind(self):
        self.__platoonCtrl.createPlatoon(startAutoSearchOnUnitJoin=True)
        LSSearchView.resetState()
