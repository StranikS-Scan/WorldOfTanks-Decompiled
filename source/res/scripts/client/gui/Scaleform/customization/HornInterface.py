# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/customization/HornInterface.py
# Compiled at: 2011-12-20 18:23:08
import BigWorld
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.customization.HornSoundPlayer import HornSoundPlayer
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.customization.CustomizationInterface import CustomizationInterface
from gui.Scaleform.customization.data_providers import HornsDataProvider
from helpers import i18n

class HornInterface(CustomizationInterface):

    def __init__(self, name):
        super(HornInterface, self).__init__(name)
        self._currentHornID = None
        self._newHornID = None
        self.__hornSoundIndexes = {}
        self._player = HornSoundPlayer()
        self._player.onStartSoundEvent += self.__onStartHornSoundEvent
        self._player.onStopSoundEvent += self.__onStopHornSoundEvent
        return

    def __del__(self):
        LOG_DEBUG('HornInterface deleted')

    def populateUI(self, proxy):
        super(HornInterface, self).populateUI(proxy)
        self.uiHolder.addExternalCallbacks({'Customization.Vehicle.Horn.RequestCurrent': self.onRequestCurrentHorn,
         'Customization.Vehicle.Horn.SetHornID': self.onSetHornID,
         'Customization.Vehicle.Horn.List.SoundButtonPress': self.onSoundButtonPressInList,
         'Customization.Vehicle.Horn.List.SoundButtonRelease': self.onSoundButtonReleaseInList,
         'Customization.Vehicle.Horn.Current.SoundButtonPress': self.onSoundButtonPressForCurrent,
         'Customization.Vehicle.Horn.Current.SoundButtonRelease': self.onSoundButtonReleaseForCurrent,
         'Customization.Vehicle.Horn.New.SoundButtonPress': self.onSoundButtonPressForNew,
         'Customization.Vehicle.Horn.New.SoundButtonRelease': self.onSoundButtonReleaseForNew})
        self._hornsDP = HornsDataProvider('Customization.Vehicle.Horn.List')
        self._hornsDP.populateUI(proxy)

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('Customization.Vehicle.Horn.RequestCurrent', 'Customization.Vehicle.Horn.SetHornID', 'Customization.Vehicle.Horn.List.SoundButtonPress', 'Customization.Vehicle.Horn.List.SoundButtonRelease', 'Customization.Vehicle.Horn.Current.SoundButtonPress', 'Customization.Vehicle.Horn.Current.SoundButtonRelease', 'Customization.Vehicle.Horn.New.SoundButtonPress', 'Customization.Vehicle.Horn.New.SoundButtonRelease')
        self._hornsDP.dispossessUI()
        self._hornsDP = None
        self.__hornSoundIndexes.clear()
        self._player.fini()
        self._eventManager.clear()
        super(HornInterface, self).dispossessUI()
        return

    def fetchCurrentItem(self, vehDescr):
        self._currentHornID = vehDescr.hornID

    def invalidateData(self, vehType, refresh=False):
        if vehType is not None:
            self._hornsDP.setVehicleTypeParams(vehType.tags, vehType.hornPriceFactor)
        BigWorld.player().shop.getHornCost(lambda resultID, costs, rev: self.__onGetHornCost(resultID, costs, rev, refresh))
        return

    def isNewItemSelected(self):
        return self._newHornID is not None

    def getSelectedItemCost(self):
        return (self._hornsDP.getCost(self._newHornID), 1)

    def isCurrentItemRemove(self):
        return self._currentHornID is not None

    def change(self, vehInvID):
        if self._newHornID is None:
            message = i18n.makeString('#system_messages:customization/horn_not_selected')
            self.onCustomizationChangeFailed(message)
            return
        else:
            gold = self._hornsDP.getCost(self._newHornID)
            if gold < 0:
                message = i18n.makeString('#system_messages:customization/horn_cost_not_found')
                self.onCustomizationChangeFailed(message)
                return
            BigWorld.player().inventory.changeVehicleHorn(vehInvID, self._newHornID, lambda resultID: self.__onChangeVehicleHorn(resultID, gold))
            return

    def drop(self, vehInvID):
        if self._currentHornID is None:
            message = i18n.makeString('#system_messages:customization/horn_not_found_to_drop')
            self.onCustomizationDropFailed(message)
            return
        else:
            BigWorld.player().inventory.changeVehicleHorn(vehInvID, 0, self.__onDropVehicleHorn)
            return

    def update(self, vehicleDescr):
        hornID = vehicleDescr.hornID
        if hornID != self._currentHornID:
            self._currentHornID = hornID
            self._hornsDP.buildList(self._currentHornID)
            self.call('Customization.Vehicle.Horn.CurrentChanged')

    def __onGetHornCost(self, resultID, costs, _, refresh):
        if resultID < 0:
            SystemMessages.pushI18nMessage('#system_messages:customization/horn_get_cost_server_error', type=SystemMessages.SM_TYPE.Error)
        else:
            self._hornsDP.setHornDefCosts(costs)
            self._hornsDP.buildList(self._currentHornID)
        if refresh:
            self._newHornID = None
            self._hornsDP.refresh()
        LOG_DEBUG('HornInterface data inited.')
        self.onDataInited(self._name)
        return

    def __onChangeVehicleHorn(self, resultID, gold):
        if resultID < 0:
            message = i18n.makeString('#system_messages:customization/horn_change_server_error')
            self.onCustomizationChangeFailed(message)
            return
        else:
            self._currentHornID = self._newHornID
            self._newHornID = None
            self._hornsDP.buildList(self._currentHornID)
            self.call('Customization.Vehicle.Horn.ChangeSuccess')
            message = i18n.makeString('#system_messages:customization/horn_change_success', BigWorld.wg_getGoldFormat(gold))
            self.onCustomizationChangeSuccess(message, SystemMessages.SM_TYPE.CustomizationForGold)
            return

    def __onDropVehicleHorn(self, resultID):
        if resultID < 0:
            message = i18n.makeString('#system_messages:customization/horn_drop_server_error')
            self.onCustomizationDropFailed(message)
            return
        else:
            self._currentHornID = None
            self._hornsDP.buildList(None)
            self.call('Customization.Vehicle.Horn.DropSuccess')
            message = i18n.makeString('#system_messages:customization/horn_drop_success')
            self.onCustomizationDropSuccess(message)
            return

    def __playHornSound(self, hornID, index, place):
        if hornID is not None:
            self.__hornSoundIndexes[hornID] = [index, place]
            self._player.play(hornID)
        return

    def __onStartHornSoundEvent(self, hornID):
        params = self.__hornSoundIndexes.get(hornID)
        self.call('Customization.Vehicle.Horn.SoundPlay', params[:])

    def __onStopHornSoundEvent(self, _):
        self.call('Customization.Vehicle.Horn.SoundStop')

    def onRequestCurrentHorn(self, *args):
        parser = CommandArgsParser(self.onRequestCurrentHorn.__name__)
        parser.parse(*args)
        parser.addArgs(self._hornsDP.makeItem(self._currentHornID, False))
        self.respond(parser.args())

    def onSetHornID(self, *args):
        parser = CommandArgsParser(self.onSetHornID.__name__, 1, [int])
        hornID = parser.parse(*args)
        if self._currentHornID == hornID:
            self._newHornID = None
        else:
            self._newHornID = hornID
        return

    def onSoundButtonPressInList(self, *args):
        parser = CommandArgsParser(self.onSoundButtonPressInList.__name__, 1, [int])
        index = parser.parse(*args)
        hornID = self._hornsDP.requestItemAt(index)[0]
        self.__playHornSound(hornID, index, 'list')

    def onSoundButtonReleaseInList(self, *args):
        self._player.stopWithDelay()

    def onSoundButtonPressForCurrent(self, *args):
        self.__playHornSound(self._currentHornID, -1, 'current')

    def onSoundButtonReleaseForCurrent(self, *args):
        self._player.stopWithDelay()

    def onSoundButtonPressForNew(self, *args):
        self.__playHornSound(self._newHornID, -1, 'new')

    def onSoundButtonReleaseForNew(self, *args):
        self._player.stopWithDelay()
