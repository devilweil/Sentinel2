# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 19:46:33 2021
针对未压缩的Safe的文件进行真彩色和SCL导出
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
import os
import glob
from datetime import date
import numpy as np

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
  
def get20MBandsOneTIFF(filePath): 
    
    # 打开栅格数据集
    root_ds = gdal.Open(filePath+'\MTD_MSIL2A.xml',1)
    # 返回结果是一个list，list中的每个元素是一个tuple，每个tuple中包含了对数据集的路径，元数据等的描述信息
    # tuple中的第一个元素描述的是数据子集的全路径
    ds_list = root_ds.GetSubDatasets()
    ###定义遥感坐标参数
    visual_ds = gdal.Open(ds_list[1][0])
    im_geotrans=visual_ds.GetGeoTransform()
    
    pronames=ds_list[1][1].split(',')[6]
    proj = osr.SpatialReference()
    proj.SetProjCS(pronames)
    proj.SetWellKnownGeogCS("WGS84")
    proj.SetUTM(int(pronames[len(pronames)-3:len(pronames)-1]),True)
    
    del visual_ds
    
    ####创建栅格
    savepath=r'H:\TempData\TrueImage\\'
    splitname=filePath.split('.')[0]+'_TCI.tif'
#    splitname=filePath.split('_')[2].split('T')[0]+'.tif'
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(savepath+splitname, 5490, 5490, 3, gdal.GDT_UInt16)
    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(proj.ExportToWkt())
    
    
    ######导出20m空间分辨率的波段
#    bands=['B02','B03','B04','B05','B06','B07','B8A','B11','B12']
#    bands=['SCL']
    bands=['TCI']
    for index in range(len(bands)):
        bn=bands[index]+'_20m'
        # 打开JP2栅格数据集
        jp2path=findfile(bn,filePath)
        ###导出多波段影像
        visual_ds = gdal.Open(jp2path)
        visual_arr = visual_ds.ReadAsArray()  # 将数据集中的数据转为ndarray
        if visual_arr is None: 
            print('visual_arr is None',bands[index])
            return
#        dataset.GetRasterBand(1).WriteArray(visual_arr)
        band=visual_arr.shape[0]
        for ind in range(band):

            dataset.GetRasterBand(ind+1).WriteArray(visual_arr[ind])

    del dataset

####找到包含特定字符串的文件，并返回绝对路径
def findfile(keyword,root):
    filelist=[]
    for root,dirs,files in os.walk(root):
        for name in files:                
            filelist.append(os.path.join(root, name))
#            print(os.path.join(root, name))
    ###找到包含特定字符串的文件，并返回
    returnStr=''
    for i in filelist:            
        if os.path.isfile(i):
            if keyword in os.path.split(i)[1]:
                returnStr=i
                break
    
    return returnStr
    
if __name__ == "__main__": 
    #读取TIF文件到内存中
    os.chdir(r'H:\TempData\L2A')
    
    filename = glob.glob('*.SAFE')
    
    for filePath in filename:
        print('正在执行：',filePath)
        ###获取场景图层分类
        get20MBandsOneTIFF(filePath)

    print('Complete')
