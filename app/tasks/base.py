import logging

from celery import Task

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """
    すべてのタスクの基底クラス
    """
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        タスク失敗時のハンドラ
        """
        logger.error(
            f"Task {task_id} failed: {exc}",
            exc_info=einfo,
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
            },
        )

    def on_success(self, retval, task_id, args, kwargs):
        """
        タスク成功時のハンドラ
        """
        logger.info(
            f"Task {task_id} completed successfully",
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
                "result": retval,
            },
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        タスクリトライ時のハンドラ
        """
        logger.warning(
            f"Task {task_id} retrying: {exc}",
            exc_info=einfo,
            extra={
                "task_id": task_id,
                "args": args,
                "kwargs": kwargs,
            },
        )