# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/dog_tags/dog_tag_marker_view.py
import BigWorld
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.dog_tags.dog_tag_marker_view_model import DogTagMarkerViewModel
from gui.battle_control.dog_tag_composer import DogTagComposerInBattleGF
from dog_tags_common.player_dog_tag import DisplayableDogTag, PlayerDogTag
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency

class DogTagMarkerView(ViewImpl):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, viewKey):
        self.__composer = DogTagComposerInBattleGF()
        self.__vehicleID = viewKey
        settings = ViewSettings(R.views.battle.dog_tags.DogTagMarkerView(), model=DogTagMarkerViewModel())
        super(DogTagMarkerView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DogTagMarkerView, self).getViewModel()

    def _onLoading(self):
        super(DogTagMarkerView, self)._onLoading()
        self.__update()

    def __update(self):
        playerInfo = self.__sessionProvider.getArenaDP().getVehicleInfo(self.__vehicleID).player
        dogTagInfo = BigWorld.entity(self.__vehicleID).dogTag['dogTag']
        dogTag = DisplayableDogTag(PlayerDogTag.fromDict(dogTagInfo), playerInfo.name, playerInfo.clanAbbrev)
        with self.viewModel.transaction() as tx:
            self.__composer.fillModel(tx, dogTag)
