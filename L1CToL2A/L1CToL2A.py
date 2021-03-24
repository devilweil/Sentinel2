# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 16:56:33 2021

@author: LW
"""
# 使用Python标准库调用Sen2cor命令行命令批量对Sentinel-2 L1C数据进行大气校正
import subprocess
import zipfile
import os
#import sys
#sys.setdefaultencoding('utf-8')

#临时存储解压数据目录
os.chdir(r'H:\PreprocessData\TempData')
#定义一个解压函数
def unzip_file(zip_file_name, mode='rb'):
    """
    Return a unzipped file name which comes from the zipped file of A Sentinel-2 L1C data
    返回Sentinel-2 L1C级.zip文件解压后的文件名
    zip_file_name   - the zipped file name of A Sentinel-2 L1C data  
    mode            - Optional parameter, the mode of the zipped file reader 
    """
    #打开.zip文件
    zip_file = open(zip_file_name, mode)
    #利用zipfile包解压文件
    zip_fn = zipfile.ZipFile(zip_file)
    #获取.zip文件的所有子目录名和文件名
    namelist = zip_fn.namelist()
    for item in namelist:
        #提取.zip文件的子目录及文件，解压在当前文件夹（'.'表示当前文件夹）
        zip_fn.extract(item, '.')
    #关闭.zip文件
    zip_fn.close()
    zip_file.close()    
    #打印解压完成
    print("Unzipping finished!")
    #返回解压后的文件名（字符串，带.SAFE后缀）
    return namelist[0]
       
#S·····························································en2cor.bat文件所在路径
sen2cor_path = r"D:\ExcuteEXE\Sen2Cor-02.08.00-win64\Sen2Cor-02.08.00-win64\L2A_Process.bat"
#Sentinel-2 L1C原始数据（.zip格式文件，无需解压）所在目录
origin_dir = r"F:\基础数据\哨兵二数据\吐鲁番\TLF_new"
#文件模式
pattern = ".zip"
#输出目录
output_dir = r"F:\BasicData\TulufanS2\TLF_new_L2A"

for in_file in os.listdir(origin_dir):
    ###过滤已经生成的L2A
    safaList=os.listdir(r'H:\PreprocessData\TempData')
    in_file_Safe=in_file.split('.')[0]+'.SAFE'
    if in_file_Safe in safaList:
        continue
    
    # 判断是否是.zip文件
    if pattern in in_file:
        #获取.zip文件的完整路径
        zip_file_path = os.path.join(origin_dir, in_file)
        #解压.zip文件，产生.safe格式文件
        safe_in_file_path = unzip_file(zip_file_path)
        
        #设置Sen2cor命令行参数，按照原始分辨率处理
        cmd_args = [sen2cor_path, safe_in_file_path,'--output_dir', output_dir]
        
        #打印处理开始的消息
        print("{} processing begin!".format(safe_in_file_path))
        #传入命令行参数并调用命令行(cmd)执行命令
        subprocess.call(cmd_args)
        #打印处理完成的消息
        print("{} processing finished!\n".format(safe_in_file_path))

#打印所有文件处理完成的消息
print("All zipped file finished!") 
