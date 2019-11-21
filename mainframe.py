import wx
import os, sys
import wx.lib.buttons as buttons
import wx.lib.scrolledpanel as scrolled
import webbrowser
import json
import textwrap
from portsettings import PortSettings
from model.model import Model, zipfolder
from model.profile import saveToFile, loadFromFile
import config
from progress import ProgressScreen

ID_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 8]
NAMES_CHANNELS = ['L1', 'L2', 'M3', 'FH', 'FB', 'M6', 'L7', 'L8', 'Filament']

ID_FILAMENT = 8
ID_VOLTAGE = 9
ID_EMISSION = 10
# CHANNEL_ID + START_ACT_CHANNELS_ID = ACT_CHANNEL_ID
START_ACT_CHANNELS_ID = 11

# CHANNEL_ID + START_CHANNELS_INDICATORS_ID = CHANNEL_INDICATOR_ID
START_CHANNELS_INDICATORS_ID = 100

# CHANNEL_ID + START_CHANNEL_AUXILIARY_INDICATORS_ID = CHANNEL_AUXILIARY_INDICATORS_ID
START_CHANNELS_AUXILIARY_INDICATORS_ID = 200

START_MODES_ID = 30
ID_MODE_ECD = 30
ID_MODE_EXD = 31
ID_MODE_POS_TRANS = 32
ID_MODE_NEG_TRANS = 33
ID_MODE_STANDBY = 34
ID_MODE_OFF = 35

ID_SAVE_POSITION = 39
ID_MENU_BUTTON_ALWAYS_ON_TOP = 40
ID_MENU_BUTTON_AUTO_CONNECT = 41
ID_MENU_PORT_SETTINGS = 42
ID_MENU_C_DC_BUTTON = 43
ID_MENU_BUTTON_DIAGNOSTICS = 44
ID_EXPAND_HIDE_BUTTON = 45
ID_RESTORE_PRESETS_BUTTON = 46

START_HELP_TOPIC_ID = 1000
START_DIAGNOSTICS_TOPIC_ID = 3000

MODES_DICTIONARY_NAME = {ID_MODE_ECD: 'ECD', ID_MODE_EXD: 'ExD', ID_MODE_POS_TRANS: 'Pos. Trans',
                   ID_MODE_NEG_TRANS: 'Neg. Trans', ID_MODE_STANDBY: 'Standby', ID_MODE_OFF: 'Off'}
MODES_DICTIONARY_ID = {'ECD': ID_MODE_ECD, 'ExD': ID_MODE_EXD, 'Pos. Trans': ID_MODE_POS_TRANS,
                       'Neg. Trans': ID_MODE_NEG_TRANS, 'Standby':  ID_MODE_STANDBY, 'Off': ID_MODE_OFF}

STATUS_DICTIONARY_NAME = {ID_FILAMENT: 'Filament', ID_VOLTAGE: '  Power', ID_EMISSION: 'Emission'}
STATUS_DICTIONARY_ID = {'Filament': ID_FILAMENT, '  Power': ID_VOLTAGE, 'Emission': ID_EMISSION}

