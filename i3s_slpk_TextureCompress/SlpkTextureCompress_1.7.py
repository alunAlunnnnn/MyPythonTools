import gzip, os
from PIL import Image


# define errors
class NotDir(Exception):
    pass


class NotExist(Exception):
    pass


class CompressSLPK:
    pass


def comPressJPG(dir, newdir):
    fileList = os.listdir(dir)
    for each in fileList:
        openData = os.path.join(dir, each)
        img = Image.open(openData)
        dataName = os.path.basename(newdir)
        newData = os.path.join(newdir, each)
        img.save(newData)


dir = r"D:\a\datas"
newdir = r"D:\a\newdatas"
comPressJPG(dir, newdir)
