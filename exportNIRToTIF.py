# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 15:57:30 2021

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

    #导出影像的存储路径
#    export_file='H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFF\hebei_multiday_NIR.tif'
#    export_file=r'H:\GraduateFile\Ningxia\BestScale\MultiDayNIRTIFF\ningxia_multiday_NIR.tif'
    
    print('writing NIR bands...')
#    bands=[1,2,3,5,6,7]
    bands=[1,2,3,4]
    for bd in range(len(tifs)):
        print('tif is  ',tifs[bd])
        tif=gdal.Open(tifs[bd])
        proj=tif.GetProjection()
        geotrans=tif.GetGeoTransform()
        x_sizes=tif.RasterXSize
        y_sizes=tif.RasterYSize
        
        for bandcount in bands:
            visual_arr = tif.GetRasterBand(bandcount).ReadAsArray() ###ReadAsArray(xoff=0, yoff=0, xsize=512, ysize=512)
        
        #创建栅格数据
#            export_file=r'H:\GraduateFile\Hebei\BestScale\MultiDayNIRTIFFs\\'+str(bandcount)+'\\'+tifs[bd]
            export_file=r'H:\GraduateFile\Ningxia\BestScale\MultiDayNIRTIFFs\\'+str(bandcount)+'\\'+tifs[bd]
#            export_file=r'H:\GraduateFile\Tulufan\BestScale\MultiDayNIRTIFFs\\'+str(bandcount)+'\\'+tifs[bd]
        
            driver=gdal.GetDriverByName("GTiff")
            datat1_out=driver.Create(export_file,x_sizes,y_sizes,1,gdal.GDT_Float32)#GDT_Float32
            datat1_out.SetGeoTransform(geotrans)
            datat1_out.SetProjection(proj)
            band=datat1_out.GetRasterBand(1)
            band.WriteArray(visual_arr)
            datat1_out.FlushCache()
            del datat1_out

    print('Finish')
