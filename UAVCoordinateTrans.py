#! /usr/bin/env python
#coding=utf-8
import math
import sys
# 常量定义
a_84 = 6378137
b_84 = 6356752.3142451
f_84 = (a_84 - b_84)/a_84
lonOrigin_Jiangmen = 111
# for convenient only
sin = math.sin
cos = math.cos
tan = math.tan
sqrt = math.sqrt
radians = math.radians
degrees = math.degrees
pi = math.pi

# 坐标转换将经纬度转换为UTM坐标
#param lat 经过UTM投影之前的纬度（角度）
#param lon 经过UTM投影之前的经度（角度）
#param lonOrigin 中央经度线（角度）
#param FN 纬度起始点，北半球为0，南半球为10000000.0m     ---------------------------------------------
#param Output:(UTMNorthing, UTMEasting)
#param UTMNorthing 经过UTM投影后的纬度方向的坐标
#param UTMEasting 经过UTM投影后的经度方向的坐标     ---------------------------------------------
#param 功能描述：经纬度坐标投影为UTM坐标，采用美国地理测量部(USGS)提供的公式
#param 作者： Frank. Wu
#param 创建日期：2008年7月19日
#param 版本：1.0
#本程序实现的公式请参考
#"Coordinate Conversions and Transformations including Formulas" p35.
#& http://www.uwgb.edu/dutchs/UsefulData/UTMFormulas.htm
def LL2UTM_USGS(lat, lon, lonOrigin, FN):
    # e表示WGS84第一偏心率,eSquare表示e的平方
    eSquare = 2*f_84 - f_84*f_84
    k0 = 0.9996
    # 确保longtitude位于-180.00----179.9之间
    lonTemp = (lon+180)-int((lon+180)/360)*360-180
    latRad = radians(lat)
    lonRad = radians(lonTemp)
    lonOriginRad = radians(lonOrigin)
    e2Square = (eSquare)/(1-eSquare)
    V = a_84/sqrt(1-eSquare*sin(latRad)**2)
    T = tan(latRad)**2
    C = e2Square*cos(latRad)**2
    A = cos(latRad)*(lonRad-lonOriginRad)
    M = a_84*((1-eSquare/4-3*eSquare**2/64-5*eSquare**3/256)*latRad -(3*eSquare/8+3*eSquare**2/32+45*eSquare**3/1024)*sin(2*latRad)+(15*eSquare**2/256+45*eSquare**3/1024)*sin(4*latRad)-(35*eSquare**3/3072)*sin(6*latRad))
    # x
    UTMEasting = k0*V*(A+(1-T+C)*A**3/6+ (5-18*T+T**2+72*C-58*e2Square)*A**5/120)+ 500000.0
    # y
    UTMNorthing = k0*(M+V*tan(latRad)*(A**2/2+(5-T+9*C+4*C**2)*A**4/24+(61-58*T+T**2+600*C-330*e2Square)*A**6/720))
    #南半球纬度起点为10000000.0m
    UTMNorthing += FN
    return (UTMEasting, UTMNorthing)

