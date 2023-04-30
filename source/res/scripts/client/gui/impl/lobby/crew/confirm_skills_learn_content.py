# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/confirm_skills_learn_content.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.confirm_skills_learn_view_model import ConfirmSkillsLearnViewModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import getCrewSkinIconBig, getBigIconPath
from gui.shared.gui_items.crew_skin import localizedFullName
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class ConfirmSkillsLearnContent(ViewImpl):
    __slots__ = ('dialogData',)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.instance(ILobbyContext)

    def __init__(self, dialogData):
        settings = ViewSettings(R.views.lobby.crew.ConfirmLearnSkillsContent())
        settings.model = ConfirmSkillsLearnViewModel()
        self.dialogData = dialogData
        super(ConfirmSkillsLearnContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ConfirmSkillsLearnContent, self).getViewModel()

    def _onLoading(self):
        super(ConfirmSkillsLearnContent, self)._onLoading()
        dd = self.dialogData
        tankman = self.itemsCache.items.getTankman(dd.tmanInvID)
        if tankman.isInSkin and self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            skinItem = self.itemsCache.items.getCrewSkin(tankman.skinID)
            tankmanIcon = getCrewSkinIconBig(skinItem.getIconID())
            fullUserName = localizedFullName(skinItem)
        else:
            tankmanIcon = getBigIconPath(tankman.nationID, tankman.descriptor.iconID)
            fullUserName = tankman.fullUserName
        with self.viewModel.transaction() as vm:
            vm.setName(fullUserName)
            vm.setIcon(tankmanIcon)
            vm.setAmount(dd.xpAmount)
            vm.setSkill(dd.skill.name)
            vm.setProgress(dd.level)
            vm.setRole(tankman.extensionLessIconRole)
