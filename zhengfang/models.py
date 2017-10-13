# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Xsjbxxb(models.Model):  # 学生基本信息表
    xh = models.CharField(primary_key=True, max_length=20)  # 学号
    xm = models.CharField(max_length=50, blank=True, null=True)  # 姓名
    xb = models.CharField(max_length=2, blank=True, null=True)  # 性别
    sfzh = models.CharField(max_length=20, blank=True, null=True)  # 身份证号
    xzb = models.CharField(max_length=50, blank=True, null=True)  # 行政班
    xy = models.CharField(max_length=30, blank=True, null=True)  # 院系
    zymc = models.CharField(max_length=40, blank=True, null=True)  # 专业
    xjzt = models.CharField(max_length=20, blank=True, null=True)  # 学籍状态

    # mm = models.CharField(max_length=128, blank=True, null=True) #密码

    class Meta:
        managed = False
        db_table = 'xsjbxxb'


class Jsxxb(models.Model):  # 教师信息表
    zgh = models.CharField(primary_key=True, max_length=10)  # 职工号
    xm = models.CharField(max_length=50)  # 姓名
    xb = models.CharField(max_length=2, blank=True, null=True)  # 性别
    bm = models.CharField(max_length=30, blank=True, null=True)  # 部门
    ks = models.CharField(max_length=30, blank=True, null=True)  # 科室

    class Meta:
        managed = False
        db_table = 'jsxxb'


class Xsxkb(models.Model):  # 学生选课表
    xkkh = models.CharField(max_length=35, primary_key=True)  # 选课课号
    xh = models.CharField(max_length=20, blank=True, null=True)  # 学号

    class Meta:
        managed = False
        db_table = 'xsxkb'


class JxrwbviewXy2(models.Model):  # 课程表
    xn = models.CharField(max_length=10, blank=True, null=True)  # 学年
    xq = models.NullBooleanField()  # 学期
    kcdm = models.CharField(max_length=10, blank=True, null=True)  # 课程代码
    kcmc = models.CharField(max_length=250, blank=True, null=True)  # 课程名称
    kkxy = models.CharField(max_length=30, blank=True, null=True)  # 开课学院
    jszgh = models.CharField(max_length=246, blank=True, null=True)  # 教师职工号
    jsxm = models.CharField(max_length=246, blank=True, null=True)  # 教师姓名
    xkkh = models.CharField(max_length=36, primary_key=True)  # 选课课号
    skdd = models.CharField(max_length=380, blank=True, null=True)  # 上课地点
    sksj = models.CharField(max_length=738, blank=True, null=True)  # 上课时间
    xkzt = models.CharField(max_length=1, blank=True, null=True)  # 选课状态
    rs = models.FloatField(blank=True, null=True)  # 学生数

    class Meta:
        managed = False
        db_table = 'jxrwbview_xy2'


class Bjdmb(models.Model):  # 班级表
    bjdm = models.CharField(primary_key=True, max_length=15)  # 班级代码
    bjmc = models.CharField(max_length=50)  # 班级名称
    nj = models.IntegerField(blank=True, null=True)  # 年级
    sfyx = models.CharField(max_length=4, blank=True, null=True)  # 是否有效
    zcrs = models.FloatField(blank=True, null=True)  # 注册人数

    class Meta:
        managed = False
        db_table = 'bjdmb'
