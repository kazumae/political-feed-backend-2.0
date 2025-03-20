# このファイルは後方互換性のために残されています
# 新しい実装は app/tasks/data_collection/ ディレクトリに移行されました

from app.tasks.data_collection.collect import collect_data

__all__ = ["collect_data"]
