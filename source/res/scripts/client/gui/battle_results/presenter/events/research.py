# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/events/research.py
import typing
from frameworks.wulf import Array
from gui.battle_results.br_constants import BattleResultsRecord
from gui.battle_results.components.progress import MIN_BATTLES_TO_SHOW_PROGRESS
from gui.battle_results.reusable.progress import VehicleProgressHelper
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.events.crew_member_new_skills import CrewMemberNewSkills
from gui.impl.gen.view_models.views.lobby.postbattle.events.crew_member import CrewMember
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.crew_skin import localizedFullName
from helpers import dependency
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.events.base_event_model import BaseEventModel

def getResearchEvents(tooltipData, reusable, result):
    unlocks = []
    skills = Array()
    for intCD, data in reusable.personal.getVehicleCDsIterator(result[BattleResultsRecord.PERSONAL]):
        tankmenXps = dict(data.get('xpByTmen', []))
        helper = VehicleProgressHelper(intCD)
        _getNewSkilledTankmenVOs(skills, helper, tankmenXps)
        helper.clear()

    if skills:
        sectionSkills = CrewMemberNewSkills()
        sectionSkills.setTitle(R.strings.battle_results.common.crewMember.newSkill())
        sectionSkills.setCrewMembers(skills)
    return unlocks


def _getNewSkilledTankmenVOs(skills, helper, tankmenXps):
    for tman, isCompletedSkill in helper.getNewSkilledTankmen(tankmenXps):
        avgBattles2NewSkill = 0
        if not isCompletedSkill:
            avgBattles2NewSkill = helper.getAvgBattles2NewSkill(tman)
            if avgBattles2NewSkill <= 0 or avgBattles2NewSkill > MIN_BATTLES_TO_SHOW_PROGRESS:
                continue
        skills.addViewModel(_createCrewMemberItem(tman, avgBattles2NewSkill))


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def _createCrewMemberItem(tman, avgBattles2NewSkill, itemsCache=None, lobbyContext=None):
    model = CrewMember()
    model.setId(tman.invID)
    model.setBattlesLeft(avgBattles2NewSkill if avgBattles2NewSkill > 0 else 0)
    model.setRole(tman.roleUserName)
    if tman.skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(tman.skinID)
        model.setIcon(R.images.gui.maps.icons.tankmen.icons.small.crewSkins.dyn(skinItem.getIconID()))
        model.setName(localizedFullName(skinItem))
    else:
        model.setIcon(R.images.gui.maps.icons.tankmen.icons.small.dyn(Tankman.getIconName(tman.nationID, tman.descriptor.iconID).replace('.png', '').replace('-', '_'))())
        model.setName(tman.fullUserName)
    return model
