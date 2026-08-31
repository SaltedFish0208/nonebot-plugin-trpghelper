import json
from pathlib import Path


class JsonIO:
    """
    该类负责使用 pathlib 读写 JSON 文件为字典

    Attr:
        path ("Path"): 指向JSON文件的Path对象
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> dict:
        """
        从 JSON 文件加载数据

        Returns:
            dict: JSON 内容，如果文件不存在返回空字典
        """
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: dict) -> None:
        """
        将字典保存到 JSON 文件

        Args:
            data (dict): 要保存的数据
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8"
        )
