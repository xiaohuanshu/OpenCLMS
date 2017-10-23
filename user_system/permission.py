# coding=utf-8

permission_data = [
    {
        'name': 'course',
        'direction': u'课程',
        'children': None,
        'operator': [
            'viewlist',
            'control'
        ],
        'operatordirection': [
            '查看课程列表',
            '控制开始\结束\签到'
        ]
    },
    {
        'name': 'checkin',
        'direction': u'考勤',
        'children': [
            {
                'name': 'ask',
                'direction': u'请假',
                'children': None,
                'operator': [
                    'add',
                    'modify',
                    'approve'
                ],
                'operatordirection': [
                    '添加假单',
                    '修改假单',
                    '批准假单'
                ]
            },
        ],
        'operator': [
            'view',
            'modify'
        ],
        'operatordirection': [
            '查看考勤数据',
            '修改考勤数据'
        ]
    },
    {
        'name': 'wechat',
        'direction': u'微信',
        'children': None,
        'operator': [
            'control'
        ],
        'operatordirection': [
            '控制'
        ]
    },
    {
        'name': 'user',
        'direction': u'用户',
        'children': None,
        'operator': [
            'addrole',
            'addpermission'
        ],
        'operatordirection': [
            '分配角色',
            '分配权限'
        ]
    },
    {
        'name': 'school',
        'direction': u'学校',
        'children': [
            {
                'name': 'student',
                'direction': u'学生',
                'children': None,
                'operator': [
                    'view',
                    'modify'
                ],
                'operatordirection': [
                    '查看',
                    '修改'
                ]
            },
            {
                'name': 'teacher',
                'direction': u'教师',
                'children': None,
                'operator': [
                    'view',
                    'modify'
                ],
                'operatordirection': [
                    '查看',
                    '修改'
                ]
            },
            {
                'name': 'class',
                'direction': u'班级',
                'children': None,
                'operator': [
                    'view'
                ],
                'operatordirection': [
                    '查看'
                ]
            },
            {
                'name': 'major',
                'direction': u'专业',
                'children': None,
                'operator': [
                    'view'
                ],
                'operatordirection': [
                    '查看'
                ]
            },
            {
                'name': 'department',
                'direction': u'部门',
                'children': None,
                'operator': [
                    'view'
                ],
                'operatordirection': [
                    '查看'
                ]
            },
            {
                'name': 'department',
                'direction': u'行政部门',
                'children': None,
                'operator': [
                    'view'
                ],
                'operatordirection': [
                    '查看'
                ]
            },
            {
                'name': 'classroom',
                'direction': u'教室',
                'children': None,
                'operator': [
                    'view'
                ],
                'operatordirection': [
                    '查看'
                ]
            },
            {
                'name': 'schoolterm',
                'direction': u'学期',
                'children': None,
                'operator': [
                    'view',
                    'modify'
                ],
                'operatordirection': [
                    '查看',
                    '修改'
                ]
            },
            {
                'name': 'classtime',
                'direction': u'学期',
                'children': None,
                'operator': [
                    'view',
                    'modify'
                ],
                'operatordirection': [
                    '查看',
                    '修改'
                ]
            },
        ], 'operator': ['privacy'],
        'operatordirection': ['隐私查看']
    },
]
