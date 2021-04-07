# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 16:44:53 2021
获取真彩色影像和场景识别
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
import imageio
import os
import glob
from datetime import date
import math
import numpy as np
import zipfile

os.chdir(r'H:\TempData\L2A')
os.environ['CPL_ZIP_ENCODING'] = 'UTF-8'


def write_MultiBands_imgArray(filename,im_proj,im_geotrans,im_data,pronames):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1,im_data.shape 

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    dataset.SetGeoTransform(im_geotrans)
    
    proj = osr.SpatialReference()
    proj.SetProjCS(pronames)
    proj.SetWellKnownGeogCS("WGS84")
    proj.SetUTM(int(pronames[len(pronames)-3:len(pronames)-1]),True)
    
    dataset.SetProjection(proj.ExportToWkt())

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i+1).WriteArray(im_data[i])

    del dataset


###获取真彩色
def getTrueImage(filePath,ds_list):
    visual_ds = gdal.Open(ds_list[3][0])  # 取出第12个数据子集（MODIS反射率产品的第一个波段）
    visual_arr = visual_ds.ReadAsArray()  # 将数据集中的数据转为ndarray
    if visual_arr is None: 
        return
    ####获取投影坐标带号
    UTMName=ds_list[3][1].split(',')[1]
    print(UTMName[len(UTMName)-3:len(UTMName)-1])
#    
    splitName=filePath.split('_')[2].split('T')[0]+'_'+filePath.split('_')[3]+'_'+filePath.split('_')[4]+'_'+filePath.split('_')[1]
    splitName=splitName+'_TrueImage_Bands.tif'
    filenames='H:/TempData/TrueImage/'+splitName
    write_MultiBands_imgArray(filenames,visual_ds.GetProjection(),visual_ds.GetGeoTransform(),visual_arr,UTMName)
    

    del visual_arr
    del visual_ds

###获取场景图层分类结果
def getSLC(filePath,ds_list):
    z = zipfile.ZipFile(filePath, "r")
    #打印zip文件中的文件列表
    slc=''
    for filename in z.namelist( ):
        if filename.find('SCL_20m')<0:
            continue
        else:
            slc=filename
            print('File:', slc)
    
    #读取SLC图层
    jp2file=slc.split('/')[len(slc.split('/'))-1]
    savePath=r'H:\TempData\JP2'
    z.extract(slc,savePath)#从zip文件中获得名为filename_fz的文件
    z.close()#关闭zip文件
    
    visual_ds = gdal.Open(savePath+'\\'+slc)
    visual_arr = visual_ds.ReadAsArray()  # 将数据集中的数据转为ndarray
    if visual_arr is None: 
        return
    
    ####获取投影坐标带号
    UTMName=ds_list[3][1].split(',')[1]
    print(UTMName[len(UTMName)-3:len(UTMName)-1])
#    
    splitName=filePath.split('_')[2].split('T')[0]+'_'+filePath.split('_')[3]+'_'+filePath.split('_')[4]+'_'+filePath.split('_')[1]
    splitName=splitName+'_slc_Bands.tif'
    filenames='H:/TempData/SLC/'+splitName
    write_MultiBands_imgArray(filenames,visual_ds.GetProjection(),visual_ds.GetGeoTransform(),visual_arr,UTMName)
    
    
    
    
    
    

if __name__ == "__main__": 
    #读取TIF文件到内存中
    filename = glob.glob('*.zip')
    
    for filePath in filename:
        print('正在执行：',filePath)
        # 打开栅格数据集
        root_ds = gdal.Open(r'H:\TempData\L2A\\'+filePath,1)
        # 返回结果是一个list，list中的每个元素是一个tuple，每个tuple中包含了对数据集的路径，元数据等的描述信息
        # tuple中的第一个元素描述的是数据子集的全路径
        ds_list = root_ds.GetSubDatasets()
#        ###获取真彩色
        getTrueImage(filePath,ds_list)
        ###获取场景图层分类
        getSLC(filePath,ds_list)

    print('Complete')
