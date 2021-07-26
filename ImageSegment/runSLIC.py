# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 16:54:55 2021
面向对象的SLIC分类算法
@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
from skimage.segmentation import slic    #SCLI算法包
from skimage.segmentation import mark_boundaries  #根据SLIC分割结果生成边界
from skimage.util import img_as_float    #读取影像数据为float型
from skimage import io,color      #颜色库
import matplotlib.pyplot as plt   #绘图制图
import argparse
import skimage.io as SKimg   #读取多种栅格图
import numpy as np

def write_imgArray(filename,im_width, im_height,im_proj,im_geotrans,im_data):
    
    #gdal数据类型包括
    #gdal.GDT_Byte, 
    #gdal .GDT_UInt16, gdal.GDT_Int16, gdal.GDT_UInt32, gdal.GDT_Int32,
    #gdal.GDT_Float32, gdal.GDT_Float64
    # 生成影像
    dataset = gdal.GetDriverByName('GTiff').Create(filename, xsize=im_width, ysize=im_height, bands=1,
                                                     eType=gdal.GDT_Float32)

    proj = osr.SpatialReference()
    proj.SetProjCS('UTM 48N')
    proj.SetWellKnownGeogCS("WGS84")
    proj.SetUTM(48,True)
    
    dataset.SetGeoTransform(im_geotrans)              #写入仿射变换参数
    dataset.SetProjection(proj.ExportToWkt())                    #写入投影
#        dataset.SetWellKnownGeogCS('WGS84')
    dataset.GetRasterBand(1).WriteArray(im_data)  #写入数组数据
   
    del dataset



if __name__ == "__main__": 
    
    # 生成不同作物样本点的光谱或植被指数值
    print('导出图片')

#    imgPath=r'H:\Temp\Ningxia20182019Winter\Vi\RedEdge1\20181108_N9999_R061_MSIL2A_RedEdge1_Bands.tif'
    imgPath=r'H:\Temp\Ningxia20182019Winter\SegmentResult\CTVI\CTVI_MAX_2019.tif'

    Tpan =SKimg.imread(imgPath) #读取全色影像数据（格式为TIFF）

    #TpanRGB=img_as_float(color.gray2rgb(Tpan)) #将灰度图像转为RGB图像
#    rcCount=10980
#    splitimage=Tpan[:,6000:10980]
    
    segments = slic(Tpan.astype('double'), n_segments =50000, sigma = 5) #设置分割数量为100
    
#    cResult=np.zeros((12924,7155))
#    
#    cResult[:,6000:10980]=segments
    
#    refeimage=r'H:\Temp\Ningxia20182019Winter\Vi\RedEdge1\20181101_N9999_R104_MSIL2A_RedEdge1_Bands.tif'
    refeimage=imgPath
    dataj=gdal.Open(refeimage)
    if dataj is None:
        print('Could not open'+refeimage)
    proj=dataj.GetProjection()
    geotrans=dataj.GetGeoTransform()
    outimgepath=r'H:\Temp\Ningxia20182019Winter\SegmentResult\RedEdge1\ctvi-LISC-RS20X20.tif'
    write_imgArray(outimgepath,7155,12924,proj,geotrans,segments)

    plt.imshow(mark_boundaries(Tpan, segments,color=(1, 1, 0), mode='outer', background_label=0)) # 显示分割后的边界线条

    plt.savefig(r'H:\Temp\Ningxia20182019Winter\SegmentResult\RedEdge1\ctvi-LISC-RS20X20-boundary.png',dpi=2000) #分割效果保存出去
    