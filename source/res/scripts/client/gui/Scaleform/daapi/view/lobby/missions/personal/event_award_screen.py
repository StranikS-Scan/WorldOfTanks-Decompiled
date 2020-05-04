# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/event_award_screen.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.EventAwardScreenMeta import EventAwardScreenMeta
from gui.Scaleform.genConsts.EVENT_AWARD_SCREEN_CONSTANTS import EVENT_AWARD_SCREEN_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.secret_event import SE20RewardComposer, RewardListMixin, VehicleMixin, AbilitiesMixin, EventViewMixin
from gui.server_events import events_dispatcher
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.pm_constants import SOUNDS
from helpers import int2roman
from helpers.CallbackDelayer import CallbackDelayer
from shared_utils import first
from gui.impl.lobby.secret_event.sound_constants import AWARD_SETTINGS

class EventAwardScreen(EventAwardScreenMeta, CallbackDelayer, EventViewMixin):
    __slots__ = ('__ctx', '__messages', '__currentMessage')
    _COMMON_SOUND_SPACE = AWARD_SETTINGS
    _VEHICLE_OFFSET = 5

    def __init__(self, ctx):
        super(EventAwardScreen, self).__init__()
        self.__ctx = ctx
        self.__messages = ctx.get('messages')
        self.__currentMessage = None
        self._eventCacheSubscribe()
        return

    def onPlaySound(self, soundType):
        self.soundManager.playSound(SOUNDS.TANK_AWARD_WINDOW)

    def onCloseWindow(self):
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MIN_MISSIONS_ZOOM)
        self.destroy()

    def _dispose(self):
        self.__showNextWindow()
        self._eventCacheUnsubscribe()
        super(EventAwardScreen, self)._dispose()

    def onButton(self):
        onButton = self.__currentMessage.get('onButton')
        if onButton is not None:
            onButton()
        return

    def _closeView(self):
        self._destroy()

    def _populate(self):
        super(EventAwardScreen, self)._populate()
        self.__currentMessage = first(self.__messages)
        name = self.__currentMessage['name']
        data = self.__getData()
        secretEvent = R.images.gui.maps.icons.secretEvent
        otherAwards = SE20RewardComposer(RewardListMixin.MAX_REWARDS_LIST_COUNT).getFormattedBonuses(self.__currentMessage['bonuses'], AWARDS_SIZES.BIG)
        vehicleAwards = []
        abilityAwards = []
        if name == 'general':
            contextObject = self.__currentMessage.get('contextObject')
            commander, item = contextObject['progress'], contextObject['item']
            level = item.getLevel()
            vehicle = VehicleMixin.getVehicleDataByLevel(commander, level)
            if vehicle:
                vehicle = vehicle.vehicle
                iconName = vehicle.name.split(':')[-1].replace('-', '_')
                vehicleAwards.append({'label': '',
                 'imgSource': backport.image(secretEvent.vehicles.c_80x80.dyn(iconName)()),
                 'tooltip': None,
                 'isSpecial': True,
                 'specialAlias': TOOLTIPS_CONSTANTS.EVENT_VEHICLE,
                 'specialArgs': [vehicle.intCD],
                 'hasCompensation': False,
                 'compensationReason': None,
                 'align': 'center',
                 'highlightType': '',
                 'overlayType': '',
                 'highlightIcon': '',
                 'overlayIcon': ''})
            for ability in AbilitiesMixin.getAbilitiesData(commander, level, level):
                abilityAwards.append({'label': '',
                 'imgSource': ability.icon,
                 'tooltip': None,
                 'isSpecial': True,
                 'specialAlias': TOOLTIPS_CONSTANTS.COMMANDER_ABILITY_INFO,
                 'specialArgs': [ability.id_, ''],
                 'hasCompensation': False,
                 'compensationReason': None,
                 'align': 'center',
                 'highlightType': '',
                 'overlayType': '',
                 'highlightIcon': '',
                 'overlayIcon': '',
                 'levelIcon': backport.image(secretEvent.tiers.skills.dyn('tier_{}'.format(ability.level))())})

        data.update({'closeBtnLabel': backport.text(R.strings.event.awardScreen.closeButton())})
        rendererYOffset = self._VEHICLE_OFFSET if self.__currentMessage['name'] == 'vehicle' else 0
        if vehicleAwards:
            data['prizeData']['vehicleAwards'] = {'rendererYOffset': rendererYOffset,
             'awards': vehicleAwards}
        if abilityAwards:
            data['prizeData']['abilityAwards'] = {'rendererYOffset': rendererYOffset,
             'awards': abilityAwards}
        if otherAwards:
            data['prizeData']['otherAwards'] = {'rendererYOffset': rendererYOffset,
             'awards': otherAwards}
        self.as_setDataS(data)
        self.soundManager.playSound(SOUNDS.TANK_AWARD_WINDOW)
        self.soundManager.setRTPC(SOUNDS.RTCP_OVERLAY, SOUNDS.MAX_MISSIONS_ZOOM)
        setShown = self.__currentMessage.get('setShown')
        if setShown is not None:
            setShown()
        return

    def __getData(self):
        name = self.__currentMessage['name']
        if name == 'vehicle':
            return self.__getVehicleData()
        if name == 'general':
            return self.__getGeneralData()
        return self.__getFrontData() if name == 'front' else None

    def __getVehicleData(self):
        icons = R.images.gui.maps.icons
        vehicle = self.__currentMessage['contextObject']['vehicle']
        level = self.__currentMessage['contextObject']['item'].getLevel()
        vehicleLevel = int2roman(vehicle.level)
        type_ = vehicle.type + '_elite' if vehicle.isElite else ''
        return {'headerLinkage': EVENT_AWARD_SCREEN_CONSTANTS.HEADER_VEHICLE_LINKAGE,
         'headerData': {'header': backport.text(R.strings.event.awardScreen.vehicle.header(), level=int2roman(level)),
                        'headerExtra': backport.text(R.strings.event.awardScreen.vehicle.headerExtra())},
         'prizeLinkage': EVENT_AWARD_SCREEN_CONSTANTS.MAIN_PRIZE_VEHICLE_LINKAGE,
         'prizeData': {'vehicleSrc': backport.image(icons.secretEvent.R175_IS_2E_446x316()),
                       'vehicleTypeIcon': backport.image(icons.vehicleTypes.big.dyn(type_)()),
                       'vehicleName': vehicle.userName,
                       'vehicleLevel': vehicleLevel},
         'background': backport.image(icons.secretEvent.backgrounds.tank_reward()),
         'buttonLinkage': EVENT_AWARD_SCREEN_CONSTANTS.BUTTON_VOLUMETRIC_LINKAGE,
         'buttonLabel': backport.text(R.strings.event.awardScreen.vehicle.button())}

    def __getGeneralData(self):
        contextObject = self.__currentMessage.get('contextObject', {})
        commander = contextObject.get('progress')
        item = contextObject.get('item')
        id_ = commander.getID()
        level = item.getLevel() + 1
        defaultIcon = R.images.gui.maps.icons.library.alertBigIcon
        secretEvent = R.images.gui.maps.icons.secretEvent
        awardScreen = R.strings.event.awardScreen
        return {'prizeLinkage': EVENT_AWARD_SCREEN_CONSTANTS.MAIN_PLATOON_LINKAGE,
         'prizeData': {'generalIconName': 'g_icon{}'.format(id_),
                       'tierLevel': level,
                       'header': makeHtmlString('html_templates:lobby/event_award_window', 'level_reached', {'level': int2roman(int(level))}),
                       'headerExtra': backport.text(awardScreen.general.headerExtra(), header=backport.text(R.strings.event.unit.name.num(id_)()))},
         'background': backport.image(secretEvent.backgrounds.dyn('unit_{}'.format(id_), defaultIcon)()),
         'buttonLinkage': EVENT_AWARD_SCREEN_CONSTANTS.BUTTON_FLAT_LINKAGE,
         'buttonLabel': backport.text(awardScreen.general.button())}

    def __getFrontData(self):
        contextObject = self.__currentMessage.get('contextObject', {})
        item = contextObject.get('item')
        secretEvent = R.images.gui.maps.icons.secretEvent
        awardScreen = R.strings.event.awardScreen
        return {'prizeLinkage': EVENT_AWARD_SCREEN_CONSTANTS.MAIN_UNIT_PROGRESSION_LINKAGE,
         'prizeData': {'header': makeHtmlString('html_templates:lobby/event_award_window', 'stage_completed', {'level': int2roman(item.getLevel())}),
                       'headerExtra': backport.text(awardScreen.player.headerExtra())},
         'background': backport.image(secretEvent.backgrounds.mission_completed()),
         'buttonLinkage': EVENT_AWARD_SCREEN_CONSTANTS.BUTTON_FLAT_LINKAGE,
         'buttonLabel': backport.text(awardScreen.general.button())}

    def __showNextWindow(self):
        self.__messages.pop(0)
        if self.__messages:
            self.delayCallback(0, events_dispatcher.showEventAwardScreen, self.__messages)
