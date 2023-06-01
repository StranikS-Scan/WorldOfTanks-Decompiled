# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/rare_achievements.py
import functools
import ResMgr
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION

def __makeAchievementFileRequest(urlName, params, achievementId, callback):
    url = __buildRareImageUrl(urlName, params)
    if url is None:
        callback(achievementId, None)
        return
    else:
        import Account
        fileCache = Account.g_accountRepository.customFilesCache
        fileCache.get(url, functools.partial(__fileLoadedCallback, achievementId=achievementId, dataCallback=callback), True)
        return


def getRareAchievementImageUrl(urlName, achievementId):
    return __buildRareImageUrl(urlName, (achievementId,))


def __fileLoadedCallback(url, data, achievementId, dataCallback):
    dataCallback(achievementId, data)


def __getAchievementDescription(dataSection):
    result = {}
    for key, value in dataSection.items():
        result[key] = value.asString

    return result


def __allMedalsTextLoadedCallback(achievementId, data, onTextLoadedCallback):
    description = {}
    achievementIdStr = str(achievementId)
    if data is not None:
        try:
            dataSection = ResMgr.DataSection()
            dataSection.createSectionFromString(data)
            achievementsSection = dataSection['root/medals']
            for item in achievementsSection.values():
                if item.readString('id') == achievementIdStr:
                    description = __getAchievementDescription(item)
                    break

        except Exception:
            LOG_CURRENT_EXCEPTION()
            description = {}

    onTextLoadedCallback(achievementId, description)
    return


def getRareAchievementImage(achievementId, onImageLoadedCallback):
    __makeAchievementFileRequest('rare_achievements_images', (achievementId,), achievementId, onImageLoadedCallback)


def getRareAchievementImageBig(achievementId, onImageLoadedCallback):
    __makeAchievementFileRequest('rare_achievements_images_big', (achievementId,), achievementId, onImageLoadedCallback)


def __buildRareImageUrl(urlName, params):
    import Account
    fileServerSettings = Account.g_accountRepository.fileServerSettings
    try:
        url = fileServerSettings[urlName]['url_template']
        return url % params
    except KeyError:
        LOG_ERROR('Failed to find fileServer setting: %s' % urlName)
    except TypeError:
        LOG_ERROR('Incorrect url format: %s' % url, params)
    except Exception:
        LOG_CURRENT_EXCEPTION()

    return


def getRareAchievementText(lang, achievementId, onTextLoadedCallback):
    cbk = functools.partial(__allMedalsTextLoadedCallback, onTextLoadedCallback=onTextLoadedCallback)
    __makeAchievementFileRequest('rare_achievements_texts', (lang,), achievementId, cbk)
