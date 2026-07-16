# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/platoon/platoon_search_view.py
from __future__ import absolute_import
from skeletons.gui.game_control import IPlatoonController
from helpers import dependency
from gui.impl.lobby.platoon.view.platoon_search_view import SearchView
from gui.impl.gen import R
from gui.impl import backport
from last_stand.gui.impl.gen.view_models.views.lobby.ext_searching_dropdown_model import ExtSearchingDropdownModel
from last_stand.gui.ls_gui_constants import QUEUE_TYPE_TO_DIFFICULTY_LEVEL

class LSSearchView(SearchView):
    _layoutID = R.views.last_stand.lobby.SearchingDropdown()
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    @property
    def _viewModelClass(self):
        return ExtSearchingDropdownModel

    def _setBackgroundImage(self):
        queueType = self.__platoonCtrl.getQueueType()
        levelInfo = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType]
        backgrounds = R.images.last_stand.gui.maps.icons.platoon.platoon_dropdown
        with self.viewModel.transaction() as model:
            model.setBackgroundImage(backport.image(backgrounds.dyn('header_bg_difficulty_{}'.format(levelInfo))()))
            model.setSelectedDifficulty(levelInfo)
