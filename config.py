
APP_NAME = 'ExDPowerSupply'
CONFIG_FILE_NAME = 'userConfig.ini'

position = 300,150
childFrameDisplacement = 40,60
positionInPercent = 0,0

expandSize = 660, 500
decreaseSize = 660, 160
portSettingsSize = 410, 300
grapgSettingsSize = 710, 300

chSize = (40, 20)

timeToAppear = 125

autoConnect = True
savePosition = True
alwaysOnTop = True

import wx
onTopTrue = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX) | wx.STAY_ON_TOP
onTopFalse = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)

onAxuliaryPageWithOnTopTrue = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.CLOSE_BOX) | wx.STAY_ON_TOP
onAxuliaryPageWithOnTopFalse = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.CLOSE_BOX)

childFrameStyle = wx.DEFAULT_FRAME_STYLE &~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX) | wx.FRAME_FLOAT_ON_PARENT

channelBorderColour = '#a9a9a9'
autoTuneColour = '#89CFF0'


import configparser
import os, sys
import win32api

monitors = win32api.EnumDisplayMonitors()

def creatingDefaultConfigFile():
    configParser = configparser.ConfigParser()
    configParser['SAVING_CONFIG'] = {'autoConnect': str(autoConnect),
                                     'savePosition': str(savePosition),
                                     'alwaysOnTop': str(alwaysOnTop)}
    configParser['POSITION'] = {'positionX': str(position[0]),
                                'positionY': str(position[1])}
    configParser['POSITION_IN_PERCENT'] = {'positionX': str(positionInPercent[0]),
                                           'positionY': str(positionInPercent[1])}
    pos = float(position[0]), float(position[1])
    style = onTopTrue
    with open(CONFIG_FILE_NAME, 'w') as configfile:
        configParser.write(configfile)
    return  pos, style

def GetConfigurations():
    if not os.path.exists(os.path.join(os.getcwd(), CONFIG_FILE_NAME)):
        pos, style = creatingDefaultConfigFile()
    else:
        configParser = configparser.ConfigParser()
        configParser.read(CONFIG_FILE_NAME)
        pos = getPosition(configParser)
        style = getStyle(configParser)
    return wx.Point(pos), wx.Size(expandSize), style

def getPosition(configParser):
    try:
        pos = float(configParser['POSITION']['positionX']), float(configParser['POSITION']['positionY'])
        if pos[0] > monitors[-1][2][2] or pos[1] > monitors[-1][2][3]:
            raise
    except:
        if type(KeyError()) == sys.exc_info()[0]:
            configParser['POSITION'] = {'positionX': str(position[0]),
                                        'positionY': str(position[1])}
            with open(CONFIG_FILE_NAME, 'w') as configfile:
                configParser.write(configfile)
        try:
            x_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionX'])
            y_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionY'])
            pos = monitors[0][2][2] / 100 * x_PercetPos, monitors[0][2][3] / 100 * y_PercetPos
        except KeyError:
            configParser['POSITION_IN_PERCENT'] = {'positionX': str(positionInPercent[0]),
                                                   'positionY': str(positionInPercent[1])}
            with open(CONFIG_FILE_NAME, 'w') as configfile:
                configParser.write(configfile)
        finally:
            x_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionX'])
            y_PercetPos = float(configParser['POSITION_IN_PERCENT']['positionY'])
            pos = monitors[0][2][2] / 100 * x_PercetPos, monitors[0][2][3] / 100 * y_PercetPos
            configParser['POSITION'] = {'positionX': str(pos[0]),
                                        'positionY': str(pos[1])}
            with open(CONFIG_FILE_NAME, 'w') as configfile:
                configParser.write(configfile)
    return pos

def getStyle(configParser):
    try:
        onTop = configParser['SAVING_CONFIG']['alwaysOnTop']
    except KeyError as key:
        if 'alwaysOnTop' in str(key):
            configParser.set('SAVING_CONFIG', 'alwaysOnTop', str(alwaysOnTop))
        else:
            configParser['SAVING_CONFIG'] = {'autoConnect': str(autoConnect),
                                             'savePosition': str(savePosition),
                                             'alwaysOnTop': str(alwaysOnTop)}
        with open(CONFIG_FILE_NAME, 'w') as configFile:
            configParser.write(configFile)
    finally:
        onTop = configParser['SAVING_CONFIG']['alwaysOnTop']
    if 'True' in onTop:
        style = onTopTrue
    else:
        style = onTopFalse
    return style

def GetSavingConfig():
    configParser = configparser.ConfigParser()
    configParser.read(CONFIG_FILE_NAME)
    success = False
    while not success:
        try:
            configAlwaysOnTop = getAlwaysOnTop(configParser)

            configAutoConnect = getAutoConnect(configParser)

            configSavePosition = getSavePosition(configParser)
            success = True
        except KeyError as key:
            if 'autoConnect' in str(key):
                configParser.set('SAVING_CONFIG', 'autoConnect', str(autoConnect))
                with open(CONFIG_FILE_NAME, 'w') as configFile:
                    configParser.write(configFile)
            elif 'savePosition' in str(key):
                configParser.set('SAVING_CONFIG', 'savePosition', str(savePosition))
                with open(CONFIG_FILE_NAME, 'w') as configFile:
                    configParser.write(configFile)

    return configAlwaysOnTop, configAutoConnect, configSavePosition

def getAlwaysOnTop(configParser):
    if 'True' in configParser['SAVING_CONFIG']['alwaysOnTop']:
        configAlwaysOnTop = True
    else:
        configAlwaysOnTop = False
    return configAlwaysOnTop

def getAutoConnect(configParser):
    if 'True' in configParser['SAVING_CONFIG']['autoConnect']:
        configAutoConnect = True
    else:
        configAutoConnect = False
    return configAutoConnect

def getSavePosition(configParser):
    if 'True' in configParser['SAVING_CONFIG']['savePosition']:
        configSavePosition = True
    else:
        configSavePosition = False
    return configSavePosition

def SavingUsersConfig(window):
    configParser = configparser.ConfigParser()
    configParser.read(CONFIG_FILE_NAME)
    configParser.set('SAVING_CONFIG', 'autoConnect', str(window.autoConnect))
    configParser.set('SAVING_CONFIG', 'savePosition', str(window.savePosition))
    configParser.set('SAVING_CONFIG', 'alwaysOnTop', str(window.alwaysOnTop))
    if window.savePosition:
        pos = window.GetPosition()
        for monitor in monitors:
            if (pos[0] >= monitor[2][0] and pos[0] < monitor[2][2]) and (pos[1] >= monitor[2][1] and pos[1] < monitor[2][3]):
                x_PercetPos = (pos[0] - monitor[2][0]) * 100 / (monitor[2][2] - monitor[2][0])
                y_PercetPos = (pos[1] - monitor[2][1]) * 100 / (monitor[2][3] - monitor[2][1])
                configParser.set('POSITION_IN_PERCENT', 'positionX', str(x_PercetPos))
                configParser.set('POSITION_IN_PERCENT', 'positionY', str(y_PercetPos))
        configParser.set('POSITION', 'positionX', str(pos[0]))
        configParser.set('POSITION', 'positionY', str(pos[1]))
    with open(CONFIG_FILE_NAME, 'w') as configFile:
        configParser.write(configFile)

def GetScreenCenter():
    x = monitors[0][2][2]
    y = monitors[0][2][3]
    return int(x/2), int(y/2)