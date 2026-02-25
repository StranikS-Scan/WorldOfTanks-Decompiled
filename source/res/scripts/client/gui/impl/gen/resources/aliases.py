# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/aliases.py
from gui.impl.gen_utils import DynAccessor

class battle_modifiers(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Modifiers = DynAccessor(125299)

    shared = _shared(125300)


class battle_pass(DynAccessor):
    __slots__ = ()
    IntroVideo = DynAccessor(125302)
    ExtraVideo = DynAccessor(125303)
    Intro = DynAccessor(125304)
    ChapterChoice = DynAccessor(125305)
    Progression = DynAccessor(125306)
    PostProgression = DynAccessor(125307)
    BuyPass = DynAccessor(125308)
    BuyPassRewards = DynAccessor(125309)
    BuyLevels = DynAccessor(125310)
    BuyLevelsRewards = DynAccessor(125311)
    HolidayFinal = DynAccessor(125312)
    FinalRewardPreview = DynAccessor(125313)


class battle_result(DynAccessor):
    __slots__ = ()
    none = DynAccessor(125315)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        User = DynAccessor(125316)
        Vehicle = DynAccessor(125317)

    contextMenu = _contextMenu(125318)


class battle_results(DynAccessor):
    __slots__ = ()

    class _progression(DynAccessor):
        __slots__ = ()
        DailyMissions = DynAccessor(125320)
        WeeklyMissions = DynAccessor(125321)
        PersonalMissions = DynAccessor(125322)
        BattlePass = DynAccessor(125323)
        Prestige = DynAccessor(125324)
        BattleMatters = DynAccessor(125325)
        ModuleVehicleUnlocks = DynAccessor(125326)
        CommonQuests = DynAccessor(125327)

    progression = _progression(125328)


class common(DynAccessor):
    __slots__ = ()
    none = DynAccessor(125330)

    class _contextMenu(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(125331)

    contextMenu = _contextMenu(125332)

    class _tooltip(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(125333)
        Wulf = DynAccessor(125334)
        Param = DynAccessor(125335)

    tooltip = _tooltip(125336)

    class _popOver(DynAccessor):
        __slots__ = ()
        Backport = DynAccessor(125337)

    popOver = _popOver(125338)

    class _shared(DynAccessor):
        __slots__ = ()
        DynamicEconomics = DynAccessor(125339)

    shared = _shared(125340)


class hangar(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(125342)
        VehiclesStatistics = DynAccessor(125343)
        Consumables = DynAccessor(125344)
        Equipments = DynAccessor(125345)
        Instructions = DynAccessor(125346)
        Shells = DynAccessor(125347)
        Loadout = DynAccessor(125348)
        Crew = DynAccessor(125349)
        VehicleParams = DynAccessor(125350)
        ETEVehicleParams = DynAccessor(125351)
        CurrentVehicle = DynAccessor(125352)
        VehiclesInventory = DynAccessor(125353)
        MainMenu = DynAccessor(125354)
        VehicleMenu = DynAccessor(125355)
        LootboxEntryPoint = DynAccessor(125356)
        VehicleFilters = DynAccessor(125357)
        VehiclePlaylists = DynAccessor(125358)
        Teaser = DynAccessor(125359)
        OptionalDevicesAssistant = DynAccessor(125360)
        SpaceInteraction = DynAccessor(125361)
        HeroTank = DynAccessor(125362)
        UserMissions = DynAccessor(125363)
        ModeState = DynAccessor(125364)
        EasyTankEquip = DynAccessor(125365)
        PetEvent = DynAccessor(125366)
        PetObjectTooltip = DynAccessor(125367)
        Settings = DynAccessor(125368)
        KeyBindings = DynAccessor(125369)
        ManageableVehiclePlaylists = DynAccessor(125370)

    shared = _shared(125371)


class lobby_footer(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Platoon = DynAccessor(125373)
        ContactsList = DynAccessor(125374)
        SessionStats = DynAccessor(125375)
        VehicleCompare = DynAccessor(125376)
        NotificationsCenter = DynAccessor(125377)
        Chats = DynAccessor(125378)
        ReferralProgram = DynAccessor(125379)
        ServerInfo = DynAccessor(125380)

    default = _default(125381)


class lobby_header(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        FightStart = DynAccessor(125383)
        NavigationBar = DynAccessor(125384)
        Prebattle = DynAccessor(125385)
        Wallet = DynAccessor(125386)
        AccountDashboard = DynAccessor(125387)
        HeaderState = DynAccessor(125388)
        UserAccount = DynAccessor(125389)
        ReservesEntryPoint = DynAccessor(125390)
        PremShop = DynAccessor(125391)
        CurrentVehicle = DynAccessor(125392)

    default = _default(125393)


class select_vehicle(DynAccessor):
    __slots__ = ()

    class _select_vehicle(DynAccessor):
        __slots__ = ()
        VehiclesInfo = DynAccessor(125395)
        VehiclesInventory = DynAccessor(125396)
        VehiclesStatistics = DynAccessor(125397)
        VehicleFilters = DynAccessor(125398)
        VehiclePlaylists = DynAccessor(125399)

    select_vehicle = _select_vehicle(125400)


class states(DynAccessor):
    __slots__ = ()

    class _Hangar(DynAccessor):
        __slots__ = ()

        class _Loadout(DynAccessor):
            __slots__ = ()
            Equipment = DynAccessor(125402)
            Instructions = DynAccessor(125403)
            Shells = DynAccessor(125404)
            Consumables = DynAccessor(125405)

        Loadout = _Loadout(125406)
        Vehicles = DynAccessor(125407)

    Hangar = _Hangar(125408)


class user_missions(DynAccessor):
    __slots__ = ()

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        BattlePass = DynAccessor(125410)
        Events = DynAccessor(125411)
        Quests = DynAccessor(125412)
        EventMainInfoTip = DynAccessor(125413)

    hangarWidget = _hangarWidget(125414)

    class _hub(DynAccessor):
        __slots__ = ()

        class _basicMissions(DynAccessor):
            __slots__ = ()
            MainView = DynAccessor(125415)

            class _DailyMissionsSection(DynAccessor):
                __slots__ = ()
                MainView = DynAccessor(125416)
                DailyBlock = DynAccessor(125417)
                PremiumBlock = DynAccessor(125418)
                RewardProgressBlock = DynAccessor(125419)

            DailyMissionsSection = _DailyMissionsSection(125420)
            WeeklyMissions = DynAccessor(125421)
            PersonalMissions = DynAccessor(125422)

        basicMissions = _basicMissions(125423)

    hub = _hub(125424)


class vehicle_hub(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        VehicleParams = DynAccessor(125426)
        Wallet = DynAccessor(125427)
        VehicleInfo = DynAccessor(125428)
        ManageableVehiclePlaylists = DynAccessor(125429)
        VehiclesInfo = DynAccessor(125430)
        VehiclesStatistics = DynAccessor(125431)
        VehicleFilters = DynAccessor(125432)
        VehiclePlaylists = DynAccessor(125433)
        VehiclesInventory = DynAccessor(125434)

    default = _default(125435)


class vehicle_menu(DynAccessor):
    __slots__ = ()

    class _default(DynAccessor):
        __slots__ = ()
        Customization = DynAccessor(125437)
        CrewAutoReturn = DynAccessor(125438)
        CrewRetrain = DynAccessor(125439)
        QuickTraining = DynAccessor(125440)
        CrewOut = DynAccessor(125441)
        CrewBack = DynAccessor(125442)
        EasyEquip = DynAccessor(125443)
        ArmorInspector = DynAccessor(125444)
        FieldModification = DynAccessor(125445)
        NationChange = DynAccessor(125446)
        Research = DynAccessor(125447)
        AboutVehicle = DynAccessor(125448)
        Compare = DynAccessor(125449)
        Repairs = DynAccessor(125450)
        VehSkillTree = DynAccessor(125451)
        ProBoost = DynAccessor(125452)

    default = _default(125453)


class white_tiger(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        Carousel = DynAccessor(125455)
        ConsumablesPanel = DynAccessor(125456)
        Progression = DynAccessor(125457)
        Crewman = DynAccessor(125458)
        VehicleStats = DynAccessor(125459)
        ProgressionContent = DynAccessor(125460)
        ProgressionQuests = DynAccessor(125461)
        LootboxEntryPoint = DynAccessor(125462)

    shared = _shared(125463)


class battle_royale(DynAccessor):
    __slots__ = ()
    BattleSelector = DynAccessor(125465)
    UserMissions = DynAccessor(125466)
    VehiclesInventory = DynAccessor(125467)
    VehiclesFilter = DynAccessor(125468)
    AlertMessage = DynAccessor(125469)
    Header = DynAccessor(125470)
    LoadoutPanelContainer = DynAccessor(125471)
    Events = DynAccessor(125472)

    class _hangarWidget(DynAccessor):
        __slots__ = ()
        Progression = DynAccessor(125473)
        EventShop = DynAccessor(125474)

    hangarWidget = _hangarWidget(125475)

    class _loadoutPanelContainer(DynAccessor):
        __slots__ = ()
        Loadout = DynAccessor(125476)
        Commander = DynAccessor(125477)

    loadoutPanelContainer = _loadoutPanelContainer(125478)


class comp7(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(125480)
        Schedule = DynAccessor(125481)
        SeasonModifier = DynAccessor(125482)
        RoleSkillSlot = DynAccessor(125483)
        UserMissions = DynAccessor(125484)
        EntryPoint = DynAccessor(125485)
        WeeklyQuestsWidget = DynAccessor(125486)

    shared = _shared(125487)


class comp7_light(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        AlertMessage = DynAccessor(125489)
        SeasonModifier = DynAccessor(125490)
        RoleSkillSlot = DynAccessor(125491)
        UserMissions = DynAccessor(125492)
        EntryPoint = DynAccessor(125493)
        Quests = DynAccessor(125494)

    shared = _shared(125495)


class frontline(DynAccessor):
    __slots__ = ()

    class _loadout(DynAccessor):
        __slots__ = ()
        BattleAbilities = DynAccessor(125497)

    loadout = _loadout(125498)

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(125499)
        AlertMessage = DynAccessor(125500)

    shared = _shared(125501)


class fun_random(DynAccessor):
    __slots__ = ()

    class _shared(DynAccessor):
        __slots__ = ()
        UserMissions = DynAccessor(125503)
        ProgressionEntryPoint = DynAccessor(125504)

    shared = _shared(125505)


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
    select_vehicle = select_vehicle()
    states = states()
    user_missions = user_missions()
    vehicle_hub = vehicle_hub()
    vehicle_menu = vehicle_menu()
    white_tiger = white_tiger()
    battle_royale = battle_royale()
    comp7 = comp7()
    comp7_light = comp7_light()
    frontline = frontline()
    fun_random = fun_random()
