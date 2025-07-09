# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/profile/comp7_profile_technique_window.py
from comp7.gui.Scaleform.daapi.view.lobby.profile.comp7_profile_helper import getBattleHandlers
from comp7.gui.Scaleform.daapi.view.lobby.profile.profile_utils import COMP7_VEHICLE_STATISTICS_LAYOUT
from comp7.gui.Scaleform.daapi.view.lobby.profile.seasons_manager import getComp7SeasonManagers
from gui.Scaleform.daapi.view.lobby.profile.ProfileTechniqueWindow import ProfileTechniqueWindow
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R

class Comp7ProfileTechniqueWindow(ProfileTechniqueWindow):

    def __init__(self, *args):
        super(Comp7ProfileTechniqueWindow, self).__init__(*args)
        self._battleTypeHandlers.update(getBattleHandlers())
        self._seasonsManagers.update(getComp7SeasonManagers())

    @classmethod
    def _makeBattleTypesDropDown(cls, accountDossier, forVehiclesPage=False):
        result = super(Comp7ProfileTechniqueWindow, cls)._makeBattleTypesDropDown(accountDossier, forVehiclesPage)
        result.addByKey(PROFILE_DROPDOWN_KEYS.COMP7)
        return result

    def _getEmptyScreenLabel(self):
        return backport.text(R.strings.profile.section.technique.emptyScreenLabel.battleType.comp7()) if self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7 else super(Comp7ProfileTechniqueWindow, self)._getEmptyScreenLabel()

    def _getDefaultTableHeader(self, isFallout=False, showMarkOfMastery=False):
        isComp7BattleType = self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7
        result = super(Comp7ProfileTechniqueWindow, self)._getDefaultTableHeader(showMarkOfMastery=not isComp7BattleType)
        if isComp7BattleType:
            result.append(self._createTableBtnInfo('prestigePoints', 62 if self._isPrestigeVisible() else 70, 6, PROFILE.SECTION_TECHNIQUE_SORT_TOOLTIP_PRESTIGEPOINTS, 'descending', iconSource=RES_ICONS.MAPS_ICONS_FILTERS_PRESTIGEPOINTS))
        return result

    def _unpackVehicleParams(self, vehParams):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7:
            battlesCount, wins, xp, prestigePoints = vehParams
            avgPrestigePoints = round(float(prestigePoints) / float(battlesCount))
            return (battlesCount,
             wins,
             xp,
             avgPrestigePoints)
        return super(Comp7ProfileTechniqueWindow, self)._unpackVehicleParams(vehParams)

    def _getLayout(self):
        return COMP7_VEHICLE_STATISTICS_LAYOUT if self._battlesType == PROFILE_DROPDOWN_KEYS.COMP7 else super(Comp7ProfileTechniqueWindow, self)._getLayout()