class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        x_screen_center, y_screen__center = config.GetScreenCenter()
        self.die = ProgressScreen(None, title='Process', size = wx.Size(400,320), pos = wx.Point(x_screen_center - 200, y_screen__center - 160),style = wx.STAY_ON_TOP)
        self.die.Show()
        pub.subscribe(self.appear, "show")
        super(MainFrame, self).__init__(*args, **kw)
        sendUpdate()
        icon = wx.Icon('bitmaps/app.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.emblem = wx.Bitmap((wx.Bitmap('bitmaps/emblem.png').ConvertToImage()).Scale(90, 73, wx.IMAGE_QUALITY_HIGH))

        self.alwaysOnTop, self.autoConnect, self.savePosition = config.GetSavingConfig()

        self.multiPanel = wx.Panel(self)
        self.multisizer = wx.BoxSizer(wx.VERTICAL)
        sendUpdate()
        self.model = Model(self.OnError, self.OnConnect, self.OnCantReconnect)
        self.isConnectedToMIPS = False
        self.helpTopicsList = []
        self.helpMaterialsList = []
        self.diagnosticsTopicsList = []
        self.diagnosticsMaterialsList = []
        self.chCtrlPanelList = []
        self.currentPage = ''
        self.currentHelpTopic_ID = START_HELP_TOPIC_ID
        self.currentDiagnosticsTopic_ID = START_DIAGNOSTICS_TOPIC_ID
        self.currentModeID = ID_MODE_ECD
        self.currentChannel = ID_CHANNELS[0]
        self.isExpanded = False
        self.searchedString = ''
        self.windowPanel = wx.Panel(self.multiPanel)
        self.windowField = wx.BoxSizer(wx.VERTICAL)
        sendUpdate()
        # Mode -- Head Sizer
        self.modesSizer = wx.BoxSizer(wx.HORIZONTAL)
        for item in range(len(MODES_DICTIONARY_ID)):
            modeBox = wx.BoxSizer(wx.VERTICAL)
            modeIndicatorButton = wx.BitmapButton(self.windowPanel, id=MODES_DICTIONARY_ID[MODES_DICTIONARY_NAME[item+START_MODES_ID]], bitmap=wx.Bitmap("bitmaps/grey_24.png", wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
            modeIndicatorButton.Bind(wx.EVT_BUTTON, self.onIndicatorButton,id=MODES_DICTIONARY_ID[MODES_DICTIONARY_NAME[item+START_MODES_ID]])
            modeName = wx.StaticText(self.windowPanel, label=MODES_DICTIONARY_NAME[item+START_MODES_ID], size=(60, 18), style=wx.TE_CENTER)
            modeBox.Add(modeIndicatorButton, 0 , wx.ALIGN_CENTER_HORIZONTAL)
            modeBox.AddSpacer(4)
            modeBox.Add(modeName, 0, wx.ALIGN_CENTER_HORIZONTAL)
            modeBox.AddSpacer(6)
            self.modesSizer.Add(modeBox, 1, wx.EXPAND | wx.ALL | wx.ALIGN_TOP)

        # Window Main -- Working Field -- Sizer
        self.mainPanel = scrolled.ScrolledPanel(self.windowPanel, -1, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.mainPanel.SetAutoLayout(1)
        self.mainPanel.SetupScrolling()
        self.windowMainSizer = wx.BoxSizer(wx.VERTICAL)
        sendUpdate()
        # Main Body Head
        self.mainSizerHead  = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizerHeadLeft = wx.BoxSizer(wx.HORIZONTAL)
        self.tuneStaticText = wx.StaticText(self.mainPanel, label='Tune File Name: ', style=wx.TE_CENTER)
        self.tuneStaticText.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.tuneFileField = wx.StaticText(self.mainPanel, label='Untitled', style=wx.TE_CENTER)
        self.tuneFileField.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.mainSizerHeadRight = wx.BoxSizer(wx.HORIZONTAL)
        self.autoTuneButton = wx.Button(self.mainPanel, label='Auto Tune', size=(70,20), style=wx.NO_BORDER)
        self.autoTuneButton.Bind(wx.EVT_BUTTON, self.onAutoTune)
        self.mainSizerHeadLeft.AddSpacer(10)
        self.mainSizerHeadLeft.Add(self.tuneStaticText)
        self.mainSizerHeadLeft.Add(self.tuneFileField)
        self.mainSizerHeadRight.Add(self.autoTuneButton)
        self.mainSizerHead.Add(self.mainSizerHeadLeft,5, wx.EXPAND)
        self.mainSizerHead.Add(self.mainSizerHeadRight,1,wx.EXPAND)
        sendUpdate()
        # Body
        self.mainSizerBody = wx.BoxSizer(wx.HORIZONTAL)
        self.mainSizerBodyLeft = wx.GridBagSizer()
        self.mainSizerBodyRight = wx.BoxSizer(wx.VERTICAL)

        # Main Body Left
        self.statusFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        for item in range(len(STATUS_DICTIONARY_ID)):
            if item == 0:
                statusFilamentSizer = wx.BoxSizer(wx.VERTICAL)
                self.statusCtrlPanel = wx.Panel(self.mainPanel, size=(58, 25))
                statusCtrlSizer = wx.BoxSizer()
                self.statusCtrlPanel.SetSizer(statusCtrlSizer)
                statusCtrlField = wx.TextCtrl(self.statusCtrlPanel, id=ID_CHANNELS[8], size = (55,22), style=wx.TE_CENTRE | wx.BORDER_STATIC)
                statusCtrlField.SetHint('0.0')
                statusCtrlField.Bind(wx.EVT_SET_CURSOR, self.channelOnFocus)
                statusCtrlField.Bind(wx.EVT_TEXT, self.channelValueChanged)
                statusActPanel = wx.Panel(self.mainPanel)
                statusActSizer = wx.BoxSizer(wx.VERTICAL)
                statusActPanel.SetSizer(statusActSizer)
                statusActField = wx.TextCtrl(statusActPanel, id=ID_CHANNELS[8] + START_ACT_CHANNELS_ID,
                                             size=(55, 22), style=wx.TE_CENTRE |wx.BORDER_DEFAULT)
                statusActSizer.AddSpacer(2)
                statusActSizer.Add(statusActField)
                statusActField.Disable()
                statusActField.SetFont(self.statusFont)
                statusStaticField = wx.StaticText(self.mainPanel, label=STATUS_DICTIONARY_NAME[item + ID_FILAMENT])
                statusStaticField.SetFont(self.statusFont)
                filamentCurrentSizer = wx.BoxSizer(wx.VERTICAL)
                filamentCurrent = wx.StaticText(self.mainPanel,label=' (A)')
                filamentCurrentSizer.AddSpacer(6)
                filamentCurrentSizer.Add(filamentCurrent)
                channelIndicator = buttons.GenButton(self.mainPanel, id=ID_CHANNELS[8] + START_CHANNELS_INDICATORS_ID,
                                                     size=(0, 3), style=wx.BORDER_NONE)
                channelAuxiliaryIndicator = buttons.GenButton(self.mainPanel,
                                                              id=ID_CHANNELS[8] + START_CHANNELS_AUXILIARY_INDICATORS_ID,
                                                              size=(0, 3),
                                                              style=wx.BORDER_NONE)
                statusFilamentSizer.Add(channelIndicator)
                statusFilamentSizer.Add(self.statusCtrlPanel)
                statusFilamentSizer.Add(channelAuxiliaryIndicator)
                statusFilamentSizer.Hide(channelAuxiliaryIndicator, recursive=True)
                self.mainSizerBodyLeft.Add(statusFilamentSizer, (0,0))
                self.mainSizerBodyLeft.Add(filamentCurrentSizer, (0,1))
                self.mainSizerBodyLeft.Add(statusActPanel, (item * 3 + 1, 0))
                self.mainSizerBodyLeft.Add(statusStaticField, (item * 3 + 2, 0))
            else:
                statusActField = wx.TextCtrl(self.mainPanel, id=STATUS_DICTIONARY_ID[STATUS_DICTIONARY_NAME[item+ID_FILAMENT]], size=(55,22), style=wx.TE_CENTRE | wx.BORDER_DEFAULT, name=STATUS_DICTIONARY_NAME[item + ID_FILAMENT])
                statusActField.Disable()
                statusActField.SetFont(self.statusFont)
                statusStaticField = wx.StaticText(self.mainPanel, label=STATUS_DICTIONARY_NAME[item+ID_FILAMENT])
                statusStaticField.SetFont(self.statusFont)
                if item == 1:
                    label = ' (V)'
                else:
                    label = ' (\u00B5A)'
                static = wx.StaticText(self.mainPanel, label=label)
                self.mainSizerBodyLeft.Add(statusActField, (item*3+1, 0))
                self.mainSizerBodyLeft.Add(static, (item*3+1, 1))
                self.mainSizerBodyLeft.Add(statusStaticField, (item*3+2,0))
        sendUpdate()
        # Main Body Right
        self.imageField = wx.StaticBitmap(self.mainPanel)
        self.image = wx.Bitmap(wx.Bitmap('bitmaps/image.png').ConvertToImage().Scale(490,126,wx.IMAGE_QUALITY_HIGH))
        self.imageField.SetBitmap(self.image)
        self.channelsBox = wx.BoxSizer(wx.HORIZONTAL)
        self.channelsBox.AddSpacer(22)

        for item in range(len(ID_CHANNELS)-1):
            channelBox = wx.BoxSizer(wx.VERTICAL)
            channelIndicator = buttons.GenButton(self.mainPanel,id=ID_CHANNELS[item]+START_CHANNELS_INDICATORS_ID, size=(0,3), style=wx.BORDER_NONE, name='Shown')
            channelAuxiliaryIndicator = buttons.GenButton(self.mainPanel, id=ID_CHANNELS[item] + START_CHANNELS_AUXILIARY_INDICATORS_ID, size=(0, 3),
                                                 style=wx.BORDER_NONE, name='Shown')

            # Rising Field
            chCtrlPanel = wx.Panel(self.mainPanel,size=(43,23))
            self.chCtrlPanelList.append(chCtrlPanel)
            chCtrlSizer = wx.BoxSizer()
            chCtrlPanel.SetSizer(chCtrlSizer)
            chCtrl = wx.TextCtrl(chCtrlPanel, id=ID_CHANNELS[item], size=config.chSize, style=wx.BORDER_STATIC | wx.TE_LEFT, name=NAMES_CHANNELS[item])
            chCtrlSizer.Add(chCtrl)

            # # Squeezing Field
            # chCtrlPanel = wx.Panel(self.mainPanel, size=(42, 22))
            # self.chCtrlPanelList.append(chCtrlPanel)
            # chCtrlSizer = wx.BoxSizer(wx.VERTICAL)
            # chCtrlPanel.SetSizer(chCtrlSizer)
            # chCtrl = wx.TextCtrl(chCtrlPanel, id=ID_CHANNELS[item], size=config.chSize, style=wx.TE_LEFT | wx.BORDER_SIMPLE,
            #                      name=NAMES_CHANNELS[item])
            # chCtrlSizer.AddSpacer(2)
            # chCtrlSizer.Add(chCtrl, wx.ALIGN_BOTTOM)

            chCtrl.SetHint('0.0')
            chCtrl.Bind(wx.EVT_SET_CURSOR, self.channelOnFocus)
            chCtrl.Bind(wx.EVT_TEXT, self.channelValueChanged)
            chActCtrl = wx.TextCtrl(self.mainPanel, id=ID_CHANNELS[item]+START_ACT_CHANNELS_ID, size=config.chSize, style= wx.BORDER_DEFAULT |wx.TE_READONLY | wx.TE_LEFT , name=NAMES_CHANNELS[item])
            chActCtrl.Disable()
            chActCtrl.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            channelBox.Add(channelIndicator,1,wx.ALIGN_CENTER_HORIZONTAL)

            channelBox.Add(chCtrlPanel)
            channelBox.Add(channelAuxiliaryIndicator,1,wx.ALIGN_CENTER_HORIZONTAL)
            channelBox.AddSpacer(5)
            channelBox.Add(chActCtrl)
            self.channelsBox.Add(channelBox)
            self.channelsBox.AddSpacer(12)
            # Rising field
            channelBox.Hide(channelAuxiliaryIndicator, recursive=True)
            # # Squeezing field
            # channelBox.Hide(channelIndicator, recursive=True)
        sendUpdate()
        self.chCtrlPanelList.append(self.statusCtrlPanel)
        self.mainSizerBodyRight.AddSpacer(13)
        self.mainSizerBodyRight.Add(self.imageField)
        self.mainSizerBodyRight.AddSpacer(20)
        self.mainSizerBodyRight.Add(self.channelsBox,0 ,wx.ALIGN_CENTER_HORIZONTAL)

        # Main Body Bottom
        self.mainSizerBottom = wx.BoxSizer(wx.HORIZONTAL)
        slyderStaticText = wx.StaticText(self.mainPanel, label='Voltage\nScalable\nAdjustment', style=wx.TE_CENTRE)
        slyderStaticText.SetFont(self.statusFont)
        slyderVBox = wx.BoxSizer(wx.VERTICAL)
        slyderBox = wx.BoxSizer(wx.HORIZONTAL)
        auxiliaryZeroSpacer =  buttons.GenButton(self.mainPanel,id=12344, size=(0,16), style=wx.BORDER_NONE)
        slyderVBox.Add(slyderBox)
        zeroValueText = wx.StaticText(self.mainPanel, id = 12345, label='0')
        zeroValueBox = wx.BoxSizer()
        zeroValueBox.AddSpacer(254)
        zeroValueBox.Add(zeroValueText)
        slyderVBox.Add(auxiliaryZeroSpacer)
        auxiliaryZeroSpacer.Hide()
        slyderVBox.Add(zeroValueBox)
        self.minText = wx.StaticText(self.mainPanel, label="-60", style=wx.TE_RIGHT)
        self.minText.SetMinSize((20,20))
        self.slyder = wx.Slider(self.mainPanel, value=0, minValue=-60, maxValue=60, size=wx.Size(453, 20),
                                style=wx.SL_SELRANGE | wx.SL_TICKS)
        self.slyder.Bind(wx.EVT_SLIDER, self.onSliderScroll)
        self.maxText = wx.StaticText(self.mainPanel, label="60 V")
        sendUpdate()
        slyderBox.Add(self.minText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        slyderBox.Add(self.slyder, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        slyderBox.Add(self.maxText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.mainSizerBottom.AddSpacer(20)
        self.mainSizerBottom.Add(slyderStaticText)
        self.mainSizerBottom.AddSpacer(33)
        self.mainSizerBottom.Add(slyderVBox, 0, wx.ALIGN_CENTER_VERTICAL)

        self.mainSizerBody.AddSpacer(25)
        self.mainSizerBody.Add(self.mainSizerBodyLeft)
        self.mainSizerBody.AddSpacer(25)
        self.mainSizerBody.Add(self.mainSizerBodyRight)
        sendUpdate()
        # Bottom Sizer
        self.bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.bottomAuxiliaryButton = buttons.GenButton(self.windowPanel, size=(70,40),style=wx.BORDER_NONE)
        # self.bottomAuxiliaryButton.Disable()
        self.expand_hide_button = buttons.GenBitmapTextButton(self.windowPanel, id=ID_EXPAND_HIDE_BUTTON, bitmap=wx.Bitmap('bitmaps\expand.png'),style=wx.BORDER_NONE, size=(60,40), name='Show')
        self.expand_hide_button.Bind(wx.EVT_BUTTON, self.onShowHideButton, id=ID_EXPAND_HIDE_BUTTON)
        self.restorePresetsButton = wx.Button(self.windowPanel, label='Restore \nPresets', size=(70, 36))
        self.restorePresetsButton.Bind(wx.EVT_BUTTON, self.onRestorePresetsButton, id=ID_RESTORE_PRESETS_BUTTON)

        #
        self.errorIndicatorSizer = wx.BoxSizer(wx.HORIZONTAL)
        indicator = wx.Bitmap((wx.Bitmap('bitmaps/green_2.png').ConvertToImage()))
        self.errorIndicator = wx.StaticBitmap(self.multiPanel)
        self.errorIndicator.SetBitmap(indicator)
        self.errorIndicatorText = wx.StaticText(self.multiPanel, size=(40,20), label='Error: 0')
        self.errorIndicatorSizer.AddSpacer(5)
        self.errorIndicatorSizer.Add(self.errorIndicator)
        self.errorIndicatorSizer.AddSpacer(5)
        self.errorIndicatorSizer.Add(self.errorIndicatorText)
        sendUpdate()
        # Filling windowPanel
        self.windowField.AddSpacer(10)
        self.windowField.Add(self.modesSizer,0, wx.EXPAND)
        self.windowField.Add(self.mainPanel, 1, wx.EXPAND)
        self.windowField.Add(self.bottomSizer, 0, wx.EXPAND | wx.ALL | wx.BOTTOM)

        self.windowMainSizer.AddSpacer(12)
        self.windowMainSizer.Add(self.mainSizerHead,1, wx.EXPAND)
        self.windowMainSizer.Add(self.mainSizerBody)
        self.windowMainSizer.AddSpacer(10)
        self.windowMainSizer.Add(self.mainSizerBottom)
        self.windowMainSizer.AddSpacer(4)
        self.bottomSizer.Add(self.errorIndicatorSizer,0,wx.ALIGN_CENTER)
        # self.bottomSizer.Add(self.bottomAuxiliaryButton)
        self.bottomSizer.Add(self.expand_hide_button,1 , wx.ALIGN_CENTER)
        self.bottomSizer.Add(self.restorePresetsButton,0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        self.windowPanel.SetSizer(self.windowField)
        self.windowPanel.Hide()
        self.mainPanel.SetSizer(self.windowMainSizer)
        sendUpdate()
        # Help Panel
        self.helpPanel = wx.Panel(self.multiPanel)
        self.helpPanelSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Help Panel Navigation Sizer
        self.helpNavigationPanel = wx.Panel(self.helpPanel)
        self.helpNavigationSizer = wx.BoxSizer(wx.VERTICAL)
        self.helpTopicTitelTextSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.helpTopicTitelText = wx.StaticText(self.helpNavigationPanel, label=' Help Topics')
        self.helpTopicTitelText.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.helpTopicTitelTextSizer.AddSpacer(16)
        self.helpTopicTitelTextSizer.Add(self.helpTopicTitelText)
        self.helpTopicsPanel = scrolled.ScrolledPanel(self.helpNavigationPanel, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.helpTopicsPanel.SetAutoLayout(1)
        self.helpTopicsPanel.SetupScrolling(scroll_x=False)
        self.helpTopicsPanel.Bind(wx.EVT_MOTION, self.onPanel)
        self.helpTopicsSizer = wx.BoxSizer(wx.VERTICAL)
        self.helpNavigationSizer.AddSpacer(16)
        self.helpNavigationSizer.Add(self.helpTopicTitelTextSizer)
        self.helpNavigationSizer.AddSpacer(16)
        self.helpNavigationSizer.Add(self.helpTopicsPanel,1, wx.EXPAND)
        self.helpNavigationSizer.AddSpacer(10)
        self.helpTopicsPanel.SetSizer(self.helpTopicsSizer)
        self.helpNavigationPanel.SetSizer(self.helpNavigationSizer)
        sendUpdate()
        # Help Panel Material Sizer
        self.helpMaterialPanel = wx.Panel(self.helpPanel)
        self.helpMaterialPanel.SetBackgroundColour(wx.WHITE)
        self.helpMaterialSizer = wx.BoxSizer(wx.VERTICAL)
        self.helpMaterialHoriSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Head
        self.helpMaterialHeadSizer = wx.BoxSizer(wx.HORIZONTAL)
        # ,style=wx.TE_READONLY | wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_NO_VSCROLL
        self.helpSubjectTitelText = wx.StaticText(self.helpMaterialPanel)
        self.helpSubjectTitelText.SetMinSize((380,35))
        self.helpSubjectTitelText.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.helpSearchField = wx.TextCtrl(self.helpMaterialPanel, style=wx.TE_LEFT | wx.TE_PROCESS_ENTER)
        self.helpSearchField.SetHint('Search')
        self.helpSearchField.SetMaxSize((95, 22))
        self.helpSearchField.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        self.helpMaterialHeadSizer.AddSpacer(3)
        self.helpMaterialHeadSizer.Add(self.helpSubjectTitelText)
        # self.helpMaterialHeadSizer.AddSpacer(224)
        self.helpMaterialHeadSizer.Add(self.helpSearchField)
        self.helpMaterialHeadSizer.AddSpacer(8)

        # Body
        self.helpMaterialBodySizer = wx.BoxSizer(wx.HORIZONTAL)
        self.helpMaterialScrolledPanel = scrolled.ScrolledPanel(self.helpMaterialPanel, -1,
                                                                       style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.helpMaterialScrolledPanel.SetAutoLayout(1)
        self.helpMaterialScrolledPanel.SetupScrolling()
        self.helpMaterialScrolledPanel.Bind(wx.EVT_MOTION, self.onPanel)
        self.helpMaterialScrolledSizer = wx.BoxSizer(wx.VERTICAL)

        self.helpMaterialScrolledPanel.SetSizer(self.helpMaterialScrolledSizer)

        self.helpEmblemSizer = wx.BoxSizer(wx.VERTICAL)
        self.helpEmblem = wx.StaticBitmap(self.helpMaterialPanel)
        self.helpEmblem.SetBitmap(self.emblem)
        self.helpEmblemSizer.Add(self.helpEmblem)
        sendUpdate()
        self.helpMaterialBodySizer.Add(self.helpMaterialScrolledPanel, 1, wx.EXPAND)
        self.helpMaterialBodySizer.AddSpacer(10)
        self.helpMaterialBodySizer.Add(self.helpEmblemSizer)
        self.helpMaterialBodySizer.AddSpacer(10)

        # Bottom
        self.helpMaterialBottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.helpMoreHelpButton = wx.Button(self.helpMaterialPanel, label='Need more help?')
        self.helpMoreHelpButton.SetMaxSize((120,25))
        self.helpMoreHelpButton.Bind(wx.EVT_BUTTON, self.onMoreHelp)
        self.helpDoneButton = wx.Button(self.helpMaterialPanel, label='Done')
        self.helpDoneButton.SetMaxSize((80,25))
        self.helpDoneButton.SetBackgroundColour('#FFFFF0')
        self.helpDoneButton.Bind(wx.EVT_BUTTON, self.onDone)
        self.helpMaterialBottomSizer.AddSpacer(265)
        self.helpMaterialBottomSizer.Add(self.helpMoreHelpButton)
        self.helpMaterialBottomSizer.AddSpacer(20)
        self.helpMaterialBottomSizer.Add(self.helpDoneButton)
        self.helpMaterialBottomSizer.AddSpacer(5)
        sendUpdate()
        self.helpMaterialSizer.AddSpacer(10)
        self.helpMaterialSizer.Add(self.helpMaterialHeadSizer)
        self.helpMaterialSizer.AddSpacer(7)
        self.helpMaterialSizer.Add(self.helpMaterialBodySizer,1, wx.EXPAND)
        self.helpMaterialSizer.AddSpacer(10)
        self.helpMaterialSizer.Add(self.helpMaterialBottomSizer)
        self.helpMaterialSizer.AddSpacer(10)
        self.helpMaterialHoriSizer.AddSpacer(3)
        self.helpMaterialHoriSizer.Add(self.helpMaterialSizer,1, wx.EXPAND)
        self.helpMaterialPanel.SetSizer(self.helpMaterialHoriSizer)

        self.helpPanelSizer.AddSpacer(10)
        self.helpPanelSizer.Add(self.helpNavigationPanel,1, wx.EXPAND)
        self.helpPanelSizer.AddSpacer(3)
        self.helpPanelSizer.Add(self.helpMaterialPanel,6,wx.EXPAND)
        self.helpPanel.SetSizer(self.helpPanelSizer)
        self.helpPanel.Hide()

        # Diagnostics Panel
        self.diagnosticsPanel = wx.Panel(self.multiPanel)
        self.diagnosticsPanelSizer = wx.BoxSizer(wx.HORIZONTAL)
        sendUpdate()
        # Diagnostics Panel Navigation Sizer
        self.diagnosticsNavigationPanel = wx.Panel(self.diagnosticsPanel)
        self.diagnosticsNavigationSizer = wx.BoxSizer(wx.VERTICAL)
        self.diagnosticsTopicTitelTextSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.diagnosticsTopicTitelText = wx.StaticText(self.diagnosticsNavigationPanel, label='Error Found')
        self.diagnosticsTopicTitelText.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.diagnosticsTopicTitelTextSizer.AddSpacer(16)
        self.diagnosticsTopicTitelTextSizer.Add(self.diagnosticsTopicTitelText)
        self.diagnosticsTopicsPanel = scrolled.ScrolledPanel(self.diagnosticsNavigationPanel, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.diagnosticsTopicsPanel.SetAutoLayout(1)
        self.diagnosticsTopicsPanel.SetupScrolling(scroll_x=False)
        self.diagnosticsTopicsPanel.Bind(wx.EVT_MOTION, self.onPanel)
        self.diagnosticsTopicsSizer = wx.BoxSizer(wx.VERTICAL)

        self.diagnosticsNavigationSizer.AddSpacer(16)
        self.diagnosticsNavigationSizer.Add(self.diagnosticsTopicTitelTextSizer)
        self.diagnosticsNavigationSizer.AddSpacer(16)
        self.diagnosticsNavigationSizer.Add(self.diagnosticsTopicsPanel, 1, wx.EXPAND)
        self.diagnosticsNavigationSizer.AddSpacer(10)
        self.diagnosticsTopicsPanel.SetSizer(self.diagnosticsTopicsSizer)
        self.diagnosticsNavigationPanel.SetSizer(self.diagnosticsNavigationSizer)
        sendUpdate()
        # Diagnostics Panel Material Sizer
        self.diagnosticsMaterialPanel = wx.Panel(self.diagnosticsPanel)
        self.diagnosticsMaterialPanel.SetBackgroundColour(wx.WHITE)
        self.diagnosticsMaterialSizer = wx.BoxSizer(wx.VERTICAL)
        self.diagnosticsMaterialHoriSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Head
        self.diagnosticsMaterialHeadSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.diagnosticsSubjectTitelText = wx.StaticText(self.diagnosticsMaterialPanel)
        self.diagnosticsSubjectTitelText.SetMinSize((380, 35))
        self.diagnosticsSubjectTitelText.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.diagnosticsSearchField = wx.TextCtrl(self.diagnosticsMaterialPanel, style=wx.TE_LEFT | wx.TE_PROCESS_ENTER)
        self.diagnosticsSearchField.SetHint('Search')
        self.diagnosticsSearchField.SetMaxSize((95,22))
        self.diagnosticsSearchField.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        self.diagnosticsMaterialHeadSizer.AddSpacer(3)
        self.diagnosticsMaterialHeadSizer.Add(self.diagnosticsSubjectTitelText)
        self.diagnosticsMaterialHeadSizer.Add(self.diagnosticsSearchField)
        self.diagnosticsMaterialHeadSizer.AddSpacer(8)
        sendUpdate()
        # Body
        self.diagnosticsMaterialBodySizer = wx.BoxSizer(wx.HORIZONTAL)
        self.diagnosticsMaterialScrolledPanel = scrolled.ScrolledPanel(self.diagnosticsMaterialPanel, -1, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)
        self.diagnosticsMaterialScrolledPanel.SetAutoLayout(1)
        self.diagnosticsMaterialScrolledPanel.SetupScrolling(scroll_x=False)
        self.diagnosticsMaterialScrolledPanel.Bind(wx.EVT_MOTION, self.onPanel)
        self.diagnosticsMaterialScrolledSizer = wx.BoxSizer(wx.VERTICAL)

        self.diagnosticsMaterialScrolledPanel.SetSizer(self.diagnosticsMaterialScrolledSizer)

        self.diagnosticsEmblemSizer = wx.BoxSizer(wx.VERTICAL)
        self.diagnosticsEmblem = wx.StaticBitmap(self.diagnosticsMaterialPanel)

        self.diagnosticsEmblem.SetBitmap(self.emblem)
        self.diagnosticsEmblemSizer.Add(self.diagnosticsEmblem)


        self.diagnosticsMaterialBodySizer.Add(self.diagnosticsMaterialScrolledPanel, 1, wx.EXPAND)
        self.diagnosticsMaterialBodySizer.AddSpacer(10)
        self.diagnosticsMaterialBodySizer.Add(self.diagnosticsEmblemSizer)
        self.diagnosticsMaterialBodySizer.AddSpacer(10)
        sendUpdate()
        # Bottom
        self.diagnosticsMaterialBottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.diagnosticsMoreHelpButton = wx.Button(self.diagnosticsMaterialPanel, label='Need more help?')
        self.diagnosticsMoreHelpButton.SetMaxSize((120,25))
        self.diagnosticsMoreHelpButton.Bind(wx.EVT_BUTTON, self.onMoreHelp)
        self.diagnosticsDoneButton = wx.Button(self.diagnosticsMaterialPanel,label='Done')
        self.diagnosticsDoneButton.SetBackgroundColour('#FFFFF0')
        self.diagnosticsDoneButton.SetMaxSize((80,25))
        self.diagnosticsDoneButton.Bind(wx.EVT_BUTTON, self.onDone)
        self.diagnosticsMaterialBottomSizer.AddSpacer(265)
        self.diagnosticsMaterialBottomSizer.Add(self.diagnosticsMoreHelpButton)
        self.diagnosticsMaterialBottomSizer.AddSpacer(20)
        self.diagnosticsMaterialBottomSizer.Add(self.diagnosticsDoneButton)
        self.diagnosticsMaterialBottomSizer.AddSpacer(5)

        self.diagnosticsMaterialSizer.AddSpacer(10)
        self.diagnosticsMaterialSizer.Add(self.diagnosticsMaterialHeadSizer)
        self.diagnosticsMaterialSizer.AddSpacer(7)
        self.diagnosticsMaterialSizer.Add(self.diagnosticsMaterialBodySizer, 1, wx.EXPAND)
        self.diagnosticsMaterialSizer.AddSpacer(10)
        self.diagnosticsMaterialSizer.Add(self.diagnosticsMaterialBottomSizer)
        self.diagnosticsMaterialSizer.AddSpacer(10)
        self.diagnosticsMaterialHoriSizer.AddSpacer(3)
        self.diagnosticsMaterialHoriSizer.Add(self.diagnosticsMaterialSizer, 1, wx.EXPAND)
        self.diagnosticsMaterialPanel.SetSizer(self.diagnosticsMaterialHoriSizer)

        self.diagnosticsPanelSizer.AddSpacer(10)
        self.diagnosticsPanelSizer.Add(self.diagnosticsNavigationPanel, 1, wx.EXPAND)
        self.diagnosticsPanelSizer.AddSpacer(3)
        self.diagnosticsPanelSizer.Add(self.diagnosticsMaterialPanel, 6, wx.EXPAND)
        self.diagnosticsPanel.SetSizer(self.diagnosticsPanelSizer)
        self.diagnosticsPanel.Hide()
        sendUpdate()

        self.multisizer.Add(self.windowPanel,1, wx.EXPAND)
        self.multisizer.Add(self.helpPanel, 1, wx.EXPAND)
        self.multisizer.Add(self.diagnosticsPanel, 1, wx.EXPAND)
        self.multiPanel.SetSizer(self.multisizer)

        # Other Settings
        self.windowPanel.Show()

        self.makeMenuBar()
        self.FindWindowById(self.currentModeID).SetBitmap(bitmap=wx.Bitmap('bitmaps\green_24.png'))
        self.Bind(wx.EVT_CLOSE, self.onExit)
        self.hide()
        # size = wx.Size(config.decreaseSize)
        # self.windowField.Hide(self.mainPanel, recursive=True)
        # self.mainPanel.Hide()
        # self.restorePresetsButton.Hide()
        # self.bottomSizer.Hide(self.errorIndicatorSizer,recursive=True)
        # self.bottomAuxiliaryButton.Hide()

        self.model.connect()
        self.selectChannel(self.currentChannel)
        self.updateSetValues()
        # self.SetMaxSize(size)
        # self.SetMinSize(size)
        # self.SetSize(size)

        self.Bind(wx.EVT_MOVE, self.onMove)
        sendUpdate()
        # self.Show()

    def onMove(self, evt):
        pos = self.GetPosition()
        try:
            errorPopUp.moving(self.pop, pos, self.currentPage)
        except:
            return

    def onPanel(self,event):
        event.GetEventObject()

    def makeMenuBar(self):

        # File Menu
        self.fileMenu = wx.Menu()

        newProfile = wx.MenuItem(self.fileMenu, wx.ID_NEW, '&New Profile')
        newProfile.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_OTHER, (16,16)))
        openProfile = wx.MenuItem(self.fileMenu, wx.ID_OPEN, '&Open Profile')
        openProfile.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16,16)))
        saveProfile = wx.MenuItem(self.fileMenu, wx.ID_SAVE, '&Save Profile')
        saveProfile.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_OTHER, (16,16)))
        quit_button = wx.MenuItem(self.fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        quit_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_OTHER, (16,16)))

        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(newProfile)
        self.fileMenu.Append(openProfile)
        self.fileMenu.Append(saveProfile)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(quit_button)

        self.Bind(wx.EVT_MENU, self.onNewProfile, newProfile)
        self.Bind(wx.EVT_MENU, self.onOpenProfile, openProfile)
        self.Bind(wx.EVT_MENU, self.onSaveProfile, saveProfile)
        self.Bind(wx.EVT_MENU, self.onExit, quit_button)

        # Connect Menu
        self.connectMenu = wx.Menu()

        portSettings = wx.MenuItem(self.connectMenu, ID_MENU_PORT_SETTINGS, '&Port Settings')
        connectDisconnect = wx.MenuItem(self.connectMenu, ID_MENU_C_DC_BUTTON, '&Connect')

        self.connectMenu.AppendCheckItem(ID_MENU_BUTTON_AUTO_CONNECT, '&Auto connect')
        self.connectMenu.AppendSeparator()
        self.connectMenu.Append(portSettings)
        self.connectMenu.AppendSeparator()
        self.connectMenu.Append(connectDisconnect)

        self.Bind(wx.EVT_MENU, self.onAutoConnect, id=ID_MENU_BUTTON_AUTO_CONNECT)
        self.connectMenu.Check(ID_MENU_BUTTON_AUTO_CONNECT, self.autoConnect)
        self.Bind(wx.EVT_MENU, self.onPortSettings, portSettings)

        # Window Menu
        self.windowMenu = wx.Menu()

        self.windowMenu.AppendCheckItem(ID_MENU_BUTTON_ALWAYS_ON_TOP, '&Always on top')
        self.windowMenu.AppendSeparator()
        self.windowMenu.AppendCheckItem(ID_SAVE_POSITION, '&Save Position')

        self.windowMenu.Check(ID_MENU_BUTTON_ALWAYS_ON_TOP, self.alwaysOnTop)
        self.windowMenu.Check(ID_SAVE_POSITION, self.savePosition)

        self.Bind(wx.EVT_MENU, self.onAlwaysOnTop, id=ID_MENU_BUTTON_ALWAYS_ON_TOP)
        self.Bind(wx.EVT_MENU, self.onSavePosition, id=ID_SAVE_POSITION)

        # Help Menu
        self.helpMenu = wx.Menu()

        self.help = wx.MenuItem(self.helpMenu, wx.ID_HELP, '&Help')
        self.help.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_OTHER, (16,16)))
        self.diagnostics = wx.MenuItem(self.helpMenu, ID_MENU_BUTTON_DIAGNOSTICS, '&Diagnostics')
        self.diagnostics.SetBitmap((wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_OTHER, (16,16))))

        self.helpMenu.AppendSeparator()
        self.helpMenu.Append(self.help)
        self.helpMenu.Append(self.diagnostics)
        self.helpMenu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self.onHelp, self.help)
        self.Bind(wx.EVT_MENU, self.onDiagnostics, self.diagnostics)

        self.popUpMenu = wx.Menu()
        self.Bind(wx.EVT_MENU_OPEN, self.onPopUp)

        # Menu Bar
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.fileMenu, '&File')
        self.menuBar.Append(self.connectMenu, '&Connect')
        self.menuBar.Append(self.windowMenu, '&Window')
        self.menuBar.Append(self.helpMenu, '&Help')
        self.menuBar.Append(self.popUpMenu, '&Pop Up Window')

        self.SetMenuBar(self.menuBar)

    def onPopUp(self, event):
        if event.GetMenu() == self.popUpMenu:
            self.pop = errorPopUp(self, self.currentPage)

    def onExit(self, event):
        config.SavingUsersConfig(window=self)
        sys.exit()

    def onNewProfile(self, event):
        self.tuneFileField.SetLabel('Untitled')
        return

    def onOpenProfile(self, event):
        text='KAKSKAKSDKSDKSADKKSAD'
        self.expand()
        self.tuneFileField.SetLabel(text)

    def onSaveProfile(self, event):
        print('save')
        return

    def onAutoConnect(self, event):
        if self.connectMenu.IsChecked(event.GetId()) == True:
            print('Auto connecting')
            self.autoConnect = True
        else:
            print('Manual Connecting')
            self.autoConnect = False

    def connectWithParams(self, port, baudRate, parity, stopBits, flowControl):
        self.model.connectWithParams(port, baudRate, parity, stopBits, flowControl)

    def onPortSettings(self, event):
        frame = PortSettings(self)
        frame.setCB(self.connectWithParams)
        size = wx.Size(config.grapgSettingsSize)
        frame.Show()
        frame.SetSize(size)

    def onAlwaysOnTop(self, event):
        if self.windowMenu.IsChecked(event.GetId()):
            self.SetWindowStyle(config.onTopTrue)
            self.alwaysOnTop = True
        else:
            self.SetWindowStyle(config.onTopFalse)
            self.alwaysOnTop = False

    def onSavePosition(self, event):
        if self.windowMenu.IsChecked(ID_SAVE_POSITION) == True:
            self.savePosition = True
        else:
            self.savePosition = False

    def onHelp(self, event):
        self.EnableCloseButton(False)
        self.searchedString = ''
        size = wx.Size(config.expandSize)
        self.fillingHelpInstanse()
        self.currentPage = 'Help'

        pos = self.GetPosition()
        try:
            errorPopUp.moving(self.pop, pos, self.currentPage)
        except:
            print('blabla')
        self.helpMenu.Enable(wx.ID_HELP, False)
        self.helpMenu.Enable(ID_MENU_BUTTON_DIAGNOSTICS, True)
        if self.menuBar.GetLabelTop(1) == 'Connect':
            self.menuBar.Remove(1)
        self.helpTopicsPanel.SetMinSize((140,380))
        self.helpMaterialScrolledPanel.SetMaxSize((375,340))


        if self.currentPage == 'Diagnostics':
            self.clearingInstance()
            self.diagnosticsSearchField.SetValue('')
        if self.GetSize() == size:
            self.helpPanel.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_LEFT, timeout=config.timeToAppear)
            self.diagnosticsPanel.Hide()
            self.windowPanel.Hide()
            self.helpPanel.Fit()
        else:
            self.SetMaxSize(size)
            self.FindWindowById(ID_EXPAND_HIDE_BUTTON).Hide()
            for i in range(config.decreaseSize[1], config.expandSize[1]+20, 20):
                self.SetSize(wx.Size(config.expandSize[0], i))
            self.SetMinSize(size)
            self.helpPanel.Fit()
            self.helpPanel.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_LEFT, timeout=config.timeToAppear)
            self.diagnosticsPanel.Hide()
            self.windowPanel.Hide()
        self.helpPanel.Refresh()


    def fillingHelpInstanse(self, searchString = ''):
        with open('help_DB.json', 'r') as file:
            data = json.load(file)
        index = 0
        self.helpTopicsPanel.Layout()
        self.helpTopicsPanel.SetupScrolling(scroll_x=False)
        self.helpMaterialScrolledPanel.Layout()
        self.helpMaterialScrolledPanel.SetupScrolling(scroll_x=False)
        for item in data['help_topics']:
            if searchString not in item['help_topic']['topic_name'].lower():
                if searchString not in item['help_topic']['topic_material'].lower():
                    continue
            butSize = (123,15)
            helpTopicSizerPanel = wx.Panel(self.helpTopicsPanel)
            helpTopicSizerPanel.Hide()
            helpTopicSizer = wx.BoxSizer(wx.VERTICAL)
            helpTopicSizerPanel.SetSizer(helpTopicSizer)
            topic = ''
            for i in range(1):
                topic += item['help_topic']['topic_name']
                topic += ' '
            label, sizeCount = self.transformTopicToFitLabel(topic)
            topicS = wx.BoxSizer()
            topic = wx.StaticText(helpTopicSizerPanel, id=START_HELP_TOPIC_ID + index,
                                  size=(butSize[0], butSize[1] * (sizeCount)), label=label, style=wx.TE_CENTRE, name='Shown')
            topic.Bind(wx.EVT_LEFT_DOWN, self.onTopicButton)
            topicS.Add(topic)
            topicS.AddSpacer(15)
            helpTopicSizer.AddSpacer(3)
            helpTopicSizer.Add(topicS)
            helpTopicSizer.AddSpacer(3)
            self.helpTopicsList.append(helpTopicSizerPanel)
            self.helpTopicsSizer.Add(helpTopicSizerPanel)
            helpMaterialSizer = wx.BoxSizer()
            label = ''
            for i in range(100):
                label += item['help_topic']['topic_material']
                label += ' '
            label = self.transformMaterialToFitPanel(label)
            # size=(374,339),style=wx.TE_MULTILINE | wx.TE_READONLY
            text = wx.StaticText(self.helpMaterialScrolledPanel)
            text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            helpMaterialSizer.Add(text)
            self.helpMaterialsList.append(helpMaterialSizer)
            self.helpMaterialScrolledSizer.Add(helpMaterialSizer)
            self.helpMaterialScrolledSizer.Hide(helpMaterialSizer)
            # text.SetLabelText(label)
            text.SetLabelText(label)
            index += 1
        for i in self.helpTopicsList:
            i.Show()
        self.currentHelpTopic_ID = START_HELP_TOPIC_ID
        if len(self.helpTopicsList) == 0:
            self.helpSubjectTitelText.SetLabelText('No matches found')
            return
        self.FindWindowById(self.currentHelpTopic_ID).SetName('Selected')
        self.helpTopicsList[self.currentHelpTopic_ID-START_HELP_TOPIC_ID].SetBackgroundColour('#00BFFF')
        self.FindWindowById(self.currentHelpTopic_ID).SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.helpMaterialScrolledSizer.Show(self.helpMaterialsList[self.currentHelpTopic_ID - START_HELP_TOPIC_ID])
        self.helpSubjectTitelText.SetLabelText(self.transformTopicToFitHeader(self.FindWindowById(self.currentHelpTopic_ID).GetLabel()))
        self.helpPanel.Layout()

    def onDiagnostics(self, event):
        self.EnableCloseButton(False)
        self.searchedString = ''
        size = wx.Size(config.expandSize)
        self.fillingDiagnosticsInstanse()
        self.currentPage = 'Diagnostics'
        pos = self.GetPosition()
        try:
            errorPopUp.moving(self.pop, pos, self.currentPage)
        except:
            print('blabla2')

        self.helpMenu.Enable(ID_MENU_BUTTON_DIAGNOSTICS, False)
        self.helpMenu.Enable(wx.ID_HELP, True)
        if self.menuBar.GetLabelTop(1) == 'Connect':
            self.menuBar.Remove(1)
            # 135, 380
            # 340, 340
        self.diagnosticsTopicsPanel.SetMinSize((140, 380))
        self.diagnosticsMaterialScrolledPanel.SetMaxSize((375,340))

        if self.currentPage == 'Help':
            self.clearingInstance()
            self.helpSearchField.SetValue('')

        if self.GetSize() == size:
            self.diagnosticsPanel.Fit()
            self.diagnosticsPanel.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_RIGHT, timeout=config.timeToAppear)
            self.helpPanel.Hide()
            self.windowPanel.Hide()

        else:
            # self.diagnosticsPanel.Hide()
            self.SetMaxSize(size)
            self.FindWindowById(ID_EXPAND_HIDE_BUTTON).Hide()
            for i in range(config.decreaseSize[1], config.expandSize[1]+20, 20):
                self.SetSize(wx.Size(config.expandSize[0], i))
            self.SetMinSize(size)
            self.diagnosticsPanel.Fit()
            self.diagnosticsPanel.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_RIGHT, timeout=config.timeToAppear)
            self.helpPanel.Hide()
            self.windowPanel.Hide()
        self.diagnosticsPanel.Refresh()

    def fillingDiagnosticsInstanse(self, searchString =''):
        with open('diagnostics_DB.json', 'r') as file:
            data = json.load(file)
        index = 0
        for item in data['diagnostics_topics']:
            if searchString not in item['diagnostics_topic']['topic_name'].lower():
                if searchString not in item['diagnostics_topic']['topic_material'].lower():
                    continue
            butSize = (123,15)
            diagnosticsTopicSizerPanel = wx.Panel(self.diagnosticsTopicsPanel)
            diagnosticsTopicSizerPanel.Hide()
            diagnosticsTopicSizer = wx.BoxSizer(wx.VERTICAL)
            diagnosticsTopicSizerPanel.SetSizer(diagnosticsTopicSizer)
            topic = ''
            for i in range(3):
                topic += item['diagnostics_topic']['topic_name']
                topic += ' '
            label, sizeCount = self.transformTopicToFitLabel(topic)
            # print(labeltext, sizeCount)
            # topic = wx.Button(self.diagnosticsTopicsPanel, id=START_DIAGNOSTICS_TOPIC_ID + index, label=labelext, style=wx.NO_BORDER | wx.TEXT_ALIGNMENT_CENTER)
            topicS = wx.BoxSizer()
            topic = wx.StaticText(diagnosticsTopicSizerPanel, id=START_DIAGNOSTICS_TOPIC_ID + index,size=(butSize[0], butSize[1]*(sizeCount)), label=label, style=wx.TE_CENTER, name='Shown')
            topic.Bind(wx.EVT_LEFT_DOWN, self.onTopicButton)
            # topic.SetLabelText(item['diagnostics_topic']['topic_name'])
            # topic.SetLabelText()
            topicS.Add(topic)
            topicS.AddSpacer(15)
            diagnosticsTopicSizer.AddSpacer(3)
            diagnosticsTopicSizer.Add(topicS)
            diagnosticsTopicSizer.AddSpacer(3)
            self.diagnosticsTopicsList.append(diagnosticsTopicSizerPanel)
            self.diagnosticsTopicsSizer.Add(diagnosticsTopicSizerPanel)
            diagnosticsMaterialSizer = wx.BoxSizer()
            label = ''
            for i in range(100):
                label += item['diagnostics_topic']['topic_material']
                label += ' '

            label = self.transformMaterialToFitPanel(label)
            text = wx.StaticText(self.diagnosticsMaterialScrolledPanel)
            text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            diagnosticsMaterialSizer.Add(text)
            self.diagnosticsMaterialsList.append(diagnosticsMaterialSizer)
            self.diagnosticsMaterialScrolledSizer.Add(diagnosticsMaterialSizer)
            self.diagnosticsMaterialScrolledSizer.Hide(diagnosticsMaterialSizer)
            # text.SetLabelText(label)
            text.SetLabelText(label)
            index += 1
        for i in self.diagnosticsTopicsList:
            i.Show()
        self.currentDiagnosticsTopic_ID = START_DIAGNOSTICS_TOPIC_ID
        if len(self.diagnosticsTopicsList) == 0:
            self.diagnosticsSubjectTitelText.SetLabelText('No matches found')
            return
        self.FindWindowById(self.currentDiagnosticsTopic_ID).SetName('Selected')
        self.diagnosticsTopicsList[self.currentDiagnosticsTopic_ID - START_DIAGNOSTICS_TOPIC_ID].SetBackgroundColour('#00BFFF')
        self.FindWindowById(self.currentDiagnosticsTopic_ID).SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.diagnosticsMaterialScrolledSizer.Show(self.diagnosticsMaterialsList[self.currentDiagnosticsTopic_ID - START_DIAGNOSTICS_TOPIC_ID])
        self.diagnosticsSubjectTitelText.SetLabelText(self.transformTopicToFitHeader(self.FindWindowById(self.currentDiagnosticsTopic_ID).GetLabel()))
        self.diagnosticsPanel.Layout()

    def onSearch(self, event):
        searchString = event.GetEventObject().GetValue()
        if searchString == self.searchedString:
            return
        else:
            self.searchedString = searchString
        self.clearingInstance()
        if self.currentPage == 'Help':
            self.fillingHelpInstanse(searchString.lower())
        else:
            self.fillingDiagnosticsInstanse(searchString.lower())

    def clearingInstance(self):
        if self.currentPage == 'Help':
            for i in self.helpTopicsList:
                i.Destroy()
                # children = i.GetChildren()
                # for child in children:
                #     widget = child.GetWindow()
                #     widget.Destroy()
                # self.helpTopicsSizer.Remove(i)
            del self.helpTopicsList[:]
            for i in self.helpMaterialsList:
                children = i.GetChildren()
                for child in children:
                    widget = child.GetWindow()
                    widget.Destroy()
                self.helpMaterialScrolledSizer.Remove(i)
            del self.helpMaterialsList[:]
        else:
            for i in self.diagnosticsTopicsList:
                i.Destroy()
                # children = i.GetChildren()
                # for child in children:
                #     widget = child.GetWindow()
                #     widget.Destroy()
                # self.diagnosticsTopicsSizer.Remove(i)
            del self.diagnosticsTopicsList[:]
            for i in self.diagnosticsMaterialsList:
                children = i.GetChildren()
                for child in children:
                    widget = child.GetWindow()
                    widget.Destroy()
                self.diagnosticsMaterialScrolledSizer.Remove(i)
            del self.diagnosticsMaterialsList[:]

    def onTopicButton(self, event):
        if event.GetEventObject().GetName() == 'Selected':
            return
        topic_id = event.GetEventObject().GetId()
        if self.currentPage == 'Help':
            self.helpSubjectTitelText.SetLabelText(self.transformTopicToFitHeader(self.FindWindowById(topic_id).GetLabel()))
            # self.FindWindowById(self.currentHelpTopic_ID).SetValue(False)
            self.FindWindowById(self.currentHelpTopic_ID).SetName('Shown')
            self.helpTopicsList[self.currentHelpTopic_ID - START_HELP_TOPIC_ID].SetBackgroundColour(wx.NullColour)
            # self.FindWindowById(self.currentHelpTopic_ID).SetBackgroundColour(wx.NullColour)
            self.FindWindowById(self.currentHelpTopic_ID).SetFont(wx.Font(wx.NullFont))
            self.helpMaterialScrolledSizer.Hide(self.helpMaterialsList[self.currentHelpTopic_ID-START_HELP_TOPIC_ID])
            # self.FindWindowById(topic_id).SetValue(True)
            self.FindWindowById(topic_id).SetName('Selected')
            self.helpTopicsList[topic_id - START_HELP_TOPIC_ID].SetBackgroundColour('#00BFFF')
            # self.FindWindowById(topic_id).SetBackgroundColour('#00BFFF')
            self.FindWindowById(topic_id).SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.helpMaterialScrolledSizer.Show(self.helpMaterialsList[topic_id-START_HELP_TOPIC_ID])
            self.currentHelpTopic_ID = topic_id
            self.helpTopicsPanel.Refresh()
        else:
            self.diagnosticsSubjectTitelText.SetLabelText(self.transformTopicToFitHeader(self.FindWindowById(topic_id).GetLabel()))
            # self.FindWindowById(self.currentDiagnosticsTopic_ID).SetValue(False)
            self.FindWindowById(self.currentDiagnosticsTopic_ID).SetName('Shown')
            self.diagnosticsTopicsList[self.currentDiagnosticsTopic_ID - START_DIAGNOSTICS_TOPIC_ID].SetBackgroundColour(wx.NullColour)
            # self.FindWindowById(self.currentDiagnosticsTopic_ID).SetBackgroundColour(wx.NullColour)
            self.FindWindowById(self.currentDiagnosticsTopic_ID).SetFont(wx.Font(wx.NullFont))
            self.diagnosticsMaterialScrolledSizer.Hide(self.diagnosticsMaterialsList[self.currentDiagnosticsTopic_ID - START_DIAGNOSTICS_TOPIC_ID])
            # self.FindWindowById(topic_id).SetValue(True)
            self.FindWindowById(topic_id).SetName('Selected')
            self.diagnosticsTopicsList[topic_id - START_DIAGNOSTICS_TOPIC_ID].SetBackgroundColour('#00BFFF')
            # self.FindWindowById(topic_id).SetBackgroundColour('#00BFFF')
            self.FindWindowById(topic_id).SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            self.diagnosticsMaterialScrolledSizer.Show(self.diagnosticsMaterialsList[topic_id - START_DIAGNOSTICS_TOPIC_ID])
            self.currentDiagnosticsTopic_ID = topic_id
            self.diagnosticsTopicsPanel.Refresh()

    def transformTopicToFitHeader(self, topic):
        topic = topic.replace('\n', ' ')
        topic = textwrap.fill(topic, 52)
        return topic

    def transformTopicToFitLabel(self, topic):
        sizeCount = 0
        item = textwrap.wrap(topic, 19)
        for i in item:
            sizeCount += 1
        topic = textwrap.fill(topic, 19)
        return topic, sizeCount

    def transformMaterialToFitPanel(self, text):
        text = textwrap.fill(text, 55)
        return text

    def onMoreHelp(self, event):
        self.windowMenu.Check(ID_MENU_BUTTON_ALWAYS_ON_TOP, False)
        self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE)
        webbrowser.open('http://e-msion.com/')

    def onDone(self, event):
        self.EnableCloseButton(True)

        self.helpSearchField.SetLabelText('')
        self.diagnosticsSearchField.SetLabelText('')
        self.searchedString = ''
        if self.currentPage == 'Help':
            self.windowPanel.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_RIGHT, timeout=config.timeToAppear)
            self.helpPanel.Hide()
            self.helpMenu.Enable(wx.ID_HELP, True)
        else:
            self.windowPanel.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_LEFT, timeout=config.timeToAppear)
            self.diagnosticsPanel.Hide()
            self.helpMenu.Enable(ID_MENU_BUTTON_DIAGNOSTICS, True)

        if not self.isExpanded:
            size = wx.Size(config.decreaseSize)
            self.SetMinSize(size)
            for i in reversed(range(config.decreaseSize[1], config.expandSize[1] + 20, 20)):
                self.SetSize(wx.Size(config.expandSize[0], i))
            self.SetMaxSize(size)
        self.FindWindowById(ID_EXPAND_HIDE_BUTTON).Show()
        self.clearingInstance()
        self.currentPage = ''
        pos = self.GetPosition()
        try:
            errorPopUp.moving(self.pop, pos, self.currentPage)
        except:
            print('blabla1')
        self.menuBar.Insert(1, self.connectMenu, 'Connect')

    def onIndicatorButton(self, event):
        print(MODES_DICTIONARY_NAME[event.GetId()])
        self.FindWindowById(self.currentModeID).SetBitmap(bitmap=wx.Bitmap('bitmaps/grey_24.png'))
        self.FindWindowById(event.GetId()).SetBitmap(bitmap=wx.Bitmap('bitmaps/green_24.png'))
        self.currentModeID = event.GetId()

    def onShowHideButton(self, event):
        if not self.isExpanded:
            self.expand()
        else:
            self.hide()

    def hide(self):
        self.windowField.Hide(self.bottomSizer, recursive=True)
        self.FindWindowById(ID_EXPAND_HIDE_BUTTON).SetBitmapLabel(wx.Bitmap('bitmaps/expand.png'))
        size = wx.Size(config.decreaseSize)
        self.mainPanel.HideWithEffect(wx.SHOW_EFFECT_SLIDE_TO_TOP, timeout=config.timeToAppear)
        self.SetMinSize(size)
        for i in reversed(range(config.decreaseSize[1],config.expandSize[1]+20,20)):
            self.SetSize(wx.Size(config.expandSize[0],i))
        self.SetMaxSize(size)
        self.bottomSizer.Show(self.FindWindowById(ID_EXPAND_HIDE_BUTTON))
        self.windowField.Layout()
        self.autoTuneButton.SetBackgroundColour('')
        self.FindWindowById(ID_EXPAND_HIDE_BUTTON).SetName('Show')
        self.isExpanded = False

    def expand(self):
        self.windowField.Hide(self.bottomSizer, recursive=True)
        self.FindWindowById(ID_EXPAND_HIDE_BUTTON).SetBitmapLabel(wx.Bitmap('bitmaps/hide.png'))
        size = wx.Size(config.expandSize)
        self.SetMaxSize(size)
        for i in range(config.decreaseSize[1],config.expandSize[1]+20,20):
            self.SetSize(wx.Size(config.expandSize[0],i))
        self.SetMinSize(size)
        # self.Fit()
        self.mainPanel.ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM, timeout=config.timeToAppear)
        self.windowField.Show(self.bottomSizer, recursive=True)
        self.autoTuneButton.SetBackgroundColour(config.autoTuneColour)
        self.windowField.Layout()
        self.FindWindowById(ID_EXPAND_HIDE_BUTTON).SetName('Hide')
        self.isExpanded = True


    def channelOnFocus(self,event):
        if not event.GetEventObject().HasFocus():
            return
        channel_id = event.GetEventObject().GetId()
        if self.currentChannel == channel_id:
            return
        self.selectChannel(channel_id)

    def selectChannel(self, channel):
        # val = self.FindWindowById(self.currentChannel).GetValue()
        for channel1 in ID_CHANNELS:
            val = self.FindWindowById(channel1).GetValue()
            if val == '' or val == '-' or val =='0' or val =='0.' or val =='.0':
                self.FindWindowById(channel1).SetValue('0.0')
        # if False: #channel == ID_FILAMENT:
        #     # Rising field
        #     self.FindWindowById(self.currentChannel + START_CHANNELS_INDICATORS_ID).Show()
        #     self.FindWindowById(self.currentChannel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Hide()
        #     # Squeezing field
        #     # self.FindWindowById(self.currentChannel + START_CHANNELS_INDICATORS_ID).Hide()
        #     # self.FindWindowById(self.currentChannel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Show()
        #
        #     self.chCtrlPanelList[self.currentChannel].SetBackgroundColour(wx.NullColour)
        #     self.chCtrlPanelList[self.currentChannel].Refresh()
        #     self.currentChannel = channel
        #     self.chCtrlPanelList[channel].SetBackgroundColour(cжмюоб.жмюоб.fig.channelBorderColour)
        #     self.chCtrlPanelList[channel].Refresh()
        #     self.updateChannelUI()
        #     # self.mainPanel.Layout()
        # else:
        #     if False: #self.currentChannel == ID_FILAMENT:
        #         self.chCtrlPanelList[self.currentChannel].SetBackgroundColour(wx.NullColour)
        #         self.chCtrlPanelList[self.currentChannel].Refresh()
        #         # Rising Field
        #         self.FindWindowById(channel + START_CHANNELS_INDICATORS_ID).Hide()
        #         self.FindWindowById(channel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Show()
        #         # Squeezing field
        #         # self.FindWindowById(channel + START_CHANNELS_INDICATORS_ID).Show()
        #         # self.FindWindowById(channel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Hide()
        #
        #         self.chCtrlPanelList[channel].SetBackgroundColour(config.channelBorderColour)
        #         self.chCtrlPanelList[channel].Refresh()
        #         self.currentChannel = channel
        #         self.updateChannelUI()
        #         # self.mainPanel.Layout()
        #     else:
        # Rising field
        self.FindWindowById(self.currentChannel + START_CHANNELS_INDICATORS_ID).Show()
        self.FindWindowById(self.currentChannel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Hide()
        # Squeezing field
        # self.FindWindowById(self.currentChannel + START_CHANNELS_INDICATORS_ID).Hide()
        # self.FindWindowById(self.currentChannel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Show()

        self.chCtrlPanelList[self.currentChannel].SetBackgroundColour(wx.NullColour)
        self.chCtrlPanelList[self.currentChannel].Refresh()
        # Rising field
        self.FindWindowById(channel + START_CHANNELS_INDICATORS_ID).Hide()
        self.FindWindowById(channel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Show()
        # Squeezing field
        # self.FindWindowById(channel + START_CHANNELS_INDICATORS_ID).Show()
        # self.FindWindowById(channel + START_CHANNELS_AUXILIARY_INDICATORS_ID).Hide()

        self.chCtrlPanelList[channel].SetBackgroundColour(config.channelBorderColour)
        self.chCtrlPanelList[channel].Refresh()
        # self.FindWindowById(self.currentChannel).SetBackgroundColour(wx.NullColour)
        self.currentChannel = channel
        # self.FindWindowById(self.currentChannel).SetBackgroundColour('#eba6a1')
        if self.currentChannel == ID_FILAMENT:
            self.FindWindowById(12345).Hide()
            self.FindWindowById(12344).Show()
            self.slyder.SetTickFreq(20)
        else:
            self.FindWindowById(12345).Show()
            self.FindWindowById(12344).Hide()
            self.slyder.SetTickFreq(100)
        self.updateChannelUI()

        self.mainPanel.Layout()

    def channelValueChanged(self, event):
        val = self.FindWindowById(event.GetEventObject().GetId())
        id = event.GetEventObject().GetId()
        try:
            if val.GetValue() == '' or val.GetValue() == '-':
                self.slyder.SetValue(0)
                self.slyder.SetSelection(0,0)
                return
            flVal = float(val.GetValue())

            if id == ID_FILAMENT:
                if flVal < 0:
                    raise
                if flVal > self.model.appData.getFilamentMaxCurrent():
                    # val.SetValue(str(self.model.appData.getFilamentMaxCurrent()))
                    raise
            else:
                if flVal > self.model.deviceData.getChannelsMaxValues(id):
                    raise
                if flVal < self.model.deviceData.getChannelsMinValues(id):
                    raise
        except:
            if id == ID_FILAMENT:
                val.SetValue(str(self.model.appData.getFilamentCurrent()))
            else:
                # val.SetValue(str(self.model.deviceData.getChannelsMaxValues(i)))
                val.SetValue(str(self.model.appData.getChannelValue(id)))
            return

        self.model.setChannelValue(id, float(val.GetValue()))
        if self.currentChannel == id:
            valCalc = int(self.model.getChannelValue(self.currentChannel) * self.slyderMultiplier())
            if self.slyder.GetValue() != valCalc:
                self.slyder.SetValue(valCalc)
                val = self.model.getRealValue(self.currentChannel)
                if val > self.slyder.GetValue():
                    self.slyder.SetSelection(self.slyder.GetValue(), int(val * self.slyderMultiplier()))
                else:
                    self.slyder.SetSelection(int(val * self.slyderMultiplier()), self.slyder.GetValue())

    def onRestorePresetsButton(self, event):
        return

    def onAutoTune(self, event):
        return

    def onSliderScroll(self, event):
        self.slyder.SetCanFocus(False)
        obj = event.GetEventObject()
        val = obj.GetValue()
        self.model.setChannelValue(self.currentChannel, float(val) / self.slyderMultiplier())
        self.FindWindowById(self.currentChannel).SetValue(str(float(val) / self.slyderMultiplier()))
        if val > 0:
            self.slyder.SetSelection(0, val)
        else:
            self.slyder.SetSelection(val,0)
        self.slyder.SetCanFocus(False)

    def slyderMultiplier(self):
        if self.currentChannel == ID_CHANNELS[8]:
            return 100
        return 10

    def updateChannelUI(self):
        maxVal = self.model.getMaxValue(self.currentChannel)
        minVal = self.model.getMinValue(self.currentChannel)
        val = self.model.getRealValue(self.currentChannel)
        self.minText.SetLabel(str(minVal))
        self.maxText.SetLabel(str(maxVal))
        self.slyder.SetMax(int(maxVal * self.slyderMultiplier()))
        self.slyder.SetMin(int(minVal * self.slyderMultiplier()))
        self.slyder.SetValue(int(self.model.getChannelValue(self.currentChannel) * self.slyderMultiplier()))
        self.slyder.SetCanFocus(False)
        if val > self.slyder.GetValue():
            self.slyder.SetSelection(self.slyder.GetValue(), int(val * self.slyderMultiplier()))
        else:
            self.slyder.SetSelection(int(val * self.slyderMultiplier()), self.slyder.GetValue())

    def updateDeviceUI(self):
        val = self.model.getRealValue(self.currentChannel)
        if val > self.slyder.GetValue():
            self.slyder.SetSelection(self.slyder.GetValue(), int(val * self.slyderMultiplier()))
        else:
            self.slyder.SetSelection(int(val * self.slyderMultiplier()), self.slyder.GetValue())
        emission = self.model.getEmission()
        self.FindWindowById(STATUS_DICTIONARY_ID[STATUS_DICTIONARY_NAME[ID_EMISSION]]).SetValue(str(emission + u' \u00B5A'))
        voltage = self.model.getFilamentVoltage()
        self.FindWindowById(STATUS_DICTIONARY_ID[STATUS_DICTIONARY_NAME[ID_VOLTAGE]]).SetValue(str(voltage + ' W'))

        for i in range(0, len(ID_CHANNELS)):
            if i == ID_FILAMENT:
                self.FindWindowById(ID_CHANNELS[i] + START_ACT_CHANNELS_ID).SetValue(str(self.model.getRealValue(ID_CHANNELS[i]))+ ' A')
                self.FindWindowById(ID_CHANNELS[i]).SetValue(str(self.model.getChannelValue(ID_CHANNELS[i])))
            else:
                self.FindWindowById(ID_CHANNELS[i]+START_ACT_CHANNELS_ID).SetValue(str(self.model.getRealValue(ID_CHANNELS[i])))
                self.FindWindowById(ID_CHANNELS[i]).SetValue(str(self.model.getChannelValue(ID_CHANNELS[i])))

        # if not self.model.isFilamentOn():
        #     self.filamentBtn.SetLabel('OFF')
        #     self.filamentBtn.SetBackgroundColour(wx.RED)
        # else:
        #     self.filamentBtn.SetLabel('ON')
        #     self.filamentBtn.SetBackgroundColour(wx.GREEN)

    def updateSetValues(self):
        for i in range(0, len(ID_CHANNELS)):
            self.FindWindowById(ID_CHANNELS[i]).SetValue(str(self.model.getChannelValue(ID_CHANNELS[i])))

    def connectWithParams(self, port, baudRate, parity, stopBits, flowControl):
        self.model.connectWithParams(port, baudRate, parity, stopBits, flowControl)

    def OnError(self, message):
        print("error")
        print(message)
        self.connectMenu.SetLabel(ID_MENU_C_DC_BUTTON, '&Connect')
        self.isConnectedToMIPS = False

    def OnConnect(self):
        self.connectMenu.SetLabel(ID_MENU_C_DC_BUTTON, '&Disconnect')
        self.updateUI()
        self.isConnectedToMIPS = True

    def OnCantReconnect(self):
        if not self.IsShown():
            wx.CallLater(500, self.OnCantReconnect)
        else:
            self.connectMenu.SetLabel(ID_MENU_C_DC_BUTTON, '&Connect')
            frame = PortSettings(self)
            frame.setCB(self.connectWithParams)
            size = wx.Size(config.portSettingsSize)
            frame.Show()
            frame.SetSize(size)
            self.isConnectedToMIPS = False

    def updateUI(self):
        if self.model.appData.getConnectionControlValue() == 0:
            if self.isConnectedToMIPS:
                self.connectMenu.SetLabel(ID_MENU_C_DC_BUTTON, '&Connect')
                self.isConnectedToMIPS = False
        else:
            if not self.isConnectedToMIPS:
                self.connectMenu.SetLabel(ID_MENU_C_DC_BUTTON, '&Disconnect')
                self.isConnectedToMIPS = True
        self.updateDeviceUI()
        wx.CallLater(50, self.updateUI)

    def appear(self):
        self.die.Destroy()
        self.Show()

class errorPopUp(wx.PopupWindow):
    def __init__(self, parent, page):
        self.parent = parent
        super().__init__(parent, wx.BORDER_THEME )
        pos = parent.GetPosition()
        if page == '':
            self.SetPosition((pos[0] + 163, pos[1]+48))
        else:
            self.SetPosition((pos[0] + 103, pos[1] + 48))

        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer()
        text = wx.StaticText(self.panel, label=' Error occured')
        sizer.Add(text,1, wx.EXPAND)
        self.panel.SetSizer(sizer)
        self.SetSize(80,18)
        self.panel.Fit()
        import winsound
        winsound.Beep(350, 500)
        self.Show()
        wx.CallLater(5000, self.end)

    def moving(self, pos, page):
        if page == '':
            self.SetPosition((pos[0]+ 163, pos[1]+48))
        else:
            self.SetPosition((pos[0] + 103, pos[1] + 48))

    def end(self):
        self.Destroy()
        self.parent.Refresh()

from wx.lib.pubsub import pub
def sendUpdate():
    pub.sendMessage('update', msg='sended')
