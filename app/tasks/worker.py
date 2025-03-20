
from app.core.config import settings
from celery import Celery

# Celeryインスタンスの作成
celery_app = Celery("political_feed")

# Celeryの設定
celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL

# タスクの自動検出
celery_app.autodiscover_tasks(["app.tasks"])

# タスクの実行時間制限
celery_app.conf.task_time_limit = 30 * 60  # 30分
celery_app.conf.task_soft_time_limit = 15 * 60  # 15分

# タスクのリトライ設定
celery_app.conf.task_acks_late = True
celery_app.conf.task_reject_on_worker_lost = True

# タスクのシリアライザ
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

# タイムゾーン
celery_app.conf.timezone = "Asia/Tokyo"
celery_app.conf.enable_utc = True

# ワーカープール設定
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.worker_max_tasks_per_child = 1000

# タスクキューの設定
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_queues = {
    "default": {"exchange": "default", "routing_key": "default"},
    "high_priority": {
        "exchange": "high_priority",
        "routing_key": "high_priority"
    },
    "low_priority": {
        "exchange": "low_priority",
        "routing_key": "low_priority"
    },
}

# 定期タスクの設定
celery_app.conf.beat_schedule = {
    "data-collection-every-hour": {
        "task": "app.tasks.data_collection.collect.collect_data",
        "schedule": 60 * 60,  # 1時間ごと
        "options": {"queue": "low_priority"},
    },
}