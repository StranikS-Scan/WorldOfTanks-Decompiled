# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/FortTransportationViewHelper.py
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.formatters import time_formatters
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS

class FortTransportationViewHelper(FortViewHelper):

    def _makeBuildingData(self, buildingDescr, direction, position, onlyBaseData = True, animation = FORTIFICATION_ALIASES.WITHOUT_ANIMATION):
        data = super(FortTransportationViewHelper, self)._makeBuildingData(buildingDescr, direction, position, onlyBaseData, animation)
        data.update({'transportTooltipData': self.__getTransportingBuildTooltipData(buildingDescr)})
        return data

    def isOnNextTransportingStep(self):
        raise NotImplementedError

    def __getTransportingBuildTooltipData(self, building):
        state = None
        headerArgs = {}
        bodyArgs = {}
        if building is not None:
            buildingName = building.userName
            if building.isInCooldown():
                state = 'cooldown'
                timeStr = time_formatters.getTimeDurationStr(building.getEstimatedCooldown())
                headerArgs = {'buildingName': buildingName}
                bodyArgs = {'time': timeStr}
            elif not building.hasStorageToExport():
                state = 'emptyStorage'
                headerArgs = {'buildingName': buildingName}
            elif not building.hasSpaceToImport() and self.isOnNextTransportingStep():
                state = 'notEmptySpace'
                headerArgs = {'buildingName': buildingName}
            elif not building.isReady():
                state = 'foundation'
        else:
            state = 'foundation'
        if state == 'foundation':
            headerArgs = {'buildingName': i18n.makeString(FORTIFICATIONS.BUILDINGS_TROWELLABEL)}
        if state is not None:
            header = TOOLTIPS.fortification_transporting(state + '/header')
            body = TOOLTIPS.fortification_transporting(state + '/body')
            return [i18n.makeString(header, **headerArgs), i18n.makeString(body, **bodyArgs)]
        else:
            return
            return
