# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(124419)

    shared = _shared(124420)


class battle_pass(DynAccessor):
    __slots__ = ()
    IntroVideo = DynAccessor(124422)
    ExtraVideo = DynAccessor(124423)
    Intro = DynAccessor(124424)
    ChapterChoice = DynAccessor(124425)
    Progression = DynAccessor(124426)
    PostProgression = DynAccessor(124427)
    BuyPass = DynAccessor(124428)
    BuyPassConfirm = DynAccessor(124429)
    BuyPassRewards = DynAccessor(124430)
    BuyLevels = DynAccessor(124431)
    BuyLevelsRewards = DynAccessor(124432)
    HolidayFinal = DynAccessor(124433)
    FinalRewardPreview = DynAccessor(124434)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(124436)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(124437)
        Vehicle = DynAccessor(124438)

    contextMenu = _contextMenu(124439)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(124441)
        WeeklyMissions = DynAccessor(124442)
        PersonalMissions = DynAccessor(124443)
        BattlePass = DynAccessor(124444)
        Prestige = DynAccessor(124445)
        BattleMatters = DynAccessor(124446)
        ModuleVehicleUnlocks = DynAccessor(124447)
        CommonQuests = DynAccessor(124448)

    progression = _progression(124449)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(124451)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(124452)

    contextMenu = _contextMenu(124453)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(124454)
        Wulf = DynAccessor(124455)
        Param = DynAccessor(124456)

    tooltip = _tooltip(124457)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(124458)

    popOver = _popOver(124459)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(124460)

    shared = _shared(124461)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(124463)
        VehiclesStatistics = DynAccessor(124464)
        Consumables = DynAccessor(124465)
        Equipments = DynAccessor(124466)
        Instructions = DynAccessor(124467)
        Shells = DynAccessor(124468)
        Loadout = DynAccessor(124469)
        Crew = DynAccessor(124470)
        VehicleParams = DynAccessor(124471)
        ETEVehicleParams = DynAccessor(124472)
        CurrentVehicle = DynAccessor(124473)
        VehiclesInventory = DynAccessor(124474)
        MainMenu = DynAccessor(124475)
        VehicleMenu = DynAccessor(124476)
        LootboxEntryPoint = DynAccessor(124477)
        VehicleFilters = DynAccessor(124478)
        VehiclePlaylists = DynAccessor(124479)
        Teaser = DynAccessor(124480)
        OptionalDevicesAssistant = DynAccessor(124481)
        SpaceInteraction = DynAccessor(124482)
        HeroTank = DynAccessor(124483)
        UserMissions = DynAccessor(124484)
        ModeState = DynAccessor(124485)
        EasyTankEquip = DynAccessor(124486)
        PetEvent = DynAccessor(124487)
        PetObjectTooltip = DynAccessor(124488)
        Settings = DynAccessor(124489)
        KeyBindings = DynAccessor(124490)

    shared = _shared(124491)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(124493)
        ContactsList = DynAccessor(124494)
        SessionStats = DynAccessor(124495)
        VehicleCompare = DynAccessor(124496)
        NotificationsCenter = DynAccessor(124497)
        Chats = DynAccessor(124498)
        ReferralProgram = DynAccessor(124499)
        ServerInfo = DynAccessor(124500)

    default = _default(124501)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(124503)
        NavigationBar = DynAccessor(124504)
        Prebattle = DynAccessor(124505)
        Wallet = DynAccessor(124506)
        AccountDashboard = DynAccessor(124507)
        HeaderState = DynAccessor(124508)
        UserAccount = DynAccessor(124509)
        ReservesEntryPoint = DynAccessor(124510)
        PremShop = DynAccessor(124511)
        CurrentVehicle = DynAccessor(124512)

    default = _default(124513)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(124515)
            Instructions = DynAccessor(124516)
            Shells = DynAccessor(124517)
            Consumables = DynAccessor(124518)

        Loadout = _Loadout(124519)
        Vehicles = DynAccessor(124520)

    Hangar = _Hangar(124521)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(124523)
        Events = DynAccessor(124524)
        Quests = DynAccessor(124525)
        EventMainInfoTip = DynAccessor(124526)

    hangarWidget = _hangarWidget(124527)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(124528)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(124529)
                DailyBlock = DynAccessor(124530)
                PremiumBlock = DynAccessor(124531)
                RewardProgressBlock = DynAccessor(124532)

            DailyMissionsSection = _DailyMissionsSection(124533)
            WeeklyMissions = DynAccessor(124534)
            PersonalMissions = DynAccessor(124535)

        basicMissions = _basicMissions(124536)

    hub = _hub(124537)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(124539)
        Wallet = DynAccessor(124540)

    default = _default(124541)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(124543)
    UserMissions = DynAccessor(124544)
    VehiclesInventory = DynAccessor(124545)
    VehiclesFilter = DynAccessor(124546)
    AlertMessage = DynAccessor(124547)
    Header = DynAccessor(124548)
    LoadoutPanelContainer = DynAccessor(124549)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(124550)
        EventShop = DynAccessor(124551)

    hangarWidget = _hangarWidget(124552)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(124553)
        Commander = DynAccessor(124554)

    loadoutPanelContainer = _loadoutPanelContainer(124555)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(124557)
        Schedule = DynAccessor(124558)
        SeasonModifier = DynAccessor(124559)
        RoleSkillSlot = DynAccessor(124560)
        UserMissions = DynAccessor(124561)
        EntryPoint = DynAccessor(124562)
        WeeklyQuestsWidget = DynAccessor(124563)

    shared = _shared(124564)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(124566)
        SeasonModifier = DynAccessor(124567)
        RoleSkillSlot = DynAccessor(124568)
        UserMissions = DynAccessor(124569)
        EntryPoint = DynAccessor(124570)
        Quests = DynAccessor(124571)

    shared = _shared(124572)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(124574)

    loadout = _loadout(124575)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(124576)
        AlertMessage = DynAccessor(124577)

    shared = _shared(124578)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(124580)
        ProgressionEntryPoint = DynAccessor(124581)

    shared = _shared(124582)


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
