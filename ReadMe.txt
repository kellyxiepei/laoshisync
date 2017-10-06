pip install celery -i https://mirrors.aliyun.com/pypi/simple
pip install redis -i https://mirrors.aliyun.com/pypi/simple
pip install requests -i https://mirrors.aliyun.com/pypi/simple

cd /Users/xiewangyi/projects/laoshisync/laoshisync
celery -A celery_app.celery worker  --loglevel=debug
celery -A celery_app.celery beat  --loglevel=debug