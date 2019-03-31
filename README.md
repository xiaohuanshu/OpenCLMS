# OpenCLMS(名字待定)
## 介绍

适合中国互联网情况的、现代化的开源课堂辅助系统

## 功能

* 微信二维码考勤
* 作业提交
* 资源分享
* 课堂提问
* 等等

## 部署方法(Docker-compose)
1. Clone 代码
2. 复制.env-example 到 .env
3. 编辑.env配置文件
4. 编译: docker-compose build
5. 运行: docker-compose up -d
6. 更新数据表: docker-compose exec web python manage.py migrate

## 部署方法(本地)
1. 安装配置postgresql数据库
1. 安装配置redis缓存服务
1. 安装nginx服务器
1. 安装配置Python2环境
1. Clone代码
1. 复制checkinsystem/local_settings_example.py 到 checkinsystem/local_settings.py
1. 编辑checkinsystem/local_settings.py配置
1. 测试运行 python manage.py runserver
1. 更新数据表: python manage.py migrate
1. 配置uwsgi与nginx

## License
本项目在GNU Affero General Public License version 3协议下开源
