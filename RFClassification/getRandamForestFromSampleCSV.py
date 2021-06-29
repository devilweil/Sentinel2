# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 20:42:42 2021

@author: LW
"""
from osgeo import gdal,gdal_array,osr, ogr
import os,sys 
import glob
import numpy as np
import random
from skimage import io
import xlwt

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix


if __name__ == "__main__":
    #获取样本点
    print('Loading XY samples....')
    base_path=r'/home/lw/Sample/Hebei/OptimizeRFResult/XYSample'
    
    x_train = np.loadtxt(open(base_path+'/x_train.csv',"rb"),delimiter=",")
    y_train = np.loadtxt(open(base_path+'/y_train.csv',"rb"),delimiter=",")
    x_test = np.loadtxt(open(base_path+'/x_test.csv',"rb"),delimiter=",")
    y_test = np.loadtxt(open(base_path+'/y_test.csv',"rb"),delimiter=",")
    
    print('x_train shape:',len(x_train),len(x_train[0]))
    print('y_train shape:',len(y_train))
    print('x_test shape:',len(x_test),len(x_test[0]))
    print('y_test shape:',len(y_test))
    
    print('Progressing RF...')
    #,n_estimators=150
    clf = RandomForestClassifier(n_jobs=-1,random_state=0,n_estimators=200)
    clf.fit(x_train, y_train)
    
    print(' RF has trainned ')
    print(clf.feature_importances_)
    
    y_pred=clf.predict(x_test)
    print('confusion_matrix ',confusion_matrix(y_test, y_pred))
    print('OA ',clf.score(x_test, y_test))
    print('Saving confusion_matrix...')
    save_path=r'/home/lw/Sample/Hebei/OptimizeRFResult/RFResult/'
#    save_path=r'/home/lw/Sample/Ningxia/RFResult/'
#    save_path=r'/home/lw/Sample/Tulufan/RFResult/'
    np.savetxt(save_path+'confusion_matrix.csv', confusion_matrix(y_test, y_pred), delimiter = ',')
    
    #开始预测
    print(' RF is beginning to predict... ')
    print('Loading Predict samples')
    file_path=r'/home/lw/Sample/Hebei/OptimizeRFResult/PredictSample/x_predict.csv'
    predict_sample = np.loadtxt(open(file_path,"rb"),delimiter=",")
    predict_result=[]
    for pred_index in range(len(predict_sample)):
        print('Predicting ',pred_index)
        preDS=clf.predict_proba(predict_sample[pred_index])
        print(preDS)
        predict_result.append(preDS)
    
    print('Saving Predict results...')
    np.savetxt(save_path+'hebei_predict_result.csv', predict_result, delimiter = ',')
    
    print('Finish')
    