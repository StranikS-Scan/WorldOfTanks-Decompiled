# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(124611)

    shared = _shared(124612)


class battle_pass(DynAccessor):
    __slots__ = ()
    IntroVideo = DynAccessor(124614)
    ExtraVideo = DynAccessor(124615)
    Intro = DynAccessor(124616)
    ChapterChoice = DynAccessor(124617)
    Progression = DynAccessor(124618)
    PostProgression = DynAccessor(124619)
    BuyPass = DynAccessor(124620)
    BuyPassConfirm = DynAccessor(124621)
    BuyPassRewards = DynAccessor(124622)
    BuyLevels = DynAccessor(124623)
    BuyLevelsRewards = DynAccessor(124624)
    HolidayFinal = DynAccessor(124625)
    FinalRewardPreview = DynAccessor(124626)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(124628)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(124629)
        Vehicle = DynAccessor(124630)

    contextMenu = _contextMenu(124631)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(124633)
        WeeklyMissions = DynAccessor(124634)
        PersonalMissions = DynAccessor(124635)
        BattlePass = DynAccessor(124636)
        Prestige = DynAccessor(124637)
        BattleMatters = DynAccessor(124638)
        ModuleVehicleUnlocks = DynAccessor(124639)
        CommonQuests = DynAccessor(124640)

    progression = _progression(124641)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(124643)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(124644)

    contextMenu = _contextMenu(124645)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(124646)
        Wulf = DynAccessor(124647)
        Param = DynAccessor(124648)

    tooltip = _tooltip(124649)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(124650)

    popOver = _popOver(124651)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(124652)

    shared = _shared(124653)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(124655)
        VehiclesStatistics = DynAccessor(124656)
        Consumables = DynAccessor(124657)
        Equipments = DynAccessor(124658)
        Instructions = DynAccessor(124659)
        Shells = DynAccessor(124660)
        Loadout = DynAccessor(124661)
        Crew = DynAccessor(124662)
        VehicleParams = DynAccessor(124663)
        ETEVehicleParams = DynAccessor(124664)
        CurrentVehicle = DynAccessor(124665)
        VehiclesInventory = DynAccessor(124666)
        MainMenu = DynAccessor(124667)
        VehicleMenu = DynAccessor(124668)
        LootboxEntryPoint = DynAccessor(124669)
        VehicleFilters = DynAccessor(124670)
        VehiclePlaylists = DynAccessor(124671)
        Teaser = DynAccessor(124672)
        OptionalDevicesAssistant = DynAccessor(124673)
        SpaceInteraction = DynAccessor(124674)
        HeroTank = DynAccessor(124675)
        UserMissions = DynAccessor(124676)
        ModeState = DynAccessor(124677)
        EasyTankEquip = DynAccessor(124678)
        PetEvent = DynAccessor(124679)
        PetObjectTooltip = DynAccessor(124680)
        Settings = DynAccessor(124681)
        KeyBindings = DynAccessor(124682)

    shared = _shared(124683)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(124685)
        ContactsList = DynAccessor(124686)
        SessionStats = DynAccessor(124687)
        VehicleCompare = DynAccessor(124688)
        NotificationsCenter = DynAccessor(124689)
        Chats = DynAccessor(124690)
        ReferralProgram = DynAccessor(124691)
        ServerInfo = DynAccessor(124692)

    default = _default(124693)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(124695)
        NavigationBar = DynAccessor(124696)
        Prebattle = DynAccessor(124697)
        Wallet = DynAccessor(124698)
        AccountDashboard = DynAccessor(124699)
        HeaderState = DynAccessor(124700)
        UserAccount = DynAccessor(124701)
        ReservesEntryPoint = DynAccessor(124702)
        PremShop = DynAccessor(124703)
        CurrentVehicle = DynAccessor(124704)

    default = _default(124705)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(124707)
            Instructions = DynAccessor(124708)
            Shells = DynAccessor(124709)
            Consumables = DynAccessor(124710)

        Loadout = _Loadout(124711)
        Vehicles = DynAccessor(124712)

    Hangar = _Hangar(124713)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(124715)
        Events = DynAccessor(124716)
        Quests = DynAccessor(124717)
        EventMainInfoTip = DynAccessor(124718)

    hangarWidget = _hangarWidget(124719)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(124720)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(124721)
                DailyBlock = DynAccessor(124722)
                PremiumBlock = DynAccessor(124723)
                RewardProgressBlock = DynAccessor(124724)

            DailyMissionsSection = _DailyMissionsSection(124725)
            WeeklyMissions = DynAccessor(124726)
            PersonalMissions = DynAccessor(124727)

        basicMissions = _basicMissions(124728)

    hub = _hub(124729)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(124731)
        Wallet = DynAccessor(124732)

    default = _default(124733)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(124735)
    UserMissions = DynAccessor(124736)
    VehiclesInventory = DynAccessor(124737)
    VehiclesFilter = DynAccessor(124738)
    AlertMessage = DynAccessor(124739)
    Header = DynAccessor(124740)
    LoadoutPanelContainer = DynAccessor(124741)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(124742)
        EventShop = DynAccessor(124743)

    hangarWidget = _hangarWidget(124744)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(124745)
        Commander = DynAccessor(124746)

    loadoutPanelContainer = _loadoutPanelContainer(124747)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(124749)
        Schedule = DynAccessor(124750)
        SeasonModifier = DynAccessor(124751)
        RoleSkillSlot = DynAccessor(124752)
        UserMissions = DynAccessor(124753)
        EntryPoint = DynAccessor(124754)
        WeeklyQuestsWidget = DynAccessor(124755)

    shared = _shared(124756)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(124758)
        SeasonModifier = DynAccessor(124759)
        RoleSkillSlot = DynAccessor(124760)
        UserMissions = DynAccessor(124761)
        EntryPoint = DynAccessor(124762)
        Quests = DynAccessor(124763)

    shared = _shared(124764)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(124766)

    loadout = _loadout(124767)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(124768)
        AlertMessage = DynAccessor(124769)

    shared = _shared(124770)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(124772)
        ProgressionEntryPoint = DynAccessor(124773)

    shared = _shared(124774)


class Aliases(DynAccessor):
    __slots__ = ()
    battle_modifiers = battle_modifiers()
    battle_pass = battle_pass()
    battle_result = battle_result()
    battle_results = battle_results()
    common = common()
    hangar = hangar()
    lobby_footer = lobby_footer()
    lobby_header = lobby_header()
    states = states()
    user_missions = user_missions()
    vehicle_hub = vehicle_hub()
    battle_royale = battle_royale()
    comp7 = comp7()
    comp7_light = comp7_light()
    frontline = frontline()
    fun_random = fun_random()
