# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/ability_indicators/panel.py
from functools import partial
import BigWorld
import GUI
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class AbilityIndicatorsPanel(object):
    __slots__ = ('__indicators', '__window', '__order')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __HEIGHT_PER_ITEM = 25

    def __init__(self):
        self.__indicators = {}
        self.__order = []
        self.__window = w = GUI.Window('helpers/maps/col_dark_gray.dds')
        w.horizontalAnchor = 'LEFT'
        w.verticalAnchor = 'CENTER'
        w.horizontalPositionMode = 'PIXEL'
        w.verticalPositionMode = 'PIXEL'
        w.widthMode = 'PIXEL'
        w.heightMode = 'PIXEL'
        w.position = (0, 400, 1)
        w.width = 130
        w.height = 0
        GUI.addRoot(w)
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onEquipmentComponentUpdated.subscribe(self.__onEquipmentComponentUpdated)
        return

    def destroy(self):
        GUI.delRoot(self.__window)
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onEquipmentComponentUpdated.unsubscribe(self.__onEquipmentComponentUpdated)
        self.__indicators = None
        return

    def __onEquipmentComponentUpdated(self, equipmentName, vehicleID, abilityInfo):
        if vehicleID != BigWorld.player().getObservedVehicleID():
            return
        else:
            if abilityInfo.endTime - BigWorld.serverTime() > 0 and equipmentName is not None:
                self.__updateText(equipmentName, *abilityInfo)
            elif equipmentName in self.__indicators:
                text, callbackID = self.__indicators.pop(equipmentName)
                BigWorld.cancelCallback(callbackID)
                self.__window.delChild(text)
                idx = self.__order.index(equipmentName)
                self.__window.height -= self.__HEIGHT_PER_ITEM
                for compactDescr in self.__order[idx + 1:]:
                    self.__indicators[compactDescr][0].position.y -= self.__HEIGHT_PER_ITEM

                del self.__order[idx]
            return

    def __updateText(self, equipmentName, endTime, *args):
        if not self.__indicators:
            return
        if equipmentName in self.__indicators:
            text, callbackID = self.__indicators.pop(equipmentName)
            BigWorld.cancelCallback(callbackID)
        else:
            text = self.__createText()
            self.__order.append(equipmentName)
        values = []
        for value in args:
            if isinstance(value, float):
                value = round(value, 3)
            values.append(str(value))

        text.text = equipmentName + ' ' + ' | '.join((str(int(round(endTime - BigWorld.serverTime()))),) + tuple(values))
        callbackID = BigWorld.callback(1, partial(self.__updateText, equipmentName, endTime, *args))
        self.__indicators[equipmentName] = (text, callbackID)

    def __createText(self):
        text = GUI.Text('')
        text.explicitSize = True
        text.size = (0.17, 0.05)
        text.colour = (0, 0, 0, 255)
        text.horizontalAnchor = 'LEFT'
        text.verticalAnchor = 'TOP'
        text.horizontalPositionMode = 'PIXEL'
        text.verticalPositionMode = 'PIXEL'
        text.position = (0, len(self.__indicators) * self.__HEIGHT_PER_ITEM, 1)
        self.__window.height += self.__HEIGHT_PER_ITEM
        self.__window.addChild(text)
        return text
