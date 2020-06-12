import os, sys

# define errors
class NotDir(Exception):
    pass


class NotExist(Exception):
    pass


class BinPictureReader:
    'this class used to read binary picture, write into a common png picture'

    def __init__(self, picFile):
        self.picFile = picFile
        self.readBinPic()


    def readBinPic(self):
        with open(self.picFile, 'rb') as f:
            binData = f.read()
        self.binData = binData
        return self


    def saveToPNG(self, outputPath, outputName):
        if os.path.exists(outputPath):
            if os.path.isdir(outputPath):
                with open(os.path.join(outputPath, str(outputName) + '.png'), 'wb') as f:
                    f.write(self.binData)
            else:
                print('the directory of outputPath is not available')
                raise NotDir
        else:
            print('the directory of outputPath is not exist')
            raise NotExist


    def saveToJPG(self, outputPath, outputName):
        if os.path.exists(outputPath):
            if os.path.isdir(outputPath):
                with open(os.path.join(outputPath, str(outputName) + '.bin.dds.gz'), 'wb') as f:
                    f.write(self.binData)
            else:
                print('the directory of outputPath is not available')
                raise NotDir
        else:
            print('the directory of outputPath is not exist')
            raise NotExist


# binPic = r'D:\a\nodes_0_textures_0.txt'
binPic = r'D:\a\nodes_0_textures_0_0_1.txt'
binReader = BinPictureReader(binPic)
binReader.saveToJPG('D:/a', 'my_reader2')