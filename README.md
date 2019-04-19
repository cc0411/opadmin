#安装rabbitmq
wget https://github.com/rabbitmq/erlang-rpm/releases/download/v20.1.7.1/erlang-20.1.7.1-1.el6.x86_64.rpm
yum localinstall erlang-20.1.7.1-1.el6.x86_64.rpm
wget https://dl.bintray.com/rabbitmq/all/rabbitmq-server/3.7.7/rabbitmq-server-3.7.7-1.el6.noarch.rpm
yum localinstall rabbitmq-server-3.7.7-1.el6.noarch.rpm
## 启动
/etc/init.d/rabbitmq-server
## 使用
rabbitmqctl add_user opadmin  opadmin
rabbitmqctl add_vhost myhost
rabbitmqctl set_permissions -p myhost opadmin ".*" ".*" ".*"
#配置celery后台启动
cp conf/celeryd.conf /etc/default/celeryd
### 将配置文件里的内容按照实际情况更改

cp conf/celeryd.server /etc/init.d/celeryd
cp conf/celerybeat.server /etc/init.d/celerybeat
/etc/init.d/celeryd start  ##如果出现celeryd无法启动，则添加环境变量：export C_FORCE_ROOT="true"
/etc/init.d/celerybeat start
#安装redis
#安装mysql
#初始化表
create database ops CHARACTER SET utf8 COLLATE utf8_general_ci;
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

最后执行db.sql里面的内容

#测试使用celery  相关命令
Celery -A opadmin  worker -l info
celery -A opadmin  beat -l info -S django  #监听后面定时任务
3. 启动flower celery -A opadmin  flower
http://localhost:5555/tasks web后台界面可以查看任务执行状态