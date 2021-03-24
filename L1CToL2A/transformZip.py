# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 15:16:23 2020

@author: LW
"""

#把整个文件夹内的文件打包
import zipfile
import os
import glob
os.chdir(r'F:\BasicData\OneTIFFYCPlain_L2A_winter')

def DirToZip(dir, zip_fp, delete=False):
    ''' 文件夹打包成zip
    :param dir:     r'C:\data'
    :param zip_fp:  r'C:\data.zip'
    :param delete:  True 删除原文件（可选）
    :return:
    '''
    if not zip_fp.endswith('zip'): return None    #保存路径出错
    fps = []
    zipf = zipfile.ZipFile(zip_fp, "w") #创建一个zip对象
    for root,dirs,fns in os.walk(dir):
        for fn in fns:
            fp = os.path.join(root, fn)
#            arcname = fp.replace(dir, '') #fn在dir中的相对位置
            zipf.write(fp, fp)
            fps.append(fp)
    zipf.close()
    if delete:
        for fp in fps:
            os.remove(fp)
    return zip_fp
def FilesToZip(fps, zip_fp, delete=False):
    ''' 多文件打包成zip
    :param fps:   [r'C:\1.txt', r'C:\2.txt', r'C:\3.txt'] 文件全路径的list
    :param zip_fp:  r'C:\files.zip'
    :param delete:  True    删除原文件
    :return:
    '''
    if len(fps)==0: return None
    if not zip_fp.endswith("zip"): return None
    zipf = zipfile.ZipFile(zip_fp, "w") #在路径中创建一个zip对象
    for fp in fps:
        fn = os.path.basename(fp)
        zipf.write(fp, fn) #第一个参数为该文件的全路径；第二个参数为文件在zip中的相对路径
    zipf.close()    #关闭文件
    if delete:      #删除原文件
        for fp in fps:
            os.remove(fp)
    return zip_fp


if __name__ == '__main__':
    #读取TIF文件到内存中
    filename = glob.glob('*.SAFE')
    
    for filePath in filename:
        print('正在执行：',filePath)
        filepath=filePath.split('.')[0]
        outfile=r'F:/BasicData/OneTIFFYCPlain_L2A_ZIP/'
        # 压缩文件夹
        DirToZip(filePath, outfile+filepath+'.zip')
    print('Complete!')



