import pickle

class ProfileData:
    def __init__(self):
        self.channelsValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.filamentValue = 0.0
        self.filamentMaxValue = 2.0
        self.directionValue = 1
        self.channelsNames = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Channel5', 'Channel6', 'Channel7', 'Channel8', 'Filament']
    
def saveToFile(path, appData):
    profile = ProfileData()
    profile.channelsNames = appData.channelsNames
    profile.filamentMaxValue = appData.getFilamentMaxCurrent()
    profile.filamentValue = appData.getFilamentCurrent()
    profile.directionValue = appData.getDirectionValue()
    for x in range(0, 8):
        profile.channelsValues[x] = appData.getChannelValue(x)
    with open(path, "wb") as f:
        pickle.dump(profile, f, pickle.HIGHEST_PROTOCOL)
    
def loadFromFile(path, appData):
    with open(path, "rb") as f:
        profile = pickle.load(f)
        appData.channelsNames = profile.channelsNames
        appData.setFilamentMaxCurrent(profile.filamentMaxValue)
        appData.setFilamentCurrent(profile.filamentValue)
        appData.setDirectionValue(profile.directionValue)
        for x in range(0, 8):
            appData.setChannelValue(x, profile.channelsValues[x])