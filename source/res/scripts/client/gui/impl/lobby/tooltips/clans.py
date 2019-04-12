# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/clans.py
from frameworks.wulf import View, ViewFlags
from gui.impl.gen.view_models.views.lobby.tooltips.clan_short_info_content_model import ClanShortInfoContentModel
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.web import IWebController

class ClanShortInfoTooltipContent(View, ClanEmblemsHelper):
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self):
        super(ClanShortInfoTooltipContent, self).__init__(R.views.clanShortInfoTooltipContent(), ViewFlags.COMPONENT, ClanShortInfoContentModel)
        clanProfile = self.__webCtrl.getAccountProfile()
        self.requestClanEmblem32x32(clanProfile.getClanDbID())
        self.viewModel.setFullName(clanProfile.getClanFullName())

    @property
    def viewModel(self):
        return super(ClanShortInfoTooltipContent, self).getViewModel()

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if emblem:
            self.viewModel.setEmblem(self.getMemoryTexturePath(emblem))
