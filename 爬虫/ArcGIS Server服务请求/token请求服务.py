import requests



def getToken(username, password, serverHost, serverPort, availMinuteTime):
    tokenUrl = "/arcgis/admin/generateToken"

    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"

    para = {
        "username": username,
        "password": password,
        "client": "requestip",
        "f": "json",
        "expiration": availMinuteTime
    }

    headers = {
        "User-Agent": ua,
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }

    reqUrl = f"http://{serverHost}:{serverPort}/{tokenUrl}"

    # req = requests.get(reqUrl, headers=headers, params=para)
    req = requests.post(reqUrl, headers=headers, data=para)

    return req.json()["token"]


def reqSerWithToken(serHost, serPort, username, password, availMinuteTime, serFolder, serName, serType):
    # get token from token generate
    token = getToken(username, password, serHost, serPort, availMinuteTime)

    # generate request parameters
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"

    para = {
        "token": token,
        "f": "json",
    }

    headers = {
        "User-Agent": ua,
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"
    }

    reqUrl = f"http://{serHost}:{serPort}/arcgis/rest/services/{serFolder}/{serName}/{serType}"
    print(reqUrl)
    res = requests.post(reqUrl, data=para, headers=headers)
    print(res.text)
    print(res.json())




username = "siteadmin"
password = "Hs_123456"
serverHost = "192.168.2.235"
serverPort = "6080"
availMinuteTime = "90"
serFolder = "GL_SJ"
serName = "SH_SJ_YX_WGS84V2"
serType = "MapServer"

reqSerWithToken(serverHost, serverPort, username, password, availMinuteTime, serFolder, serName, serType)
