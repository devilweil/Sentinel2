# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 15:10:27 2021
合成时间段内的所有影像的NIR波段到一景影像
@author: LW
"""

from osgeo import gdal,gdal_array,osr, ogr
import os,sys 
import glob
import numpy as np
import random
from skimage import io


    
if __name__ == "__main__":

    ####获取时间范围内的地址列表
#    os.chdir('H:\GraduateFile\Hebei\Bands\Bands10mProjClip')
    os.chdir(r'H:\GraduateFile\Ningxia\Bands\Bands10m')
#    os.chdir(r'H:\GraduateFile\Tulufan\Bands\Bands10mProjClip')
    tifLists=glob.glob('*.tif')
    tifs=[]
    for temp in tifLists:
        days=int(temp.split('.')[0])
        if days<20200415 or days>20201115:
            continue
        else:
            tifs.append(temp)
    
    ####获取导出最小的范围
    x_sizes=[]
    y_sizes=[]
    for tif_temp in tifs:
        data_tif=gdal.Open(tif_temp)
        x_sizes.append(data_tif.RasterXSize)
        y_sizes.append(data_tif.RasterYSize)
    
    x_min,y_min=min(x_sizes),min(y_sizes)
    
    ###获取仿射变换矩阵和参考坐标系
    data_origin=gdal.Open(tifs[0])
    if data_origin is None:
        print('Could not open'+tifs[0])
    proj=data_origin.GetProjection()
    geotrans=data_origin.GetGeoTransform()
    bandscount=len(tifs)
    del data_origin
    #导出影像的存储路径
#    export_file='H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFF\hebei_multiday_NIR.tif'
    export_file=r'H:\GraduateFile\Ningxia\BestScale\MultiDayNIRTIFF\ningxia_multiday_NIR.tif'
#    export_file=r'H:\GraduateFile\Tulufan\BestScale\MultiDayNIRTIFF\tulufan_multiday_NIR.tif'
    print('writing NIR bands...')
    #创建栅格数据
    driver=gdal.GetDriverByName("GTiff")
    datat1_out=driver.Create(export_file,x_min,y_min,bandscount,gdal.GDT_Float32)#GDT_Float32
    datat1_out.SetGeoTransform(geotrans)
    datat1_out.SetProjection(proj)
    for bd in range(bandscount):
        print('bands ',bd)
        tif=gdal.Open(tifs[bd])
        visual_arr = tif.GetRasterBand(4).ReadAsArray(0,0,x_min,y_min) ###ReadAsArray(xoff=0, yoff=0, xsize=512, ysize=512)
        band=datat1_out.GetRasterBand(bd+1)
        band.WriteArray(visual_arr)

    datat1_out.FlushCache()
    del datat1_out
    print('Finish')
    
    
