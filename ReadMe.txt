pip install celery -i https://mirrors.aliyun.com/pypi/simple
pip install redis -i https://mirrors.aliyun.com/pypi/simple
pip install requests -i https://mirrors.aliyun.com/pypi/simple


cd /Users/xiewangyi/projects/laoshisync/laoshisync
celery -A celery_app.celery worker  --loglevel=debug
celery -A celery_app.celery beat  --loglevel=debug


sudo pip install celery
sudo pip install redis
sudo pip install requests

nohup celery -A celery_app.celery worker  --loglevel=debug > celery_worker.log &
nohup celery -A celery_app.celery beat  --loglevel=debug > celery_beat.log &