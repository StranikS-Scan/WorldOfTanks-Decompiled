# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/resources/strings_entries/ingame_gui.py
from gui.impl.gen_utils import DynAccessor

class IngameGui(DynAccessor):
    __slots__ = ()

    class aim(DynAccessor):
        __slots__ = ()
        zoom = 1589

    class attackReason(DynAccessor):
        __slots__ = ()
        artilleryProtection = 1623
        artillery_sector = 1624
        bombers = 1625

    class battleEndWarning(DynAccessor):
        __slots__ = ()
        text = 1594

    class battleMessenger(DynAccessor):
        __slots__ = ()

        class toxic(DynAccessor):
            __slots__ = ()

            class blackList(DynAccessor):
                __slots__ = ()

                class ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1600
                    header = 1599

                class CANT_ADD_IN_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1602
                    header = 1601

                class REMOVE_FROM_BLACKLIST(DynAccessor):
                    __slots__ = ()
                    body = 1604
                    header = 1603

    class battleProgress(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            description = 1632
            noBindingKey = 1639
            press = 1631

    class chat_example(DynAccessor):
        __slots__ = ()
        attack = 1159
        attack_enemy = 1164
        attention_to_cell = 1163
        back_to_base = 1160
        follow_me = 1158

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 1146
                save_tanks = 1140
                time = 1141

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 1147
                save_tanks = 1138
                time = 1142

            class lane(DynAccessor):
                __slots__ = ()
                center = 1144
                east = 1145
                west = 1143

        help_me = 1156
        help_me_ex = 1157
        negative = 1162
        positive = 1161
        reloading_cassette = 1150
        reloading_gun = 1149
        reloading_ready = 1151
        reloading_ready_cassette = 1153
        reloading_unavailable = 1154
        spg_aim_area = 1165
        stop = 1155
        support_me_with_fire = 1148
        turn_back = 1152

    class chat_shortcuts(DynAccessor):
        __slots__ = ()
        attack = 1115
        attack_enemy = 1136
        attack_enemy_reloading = 1137
        attention_to_base_atk = 1125
        attention_to_base_def = 1126
        attention_to_cell = 1119
        attention_to_objective_atk = 1123
        attention_to_objective_def = 1124
        attention_to_position = 1122
        back_to_base = 1116
        follow_me = 1114

        class global_msg(DynAccessor):
            __slots__ = ()

            class atk(DynAccessor):
                __slots__ = ()
                focus_hq = 1134
                save_tanks = 1127
                time = 1129

            class c_def(DynAccessor):
                __slots__ = ()
                focus_hq = 1135
                save_tanks = 1128
                time = 1130

            class lane(DynAccessor):
                __slots__ = ()
                center = 1132
                east = 1133
                west = 1131

        help_me = 1112
        help_me_ex = 1113
        negative = 1118
        positive = 1117
        reloading_cassette = 1107
        reloading_gun = 1106
        reloading_ready = 1108
        reloading_ready_cassette = 1109
        reloading_unavailable = 1110
        spg_aim_area = 1120
        spg_aim_area_reloading = 1121
        stop = 1111
        support_me_with_fire = 1105
        turn_back = 1104

    class colorSettingsTipPanel(DynAccessor):
        __slots__ = ()
        btnLabel = 1633

    class consumables_panel(DynAccessor):
        __slots__ = ()

        class equipment(DynAccessor):
            __slots__ = ()
            cooldownSeconds = 1273

            class tooltip(DynAccessor):
                __slots__ = ()
                empty = 1272

    class countRibbons(DynAccessor):
        __slots__ = ()
        multiSeparator = 1534

    class cruise_ctrl(DynAccessor):
        __slots__ = ()
        speedMetric = 1271

    class damageIndicator(DynAccessor):
        __slots__ = ()
        multiplier = 1595

    class damageLog(DynAccessor):
        __slots__ = ()
        multiplier = 1558

        class shellType(DynAccessor):
            __slots__ = ()
            ARMOR_PIERCING = 1553
            ARMOR_PIERCING_CR = 1556
            ARMOR_PIERCING_HE = 1555
            HIGH_EXPLOSIVE = 1554
            HOLLOW_CHARGE = 1557

    class damage_panel(DynAccessor):
        __slots__ = ()

        class crew(DynAccessor):
            __slots__ = ()

            class commander(DynAccessor):
                __slots__ = ()
                destroyed = 1256
                normal = 1255

            class driver(DynAccessor):
                __slots__ = ()
                destroyed = 1258
                normal = 1257

            class gunner1(DynAccessor):
                __slots__ = ()
                destroyed = 1264
                normal = 1263

            class gunner2(DynAccessor):
                __slots__ = ()
                destroyed = 1266
                normal = 1265

            class loader1(DynAccessor):
                __slots__ = ()
                destroyed = 1268
                normal = 1267

            class loader2(DynAccessor):
                __slots__ = ()
                destroyed = 1270
                normal = 1269

            class radioman1(DynAccessor):
                __slots__ = ()
                destroyed = 1260
                normal = 1259

            class radioman2(DynAccessor):
                __slots__ = ()
                destroyed = 1262
                normal = 1261

        class devices(DynAccessor):
            __slots__ = ()

            class ammoBay(DynAccessor):
                __slots__ = ()
                critical = 1238
                destroyed = 1239
                normal = 1237

            class chassis(DynAccessor):
                __slots__ = ()
                critical = 1244
                destroyed = 1245
                normal = 1243

            class engine(DynAccessor):
                __slots__ = ()
                critical = 1232
                destroyed = 1233
                normal = 1231

            class fuelTank(DynAccessor):
                __slots__ = ()
                critical = 1250
                destroyed = 1251
                normal = 1249

            class gun(DynAccessor):
                __slots__ = ()
                critical = 1235
                destroyed = 1236
                normal = 1234

            class radio(DynAccessor):
                __slots__ = ()
                critical = 1247
                destroyed = 1248
                normal = 1246

            class surveyingDevice(DynAccessor):
                __slots__ = ()
                critical = 1253
                destroyed = 1254
                normal = 1252

            class track(DynAccessor):
                __slots__ = ()
                critical = 1241
                destroyed = 1242
                normal = 1240

            class turretRotator(DynAccessor):
                __slots__ = ()
                critical = 1229
                destroyed = 1230
                normal = 1228

    class devices(DynAccessor):
        __slots__ = ()
        ammo_bay = 1037
        chassis = 1045
        engine = 1036
        fuel_tank = 1038
        gun = 1042
        left_track = 1040
        radio = 1039
        right_track = 1041
        surveing_device = 1044
        turret_rotator = 1043

    class distance(DynAccessor):
        __slots__ = ()
        meters = 1590

    class dynamicSquad(DynAccessor):
        __slots__ = ()

        class ally(DynAccessor):
            __slots__ = ()
            add = 1580
            disabled = 1582
            received = 1587
            wasSent = 1584

        class enemy(DynAccessor):
            __slots__ = ()
            add = 1581
            disabled = 1583
            received = 1588
            wasSent = 1585

        invite = 1586

    class efficiencyRibbons(DynAccessor):
        __slots__ = ()
        armor = 1535
        assistByAbility = 1619
        assistSpot = 1544
        assistTrack = 1543
        burn = 1539
        capture = 1536
        crits = 1545
        damage = 1537
        defence = 1540
        defenderBonus = 1618
        destructibleDamaged = 1615
        destructibleDestroyed = 1616
        destructiblesDefended = 1617
        enemySectorCaptured = 1614
        kill = 1541
        ram = 1538
        receivedBurn = 1549
        receivedCrits = 1547
        receivedDamage = 1548
        receivedRam = 1550
        receivedWorldCollision = 1551
        spotted = 1542
        stun = 1559
        vehicleRecovery = 1552
        worldCollision = 1546

    class epic_players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class hidden(DynAccessor):
                __slots__ = ()
                body = 1303
                header = 1302
                note = 1304

            class medium_player(DynAccessor):
                __slots__ = ()
                body = 1309
                header = 1308
                note = 1310

            class medium_tank(DynAccessor):
                __slots__ = ()
                body = 1312
                header = 1311
                note = 1313

            class short(DynAccessor):
                __slots__ = ()
                body = 1306
                header = 1305
                note = 1307

            class toggle(DynAccessor):
                __slots__ = ()
                body = 1315
                header = 1314
                note = 1316

    class flagNotification(DynAccessor):
        __slots__ = ()
        flagAbsorbed = 1576
        flagCaptured = 1573
        flagDelivered = 1575
        flagInbase = 1574

    class flags(DynAccessor):
        __slots__ = ()
        timer = 1533

    class fortConsumables(DynAccessor):
        __slots__ = ()

        class timer(DynAccessor):
            __slots__ = ()
            postfix = 1532

    class hitMarker(DynAccessor):
        __slots__ = ()
        blocked = 1560
        critical = 1562
        ricochet = 1561

    class marker(DynAccessor):
        __slots__ = ()
        meters = 1139

    class personalMissions(DynAccessor):
        __slots__ = ()

        class tip(DynAccessor):
            __slots__ = ()
            additionalHeader = 1529
            mainHeader = 1528

            class noQuests(DynAccessor):
                __slots__ = ()
                battleType = 1531
                vehicleType = 1530

    class player_errors(DynAccessor):
        __slots__ = ()

        class cant_move(DynAccessor):
            __slots__ = ()
            chassis_damaged = 1053
            crew_inactive = 1051
            engine_damaged = 1052

        class cant_shoot(DynAccessor):
            __slots__ = ()
            crew_inactive = 1055
            gun_damaged = 1057
            gun_locked = 1059
            gun_reload = 1058
            no_ammo = 1056
            vehicle_destroyed = 1054

        class cant_switch(DynAccessor):
            __slots__ = ()
            engine_destroyed = 1060

        class equipment(DynAccessor):
            __slots__ = ()
            alreadyActivated = 1061

            class extinguisher(DynAccessor):
                __slots__ = ()
                doesNotActivated = 1067

            isInCooldown = 1062

            class medkit(DynAccessor):
                __slots__ = ()
                allTankmenAreSafe = 1064
                tankmanIsSafe = 1063

            class order(DynAccessor):
                __slots__ = ()
                notReady = 1068

            class repairkit(DynAccessor):
                __slots__ = ()
                allDevicesAreNotDamaged = 1066
                deviceIsNotDamaged = 1065

    class player_messages(DynAccessor):
        __slots__ = ()
        ALLY_HIT = 1081
        COMBAT_EQUIPMENT_READY_ARTILLERY = 1429
        COMBAT_EQUIPMENT_READY_BOMBER = 1430
        COMBAT_EQUIPMENT_READY_INSPIRE = 1433
        COMBAT_EQUIPMENT_READY_RECON = 1431
        COMBAT_EQUIPMENT_READY_SMOKE = 1432
        COMBAT_EQUIPMENT_USED_ARTILLERY = 1434
        COMBAT_EQUIPMENT_USED_BOMBER = 1435
        COMBAT_EQUIPMENT_USED_INSPIRE = 1438
        COMBAT_EQUIPMENT_USED_RECON = 1436
        COMBAT_EQUIPMENT_USED_SMOKE = 1437
        DEATH_FROM_ARTILLERY_ALLY_ALLY = 1391
        DEATH_FROM_ARTILLERY_ALLY_ENEMY = 1392
        DEATH_FROM_ARTILLERY_ALLY_SUICIDE = 1388
        DEATH_FROM_ARTILLERY_ENEMY_ALLY = 1394
        DEATH_FROM_ARTILLERY_ENEMY_ENEMY = 1393
        DEATH_FROM_ARTILLERY_ENEMY_SUICIDE = 1387
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ALLY = 1398
        DEATH_FROM_ARTILLERY_PROTECTION_UNKNOWN_ENEMY = 1397
        DEATH_FROM_BOMBER_ALLY_SUICIDE = 1390
        DEATH_FROM_BOMBER_ENEMY_SUICIDE = 1389
        DEATH_FROM_DEATH_ZONE_ALLY_ALLY = 1486
        DEATH_FROM_DEATH_ZONE_ALLY_ENEMY = 1487
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1485
        DEATH_FROM_DEATH_ZONE_ALLY_SUICIDE = 1484
        DEATH_FROM_DEATH_ZONE_ENEMY_ALLY = 1490
        DEATH_FROM_DEATH_ZONE_ENEMY_ENEMY = 1491
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1489
        DEATH_FROM_DEATH_ZONE_ENEMY_SUICIDE = 1488
        DEATH_FROM_DEATH_ZONE_SELF_ALLY = 1482
        DEATH_FROM_DEATH_ZONE_SELF_ENEMY = 1483
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1481
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 1410
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 1408
        DEATH_FROM_DROWNING_ALLY_ALLY = 1423
        DEATH_FROM_DROWNING_ALLY_ENEMY = 1424
        DEATH_FROM_DROWNING_ALLY_SELF = 1422
        DEATH_FROM_DROWNING_ALLY_SUICIDE = 1421
        DEATH_FROM_DROWNING_ENEMY_ALLY = 1427
        DEATH_FROM_DROWNING_ENEMY_ENEMY = 1428
        DEATH_FROM_DROWNING_ENEMY_SELF = 1426
        DEATH_FROM_DROWNING_ENEMY_SUICIDE = 1425
        DEATH_FROM_DROWNING_SELF_ALLY = 1419
        DEATH_FROM_DROWNING_SELF_ENEMY = 1420
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1418
        DEATH_FROM_GAS_ATTACK_ALLY_ALLY = 1495
        DEATH_FROM_GAS_ATTACK_ALLY_ENEMY = 1496
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 1494
        DEATH_FROM_GAS_ATTACK_ENEMY_ALLY = 1498
        DEATH_FROM_GAS_ATTACK_ENEMY_ENEMY = 1499
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 1497
        DEATH_FROM_GAS_ATTACK_SELF_ALLY = 1492
        DEATH_FROM_GAS_ATTACK_SELF_ENEMY = 1493
        DEATH_FROM_INACTIVE_CREW = 1407
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 1405
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ALLY = 1467
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_ENEMY = 1468
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1466
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SUICIDE = 1465
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ALLY = 1471
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_ENEMY = 1472
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1470
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SUICIDE = 1469
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ALLY = 1463
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_ENEMY = 1464
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1462
        DEATH_FROM_OVERTURN_ALLY_ALLY = 1518
        DEATH_FROM_OVERTURN_ALLY_ENEMY = 1519
        DEATH_FROM_OVERTURN_ALLY_SELF = 1517
        DEATH_FROM_OVERTURN_ALLY_SUICIDE = 1516
        DEATH_FROM_OVERTURN_ENEMY_ALLY = 1522
        DEATH_FROM_OVERTURN_ENEMY_ENEMY = 1523
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1521
        DEATH_FROM_OVERTURN_ENEMY_SUICIDE = 1520
        DEATH_FROM_OVERTURN_SELF_ALLY = 1514
        DEATH_FROM_OVERTURN_SELF_ENEMY = 1515
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1513
        DEATH_FROM_RAMMING_ALLY_ALLY = 1511
        DEATH_FROM_RAMMING_ALLY_ENEMY = 1512
        DEATH_FROM_RAMMING_ALLY_SELF = 1510
        DEATH_FROM_RAMMING_ALLY_SUICIDE = 1509
        DEATH_FROM_RAMMING_ENEMY_ALLY = 1526
        DEATH_FROM_RAMMING_ENEMY_ENEMY = 1527
        DEATH_FROM_RAMMING_ENEMY_SELF = 1525
        DEATH_FROM_RAMMING_ENEMY_SUICIDE = 1524
        DEATH_FROM_RAMMING_SELF_ALLY = 1507
        DEATH_FROM_RAMMING_SELF_ENEMY = 1508
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1506
        DEATH_FROM_RECOVERY_ALLY_SUICIDE = 1396
        DEATH_FROM_RECOVERY_ENEMY_SUICIDE = 1395
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ALLY = 1402
        DEATH_FROM_SECTOR_BOMBERS_UNKNOWN_ENEMY = 1401
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ALLY = 1400
        DEATH_FROM_SECTOR_PROTECTION_UNKNOWN_ENEMY = 1399
        DEATH_FROM_SHOT_ALLY_ALLY = 1369
        DEATH_FROM_SHOT_ALLY_ALLY_ARTILLERY = 1370
        DEATH_FROM_SHOT_ALLY_ALLY_BOMBER = 1371
        DEATH_FROM_SHOT_ALLY_ENEMY = 1372
        DEATH_FROM_SHOT_ALLY_ENEMY_ARTILLERY = 1373
        DEATH_FROM_SHOT_ALLY_ENEMY_BOMBER = 1374
        DEATH_FROM_SHOT_ALLY_SUICIDE = 1375
        DEATH_FROM_SHOT_ALLY_SUICIDE_ARTILLERY = 1376
        DEATH_FROM_SHOT_ALLY_SUICIDE_BOMBER = 1377
        DEATH_FROM_SHOT_ENEMY_ALLY = 1381
        DEATH_FROM_SHOT_ENEMY_ALLY_ARTILLERY = 1382
        DEATH_FROM_SHOT_ENEMY_ALLY_BOMBER = 1383
        DEATH_FROM_SHOT_ENEMY_ENEMY = 1384
        DEATH_FROM_SHOT_ENEMY_ENEMY_ARTILLERY = 1385
        DEATH_FROM_SHOT_ENEMY_ENEMY_BOMBER = 1386
        DEATH_FROM_SHOT_ENEMY_SUICIDE = 1378
        DEATH_FROM_SHOT_ENEMY_SUICIDE_ARTILLERY = 1379
        DEATH_FROM_SHOT_ENEMY_SUICIDE_BOMBER = 1380
        DEATH_FROM_SHOT_SELF_ALLY = 1363
        DEATH_FROM_SHOT_SELF_ALLY_ARTILLERY = 1364
        DEATH_FROM_SHOT_SELF_ALLY_BOMBER = 1365
        DEATH_FROM_SHOT_SELF_ENEMY = 1366
        DEATH_FROM_SHOT_SELF_ENEMY_ARTILLERY = 1367
        DEATH_FROM_SHOT_SELF_ENEMY_BOMBER = 1368
        DEATH_FROM_WORLD_COLLISION_ALLY_ALLY = 1450
        DEATH_FROM_WORLD_COLLISION_ALLY_ENEMY = 1451
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1449
        DEATH_FROM_WORLD_COLLISION_ALLY_SUICIDE = 1448
        DEATH_FROM_WORLD_COLLISION_ENEMY_ALLY = 1454
        DEATH_FROM_WORLD_COLLISION_ENEMY_ENEMY = 1455
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1453
        DEATH_FROM_WORLD_COLLISION_ENEMY_SUICIDE = 1452
        DEATH_FROM_WORLD_COLLISION_SELF_ALLY = 1446
        DEATH_FROM_WORLD_COLLISION_SELF_ENEMY = 1447
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1445
        DESTRUCTIBLE_DESTROYED_ALLY = 1606
        DESTRUCTIBLE_DESTROYED_ENEMY = 1607
        DESTRUCTIBLE_DESTROYED_SELF = 1605
        DEVICE_CRITICAL_AT_FIRE = 1073
        DEVICE_CRITICAL_AT_SHOT = 1069
        DEVICE_DESTROYED_AT_FIRE = 1076
        DEVICE_DESTROYED_AT_SHOT = 1070
        DEVICE_REPAIRED = 1080
        DEVICE_REPAIRED_TO_CRITICAL = 1077
        DEVICE_STARTED_FIRE_AT_SHOT = 1071
        ENGINE_CRITICAL_AT_UNLIMITED_RPM = 1074
        ENGINE_DESTROYED_AT_UNLIMITED_RPM = 1075
        FIRE_STOPPED = 1078
        TANKMAN_HIT_AT_SHOT = 1072
        TANKMAN_RESTORED = 1079
        allied_team_name = 1089
        ally_base_captured_by_notification = 1085
        ally_base_captured_notification = 1082
        base_capture_blocked = 1088
        base_captured_by_notification = 1087
        base_captured_notification = 1084
        enemy_base_captured_by_notification = 1086
        enemy_base_captured_notification = 1083
        enemy_team_name = 1090
        loader_intuition_was_used = 1103

        class postmortem_caption(DynAccessor):
            __slots__ = ()
            other = 1093
            self = 1092

        postmortem_caption_ = 1091
        postmortem_userNoHasAmmo = 1094
        replayControlsHelp1 = 1100
        replayControlsHelp2 = 1101
        replayControlsHelp3 = 1102
        replayFreeCameraActivated = 1096
        replayPaused = 1099
        replaySavedCameraActivated = 1097
        replaySpeedChange = 1098
        tank_in_fire = 1095

    class players_panel(DynAccessor):
        __slots__ = ()

        class state(DynAccessor):
            __slots__ = ()

            class large(DynAccessor):
                __slots__ = ()
                body = 1295
                header = 1294
                note = 1296

            class medium(DynAccessor):
                __slots__ = ()
                body = 1289
                header = 1288
                note = 1290

            class medium2(DynAccessor):
                __slots__ = ()
                body = 1292
                header = 1291
                note = 1293

            class none(DynAccessor):
                __slots__ = ()
                body = 1283
                header = 1282
                note = 1284

            class short(DynAccessor):
                __slots__ = ()
                body = 1286
                header = 1285
                note = 1287

        unknown_clan = 1301
        unknown_frags = 1299
        unknown_name = 1297
        unknown_vehicle = 1298
        unknown_vehicleState = 1300

    class postmortem(DynAccessor):
        __slots__ = ()

        class tips(DynAccessor):
            __slots__ = ()

            class exitHangar(DynAccessor):
                __slots__ = ()
                label = 1280
                text = 1281

            class observerMode(DynAccessor):
                __slots__ = ()
                label = 1278
                text = 1279

    class postmortem_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1478
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1476
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1474
        DEATH_FROM_DEVICE_EXPLOSION_AT_FIRE = 1411
        DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT = 1409
        DEATH_FROM_DROWNING_ALLY_SELF = 1417
        DEATH_FROM_DROWNING_ENEMY_SELF = 1415
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1413
        DEATH_FROM_FIRE = 1404
        DEATH_FROM_INACTIVE_CREW_AT_SHOT = 1406
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1461
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1459
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1457
        DEATH_FROM_OVERTURN_ALLY_SELF = 1362
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1361
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1360
        DEATH_FROM_RAMMING_ALLY_SELF = 1505
        DEATH_FROM_RAMMING_ENEMY_SELF = 1503
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1501
        DEATH_FROM_SHOT = 1354
        DEATH_FROM_SHOT_ARTILLERY = 1358
        DEATH_FROM_SHOT_BOMBER = 1359
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1444
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1442
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1440
        DEATH_UNKNOWN = 1355

    class recovery(DynAccessor):
        __slots__ = ()
        cooldown = 1622
        hint1 = 1620
        hint2 = 1621

    class repairPoint(DynAccessor):
        __slots__ = ()
        title = 1592
        unavailable = 1593

    class respawnView(DynAccessor):
        __slots__ = ()
        additionalTip = 1564
        additionalTipLimited = 1565
        classNotAvailable = 1572
        cooldownLbl = 1566
        destroyedLbl = 1567
        disabledLbl = 1568
        emptySlotInfo = 1570
        emptySlotInfoTooltip = 1571
        nextVehicleName = 1569
        title = 1563

    class rewardWindow(DynAccessor):
        __slots__ = ()

        class base(DynAccessor):
            __slots__ = ()
            btnLabel = 1638
            descText = 1637
            headerText = 1636
            subHeaderText = 1635

        winHeaderText = 1634

    class scorePanel(DynAccessor):
        __slots__ = ()
        mySquadLbl = 1578
        playerScore = 1579
        squadLbl = 1577

    class shells_kinds(DynAccessor):
        __slots__ = ()
        ARMOR_PIERCING = 1223
        ARMOR_PIERCING_CR = 1225
        ARMOR_PIERCING_HE = 1224
        HIGH_EXPLOSIVE = 1222
        HOLLOW_CHARGE = 1221
        params = 1226
        stunParams = 1227

    class siegeMode(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()

            class forMode(DynAccessor):
                __slots__ = ()
                c_0 = 1609
                c_1 = 1610
                c_2 = 1611
                c_3 = 1612

            noBinding = 1613
            press = 1608

    class statistics(DynAccessor):
        __slots__ = ()
        exit = 1190

        class final(DynAccessor):
            __slots__ = ()
            heroes = 1213

            class lifeInfo(DynAccessor):
                __slots__ = ()
                alive = 1214
                dead = 1215

            class personal(DynAccessor):
                __slots__ = ()
                capturePoints = 1211
                damaged = 1206
                directHits = 1209
                directHitsReceived = 1210
                droppedCapturePoints = 1212
                killed = 1205
                postmortem = 1204
                shots = 1208
                spotted = 1207

            class reasons(DynAccessor):
                __slots__ = ()
                reason0 = 1194
                reason1lose = 1196
                reason1tie = 1197
                reason1win = 1195
                reason2 = 1198
                reason3 = 1199

            class stats(DynAccessor):
                __slots__ = ()
                credits = 1202
                experience = 1201
                multipliedExp = 1200
                repair = 1203

            class status(DynAccessor):
                __slots__ = ()
                lose = 1193
                tie = 1191
                win = 1192

        header = 1178

        class headers(DynAccessor):
            __slots__ = ()
            header0 = 1182
            header1 = 1183
            header2 = 1184
            header3 = 1185
            header4 = 1186

        class playerState(DynAccessor):
            __slots__ = ()
            c_0 = 1216
            c_1 = 1218
            c_2 = 1217
            c_3 = 1219
            c_4 = 1220

        class tab(DynAccessor):
            __slots__ = ()

            class line_up(DynAccessor):
                __slots__ = ()
                header = 1166
                title = 1167

            class progressTracing(DynAccessor):
                __slots__ = ()
                notAvailable = 1179

            class quests(DynAccessor):
                __slots__ = ()
                header = 1168

                class notAvailable(DynAccessor):
                    __slots__ = ()
                    title = 1177

                class nothingToPerform(DynAccessor):
                    __slots__ = ()
                    descr = 1175
                    title = 1174

                class status(DynAccessor):
                    __slots__ = ()
                    done = 1172
                    fullDone = 1173
                    inProgress = 1169
                    increaseResult = 1171
                    onPause = 1170

                class switchOff(DynAccessor):
                    __slots__ = ()
                    title = 1176

        class tabs(DynAccessor):
            __slots__ = ()
            group = 1187
            heroes = 1189
            personal = 1188

        team1title = 1180
        team2title = 1181

    class stun(DynAccessor):
        __slots__ = ()
        indicator = 1629
        seconds = 1630

    tabStatsHint = 1591

    class tankmen(DynAccessor):
        __slots__ = ()
        commander = 1046
        driver = 1047
        gunner = 1049
        loader = 1050
        radioman = 1048

    class timer(DynAccessor):
        __slots__ = ()
        battlePeriod = 1277
        started = 1276
        starting = 1275
        waiting = 1274

    class trajectoryView(DynAccessor):
        __slots__ = ()

        class hint(DynAccessor):
            __slots__ = ()
            alternateModeLeft = 1627
            alternateModeRight = 1628
            noBindingKey = 1626

    class vehicle_messages(DynAccessor):
        __slots__ = ()
        DEATH_FROM_DEATH_ZONE_ALLY_SELF = 1477
        DEATH_FROM_DEATH_ZONE_ENEMY_SELF = 1475
        DEATH_FROM_DEATH_ZONE_SELF_SUICIDE = 1473
        DEATH_FROM_DROWNING_ALLY_SELF = 1416
        DEATH_FROM_DROWNING_ENEMY_SELF = 1414
        DEATH_FROM_DROWNING_SELF_SUICIDE = 1412
        DEATH_FROM_FIRE = 1403
        DEATH_FROM_GAS_ATTACK_ALLY_SELF = 1480
        DEATH_FROM_GAS_ATTACK_ENEMY_SELF = 1479
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ALLY_SELF = 1460
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_ENEMY_SELF = 1458
        DEATH_FROM_INACTIVE_CREW_AT_WORLD_COLLISION_SELF_SUICIDE = 1456
        DEATH_FROM_OVERTURN_ALLY_SELF = 1598
        DEATH_FROM_OVERTURN_ENEMY_SELF = 1597
        DEATH_FROM_OVERTURN_SELF_SUICIDE = 1596
        DEATH_FROM_RAMMING_ALLY_SELF = 1504
        DEATH_FROM_RAMMING_ENEMY_SELF = 1502
        DEATH_FROM_RAMMING_SELF_SUICIDE = 1500
        DEATH_FROM_SHOT = 1353
        DEATH_FROM_SHOT_ARTILLERY = 1356
        DEATH_FROM_SHOT_BOMBER = 1357
        DEATH_FROM_WORLD_COLLISION_ALLY_SELF = 1443
        DEATH_FROM_WORLD_COLLISION_ENEMY_SELF = 1441
        DEATH_FROM_WORLD_COLLISION_SELF_SUICIDE = 1439
        DEVICE_CRITICAL_AT_RAMMING_ALLY_ALLY = 1334
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SELF = 1331
        DEVICE_CRITICAL_AT_RAMMING_ALLY_SUICIDE = 1332
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_ALLY = 1333
        DEVICE_CRITICAL_AT_RAMMING_ENEMY_SELF = 1330
        DEVICE_CRITICAL_AT_RAMMING_SELF_SUICIDE = 1329
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_ALLY = 1322
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SELF = 1319
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ALLY_SUICIDE = 1320
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_ALLY = 1321
        DEVICE_CRITICAL_AT_WORLD_COLLISION_ENEMY_SELF = 1318
        DEVICE_CRITICAL_AT_WORLD_COLLISION_SELF_SUICIDE = 1317
        DEVICE_DESTROYED_AT_RAMMING_ALLY_ALLY = 1340
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SELF = 1337
        DEVICE_DESTROYED_AT_RAMMING_ALLY_SUICIDE = 1338
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_ALLY = 1339
        DEVICE_DESTROYED_AT_RAMMING_ENEMY_SELF = 1336
        DEVICE_DESTROYED_AT_RAMMING_SELF_SUICIDE = 1335
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_ALLY = 1328
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SELF = 1325
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ALLY_SUICIDE = 1326
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_ALLY = 1327
        DEVICE_DESTROYED_AT_WORLD_COLLISION_ENEMY_SELF = 1324
        DEVICE_DESTROYED_AT_WORLD_COLLISION_SELF_SUICIDE = 1323
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_ALLY = 1346
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SELF = 1343
        DEVICE_STARTED_FIRE_AT_RAMMING_ALLY_SUICIDE = 1344
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_ALLY = 1345
        DEVICE_STARTED_FIRE_AT_RAMMING_ENEMY_SELF = 1342
        DEVICE_STARTED_FIRE_AT_RAMMING_SELF_SUICIDE = 1341
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_ALLY = 1352
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SELF = 1349
        TANKMAN_HIT_AT_WORLD_COLLISION_ALLY_SUICIDE = 1350
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_ALLY = 1351
        TANKMAN_HIT_AT_WORLD_COLLISION_ENEMY_SELF = 1348
        TANKMAN_HIT_AT_WORLD_COLLISION_SELF_SUICIDE = 1347
