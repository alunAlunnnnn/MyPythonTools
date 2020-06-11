demoDict = {'a': {'b': 1, 'c': 2}, 'd': {'e': 3, 'f': {'g': 4}}, 'h': 5}

def flatMap(dicData):
    def _flatMap(dicData, resDict=None, resKey=''):
        for eachKey, eachValue in dicData.items():
            if isinstance(eachValue, (dict, list, tuple, set)):
                _flatMap(eachValue, resDict, eachKey + '.')
            else:
                newKey = resKey + eachKey
                resDict[newKey] = eachValue
        return resDict

    resDict = {}
    _flatMap(dicData, resDict)
    return resDict

print(flatMap(demoDict))
