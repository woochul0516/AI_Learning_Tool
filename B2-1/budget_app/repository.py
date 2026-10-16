import os
import json
import tempfile
from typing import Generator, List, Dict, Optional
from .models import Transaction, Budget

DEFAULT_CATEGORIES = ["food", "transport", "rent", "salary", "etc"]

class BaseRepository:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)


class CategoryRepository(BaseRepository):
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.file_path = os.path.join(self.data_dir, "categories.jsonl")
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not os.path.exists(self.file_path):
            self.save_all(DEFAULT_CATEGORIES)

    def load_all(self) -> List[str]:
        if not os.path.exists(self.file_path):
            return []
        categories = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    categories.append(data["name"])
        return categories

    def save_all(self, categories: List[str]) -> None:
        # [보너스] 원자적 교체 쓰기 (Atomic write)
        temp_fd, temp_path = tempfile.mkstemp(dir=self.data_dir, text=True)
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            for cat in categories:
                f.write(json.dumps({"name": cat}, ensure_ascii=False) + "\n")
        os.replace(temp_path, self.file_path)

    def add(self, name: str) -> bool:
        cats = self.load_all()
        if name in cats:
            return False
        cats.append(name)
        self.save_all(cats)
        return True

    def remove(self, name: str) -> bool:
        cats = self.load_all()
        if name not in cats:
            return False
        cats.remove(name)
        self.save_all(cats)
        return True


class BudgetRepository(BaseRepository):
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.file_path = os.path.join(self.data_dir, "budgets.jsonl")
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass

    def load_all(self) -> Dict[str, int]:
        budgets = {}
        if not os.path.exists(self.file_path):
            return budgets
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    budgets[data["month"]] = data["amount"]
        return budgets

    def set_budget(self, month: str, amount: int) -> None:
        budgets = self.load_all()
        budgets[month] = amount
        
        temp_fd, temp_path = tempfile.mkstemp(dir=self.data_dir, text=True)
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            for m, a in budgets.items():
                f.write(json.dumps({"month": m, "amount": a}, ensure_ascii=False) + "\n")
        os.replace(temp_path, self.file_path)

    def get_budget(self, month: str) -> Optional[int]:
        budgets = self.load_all()
        return budgets.get(month)


class TransactionRepository(BaseRepository):
    def __init__(self, data_dir: str):
        super().__init__(data_dir)
        self.file_path = os.path.join(self.data_dir, "transactions.jsonl")
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                pass

    def stream_all(self) -> Generator[Transaction, None, None]:
        """제너레이터를 활용해 한 줄씩 스트리밍 처리"""
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    yield Transaction(
                        id=data["id"],
                        type=data["type"],
                        date=data["date"],
                        amount=data["amount"],
                        category=data["category"],
                        memo=data.get("memo", ""),
                        tags=data.get("tags", [])
                    )

    def append(self, tx: Transaction) -> None:
        tx.validate()
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(tx.__dict__, ensure_ascii=False) + "\n")

    def overwrite_all(self, transactions: List[Transaction]) -> None:
        """[보너스] 원자적 교체 방식을 적용한 전체 데이터 재작성"""
        temp_fd, temp_path = tempfile.mkstemp(dir=self.data_dir, text=True)
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            for tx in transactions:
                f.write(json.dumps(tx.__dict__, ensure_ascii=False) + "\n")
        os.replace(temp_path, self.file_path)

    def generate_next_id(self) -> str:
        max_num = 0
        for tx in self.stream_all():
            if tx.id.startswith("TX-"):
                try:
                    num = int(tx.id.split("-")[1])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"TX-{max_num + 1:06d}"