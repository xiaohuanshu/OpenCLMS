# -*- coding: utf-8 -*-
__author__ = 'xiaohuanshu'
LESSON_STATUS_AWAIT = 0  # 默认状态,还未开始
LESSON_STATUS_AGREE = 1  # 特殊,允许开始
LESSON_STATUS_CHECKIN = 2  # 首签
LESSON_STATUS_NOW = 3  # 正在上课
LESSON_STATUS_CHECKIN_ADD = 4  # 补签
LESSON_STATUS_CHECKIN_AGAIN = 10  # 再签
LESSON_STATUS_CANCLE = 5  # 课程取消
LESSON_STATUS_WRONG = 6  # 课程未正常开始
LESSON_STATUS_END = 7  # 课程结束
LESSON_STATUS_END_EARLY = 8  # 超前结束
LESSON_STATUS_START_LATE = 9  # 较晚开始
LESSON_STATUS_TRANSFERRED = 11  # 被转移
LESSON_STATUS_NEW_AWAIT = 12  # 新添加，未开始

COURSE_HOMEWORK_TYPE_NOSUBMIT = 0  # 无需提交
COURSE_HOMEWORK_TYPE_ONLINESUBMIT = 1  # 在线提交
COURSE_HOMEWORK_TYPE_ONLINEANSWER = 2  # 在线作答
