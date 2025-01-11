# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/techtree/tooltips/paragons_locked_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.techtree.tooltips.paragons_locked_tooltip_model import ParagonsLockedTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IParagonsController
from paragons_common import PARAGONS_UNLOCKS_PDATA_KEY

class ParagonsLockedTooltip(ViewImpl):
    __slots__ = ('__vehicleCD',)
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, vehicleCD=None):
        settings = ViewSettings(R.views.lobby.techtree.tooltips.ParagonsLockedTooltip())
        settings.model = ParagonsLockedTooltipModel()
        super(ParagonsLockedTooltip, self).__init__(settings)
        self.__vehicleCD = int(vehicleCD) if vehicleCD is not None else None
        return

    @property
    def viewModel(self):
        return super(ParagonsLockedTooltip, self).getViewModel()

    @property
    def config(self):
        return self.__paragonsController.config

    def _onLoading(self, *args, **kwargs):
        paragonsUnlockID = self.__getParagonsUnlockID()
        chapterID, levelID = self.__getChapterIDAndLevelID(paragonsUnlockID)
        with self.viewModel.transaction() as tx:
            tx.setLevel(levelID)
            tx.setChapterID(chapterID)

    def __getChapterIDAndLevelID(self, paragonsUnlockID):
        for chapterID, chapterData in self.config.rewards.iteritems():
            chapterLevels = chapterData.get('levels', {})
            for _, levelData in chapterLevels.iteritems():
                levelBonus = levelData.get('bonus')
                if PARAGONS_UNLOCKS_PDATA_KEY in levelBonus:
                    if paragonsUnlockID in levelBonus.get(PARAGONS_UNLOCKS_PDATA_KEY, {}).get('ids', set()):
                        return (chapterID, levelData.get('id'))

        return (None, None)

    def __getParagonsUnlockID(self):
        for paragonsUnlockID in self.config.paragonsUnlocks.iterkeys():
            if self.__vehicleCD in self.config.getParagonsUnlockVehicles(paragonsUnlockID):
                return paragonsUnlockID

        return None
