import win32com.client as win32
import os.path
import os

def xlsToxlsx():
    # 需要转换的xls文件存放处
    rootdir = r"D:\work\污水excel\20200619报告数据(密码wslzp0616)\1标待上传0616"
    # 转换好的xlsx文件存放处
    rootdir1 = r"D:\work\污水excel\20200619报告数据(密码wslzp0616)\xlsx"
    files = os.listdir(rootdir)
    num = len(files)
    for i in range(num):
        kname = os.path.splitext(files[i])[1]
        if kname == '.xls':
            fname = rootdir + '\\' + files[i]
            fname1 = rootdir1 + '\\' + files[i]
            excel = win32.gencache.EnsureDispatch('Excel.Application')
            wb = excel.Workbooks.Open(fname)
            wb.SaveAs(fname1+"x", FileFormat = 51)
            wb.Close()
            excel.Application.Quit()

if __name__ == '__main__':
    xlsToxlsx()
