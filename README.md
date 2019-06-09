# OpenCLMS
## 介绍

适合中国互联网情况的、现代化的开源课堂辅助系统

## 功能

* 微信二维码考勤
* 作业提交
* 资源分享
* 课堂通知微信推送
* 课堂提问、随机点名
* 在线课表、课表导入手机日历
* 课程数据统计，每日报表
* 正方教务系统数据自动同步
* 等等

## 部署方法(Docker-compose)
1. Clone 代码

```
git clone https://github.com/xiaohuanshu/OpenCLMS.git
```

2. 复制.env-example 到 .env

```
cp .env-example .env
```

3. 编辑.env配置文件，具体配置含义见下文

```
vim .env
```

4. 编译Docker镜像
```
docker-compose build
```
5. 运行所有相关系统(容器)

```
docker-compose up -d
```

6. 更新\初始化数据表

```
docker-compose run --rm web python manage.py migrate
```

7. 首次运行需创建管理员帐号

```
docker-compose run --rm web python manage.py createsuperuser
```

随后即可通过浏览器访问0.0.0.0:80，通过创建的管理员帐号密码登录。其它学生、教师、课程数据可通过正方同步功能同步，可通过权限系统赋予其它教师管理员权限。

## 部署方法(本地)
1. 安装配置postgresql数据库
1. 安装配置redis缓存服务
1. 安装nginx服务器
1. 安装配置Python2环境
1. Clone代码
1. 复制checkinsystem/local_settings_example.py 到 checkinsystem/local_settings.py
1. 编辑checkinsystem/local_settings.py配置
1. 测试运行 `python manage.py runserver`
1. 更新数据表: `python manage.py migrate`
1. 首次运行需创建管理员帐号`python manage.py manage.py createsuperuser`
1. 配置uwsgi与nginx

## 配置文件说明

配置 | 默认值 | 说明
---|---|---
POSTGRES_PASSWORD | 必填 |  PostgreSQL数据库密码，在Docker-compose部署模式下，第一次配置有效，后续不能通过修改配置文件来修改密码 
SECRET_KEY | 必填 |  系统随机密钥，请确保此值为随机字符串并且不能泄露
DOMAIN | 必填 |  域名，系统必须使用已备案域名 
CHECKINURL | 必填 |  签到二维码地址，请填写http://域名/checkin/ck
SCHOOLEMAIL | 必填 |  学校邮箱域(@后面)
QRCODEREFRESHTIME | 5 |  考勤二维码变换时间(s)
BROWSER_DOWNLOAD_URL | 无 |  客户端下载地址，本系统windows客户端暂不开源 
WECHAT_TOKEN | 必填 |  企业微信认证相关,具体见下文
WECHAT_CORPID | 必填 |  注册企业微信时的企业id
WECHAT_AGENTID | 必填 |  企业微信认证相关,具体见下文
WECHAT_APPSECRET | 必填 |  企业微信认证相关,具体见下文
WECHAT_ENCODINGAESKEY | 必填 |  企业微信认证相关,具体见下文
CONTACTSECRET | 必填 |  企业微信认证相关,具体见下文
WECHATQRCODEURL | 必填 |  未关注用户尝试扫描二维码考勤时的关注指引链接 
WEEK_FIRST_DAY | 1 |  每周哪一天为首日，1为周一；0为周日
DATABASE_URL | 必填 |  数据库连接配置，请填写 `postgres://postgres:数据库密码@postgres:5432/postgres`
ZHENGFANG_DATABASE_URL | 必填 |  正方教务系统数据库连接配置，请填写 `oracle://zfxfzb:密码@数据库ip地址:1521/ORCL`其中正方教务系统默认数据库名为zfxfzb，默认数据库端口为5423
REDIS_URL | 必填 |  Redis配置，使用Docker-Compose填写redis://redis:6379/1即可
EMAIL_HOST | 无 |  系统邮件SMTP (系统邮件用于发送找回密码等自动触发的邮件)
EMAIL_PORT | 无 | 系统邮件 SMTP端口
EMAIL_HOST_USER | 无 |  系统邮件地址
EMAIL_HOST_PASSWORD | 无 |  系统邮件密码
EMAIL_SUBJECT_PREFIX | 无 |  邮件标题前缀
SERVER_EMAIL | 无 |  系统邮件服务地址，同系统邮件地址即可

## 企业微信配置

OpenCLMS需要一个认证的企业微信帐号

企业微信相关文档：https://work.weixin.qq.com/help?person_id=1

企业微信添加OpenCLMS应用过程：

1. 打开企业微信-应用与小程序https://work.weixin.qq.com/wework_admin/frame#apps
2. 在自建标签中，点击创建应用，输入应用名称
![image](https://github.com/xiaohuanshu/OpenCLMS/blob/master/docs/wx1.png?raw=true)
3. 创建成功后，记录此应用的AgentId，填入配置文件中的WECHAT_AGENTID，记录Secret填入配置文件中的`WECHAT_APPSECRET`
![image](https://github.com/xiaohuanshu/OpenCLMS/blob/master/docs/wx2.png?raw=true)
4. 点击下方网页授权及JS-SDK中的设置可信域名，填入OpenCLMS系统的域名
![image](https://github.com/xiaohuanshu/OpenCLMS/blob/master/docs/wx3.png?raw=true)
5. 点击接受消息中的设置API接受，URL处填入`http://域名/wechat/api`，Token选择随机生成，并写入配置文件中的`WECHAT_TOKEN`，EncodingAESKey选择随机生成，并写入配置文件中的`WECHAT_ENCODINGAESKEY`,勾选上报地理位置
![image](https://github.com/xiaohuanshu/OpenCLMS/blob/master/docs/wx4.png?raw=true)
6. 点击企业微信授权配置中的设置，在Web网页中的设置授权回调域中填写系统域名
![image](https://github.com/xiaohuanshu/OpenCLMS/blob/master/docs/wx5.png?raw=true)
7. 在管理工具-通讯录同步(https://work.weixin.qq.com/wework_admin/frame#apps/contactsApi)中,开启API同步，并生成Secret，写入配置文件中的`CONTACTSECRET`
![image](https://github.com/xiaohuanshu/OpenCLMS/blob/master/docs/wx6.png?raw=true)

系统安装完毕后，运行命令`docker-compose run --rm web python manage.py createmenu`创建微信应用菜单

## Docker-compose 容器说明
使用Docker-compose部署后会启动5个容器

容器名 | 作用
---|---
openclms_nginx_1 | Http服务器
openclms_celery_1 | 用于执行定时任务，定时同步、定时生成考勤统计等
openclms_web_1 | OpenCLMS系统主程序
openclms_redis_1 | Redis服务器，用于缓存
openclms_postgres_1 | PostgreSQL数据库服务器，用于储存数据

## 日志
全部日志储存在容器下的/usr/src/app/logs目录中，具体含义如下：

日志名 | 含义
---|---
access.log | Nginx访问日志
checkinlog.log | 考勤相关日志
courselog.log | 课程操作相关日志
error.log | Nginx访问失败日志
request.log | 系统请求错误日志
schoollog.log | 学校操作相关日志
userlog.log | 用户相关日志
wechatlog.log | 与微信交互中的相关日志
zhengfanglog.log | 同步正方教务数据的相关日志

## License

OpenCLMS项目在GNU Affero General Public License version 3协议下开源

AGPL协议详情：https://www.gnu.org/licenses/agpl-3.0.html

项目地址:https://github.com/xiaohuanshu/OpenCLMS