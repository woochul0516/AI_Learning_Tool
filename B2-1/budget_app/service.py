import csv
import os
import shutil
from datetime import datetime
from typing import List, Generator, Optional, Dict, Any
from .models import Transaction, Budget, RecurringRule
from .repository import TransactionRepository, CategoryRepository, BudgetRepository

class BudgetService:
    def __init__(self, data_dir: str = "./data"):
        self.tx_repo = TransactionRepository(data_dir)
        self.cat_repo = CategoryRepository(data_dir)
        self.budget_repo = BudgetRepository(data_dir)

    def add_transaction(self, date: str, tx_type: str, category: str, amount: int, memo: str, tags: List[str]) -> str:
        categories = self.cat_repo.load_all()
        if category not in categories:
            raise ValueError(f"존재하지 않는 카테고리입니다: '{category}'. 등록된 카테고리: {', '.join(categories)}")

        tx_id = self.tx_repo.generate_next_id()
        tx = Transaction(
            id=tx_id,
            type=tx_type,  # type: ignore
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags
        )
        self.tx_repo.append(tx)
        return tx_id

    def list_transactions(self, limit: Optional[int] = None) -> List[Transaction]:
        all_tx = list(self.tx_repo.stream_all())
        all_tx.sort(key=lambda x: (x.date, x.id), reverse=True)
        if limit is not None and limit > 0:
            return all_tx[:limit]
        return all_tx

    def search_transactions(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        category: Optional[str] = None,
        tx_type: Optional[str] = None,
        query: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Transaction]:
        results = []
        for tx in self.tx_repo.stream_all():
            if from_date and tx.date < from_date:
                continue
            if to_date and tx.date > to_date:
                continue
            if category and tx.category != category:
                continue
            if tx_type and tx.type != tx_type:
                continue
            if query and query.lower() not in tx.memo.lower():
                continue
            if tag and tag not in tx.tags:
                continue
            results.append(tx)

        results.sort(key=lambda x: (x.date, x.id), reverse=True)
        return results

    def get_summary(self, month: str, top_n: int = 3) -> Dict[str, Any]:
        total_income = 0
        total_expense = 0
        cat_expenses: Dict[str, int] = {}
        has_data = False

        for tx in self.tx_repo.stream_all():
            if tx.date.startswith(month):
                has_data = True
                if tx.type == "income":
                    total_income += tx.amount
                elif tx.type == "expense":
                    total_expense += tx.amount
                    cat_expenses[tx.category] = cat_expenses.get(tx.category, 0) + tx.amount

        if not has_data:
            return {"has_data": False, "month": month}

        sorted_cats = sorted(cat_expenses.items(), key=lambda x: x[1], reverse=True)[:top_n]
        budget = self.budget_repo.get_budget(month)

        return {
            "has_data": True,
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "top_categories": sorted_cats,
            "budget": budget
        }

    def set_budget(self, month: str, amount: int) -> None:
        b = Budget(month=month, amount=amount)
        b.validate()
        self.budget_repo.set_budget(month, amount)

    def add_category(self, name: str) -> bool:
        return self.cat_repo.add(name)

    def list_categories(self) -> List[str]:
        return self.cat_repo.load_all()

    def remove_category(self, name: str, fallback_category: Optional[str] = None) -> None:
        in_use = any(tx.category == name for tx in self.tx_repo.stream_all())
        if in_use:
            if not fallback_category:
                raise ValueError(f"카테고리 '{name}'은(는) 현재 거래 내역에서 사용 중입니다. 대체 카테고리를 지정해야 합니다.")
            categories = self.cat_repo.load_all()
            if fallback_category not in categories or fallback_category == name:
                raise ValueError(f"유효한 대체 카테고리가 아닙니다: '{fallback_category}'")
            
            all_tx = list(self.tx_repo.stream_all())
            for tx in all_tx:
                if tx.category == name:
                    tx.category = fallback_category
            self.tx_repo.overwrite_all(all_tx)

        if not self.cat_repo.remove(name):
            raise ValueError(f"존재하지 않는 카테고리입니다: '{name}'")

    def update_transaction(
        self,
        tx_id: str,
        date: Optional[str] = None,
        tx_type: Optional[str] = None,
        category: Optional[str] = None,
        amount: Optional[int] = None,
        memo: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        all_tx = list(self.tx_repo.stream_all())
        target_idx = -1
        for idx, tx in enumerate(all_tx):
            if tx.id == tx_id:
                target_idx = idx
                break

        if target_idx == -1:
            return False

        tx = all_tx[target_idx]
        if date:
            tx.date = date
        if tx_type:
            tx.type = tx_type  # type: ignore
        if category:
            categories = self.cat_repo.load_all()
            if category not in categories:
                raise ValueError(f"존재하지 않는 카테고리입니다: '{category}'")
            tx.category = category
        if amount is not None:
            tx.amount = amount
        if memo is not None:
            tx.memo = memo
        if tags is not None:
            tx.tags = tags

        tx.validate()
        self.tx_repo.overwrite_all(all_tx)
        return True

    def delete_transaction(self, tx_id: str) -> bool:
        all_tx = list(self.tx_repo.stream_all())
        new_tx = [tx for tx in all_tx if tx.id != tx_id]
        if len(all_tx) == len(new_tx):
            return False
        self.tx_repo.overwrite_all(new_tx)
        return True

    def export_csv(self, out_path: str, month: Optional[str] = None, from_date: Optional[str] = None, to_date: Optional[str] = None) -> int:
        if not month and not (from_date or to_date):
            raise ValueError("export 실행 시 --month 또는 (--from / --to) 조건이 필수입니다.")

        records = []
        for tx in self.tx_repo.stream_all():
            if month and not tx.date.startswith(month):
                continue
            if from_date and tx.date < from_date:
                continue
            if to_date and tx.date > to_date:
                continue
            records.append(tx)

        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "category", "amount", "memo", "tags"])
            for r in records:
                tags_str = ",".join(r.tags) if r.tags else ""
                writer.writerow([r.date, r.type, r.category, r.amount, r.memo, tags_str])

        return len(records)

    def import_csv(self, in_path: str) -> tuple[int, int]:
        imported = 0
        skipped = 0
        categories = set(self.cat_repo.load_all())

        with open(in_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    date = row["date"].strip()
                    tx_type = row["type"].strip()
                    category = row["category"].strip()
                    amount = int(row["amount"].strip())
                    memo = row.get("memo", "").strip()
                    tags_raw = row.get("tags", "").strip()
                    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

                    if category not in categories:
                        skipped += 1
                        continue

                    self.add_transaction(date, tx_type, category, amount, memo, tags)
                    imported += 1
                except Exception:
                    skipped += 1

        return imported, skipped

    # [보너스 1] 타임스탬프 백업 생성
    def create_backup(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.tx_repo.data_dir, f"backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        
        for filename in ["transactions.jsonl", "categories.jsonl", "budgets.jsonl"]:
            src = os.path.join(self.tx_repo.data_dir, filename)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_dir, filename))
                
        return backup_dir

    # [보너스 2] 반복 내역 자동 생성
    def generate_recurring_transactions(self, month: str, rules: List[RecurringRule]) -> int:
        created_count = 0
        existing_memos = {tx.memo for tx in self.tx_repo.stream_all() if tx.date.startswith(month)}
        
        for rule in rules:
            date_str = f"{month}-{rule.day:02d}"
            if rule.memo not in existing_memos:
                self.add_transaction(
                    date=date_str,
                    tx_type=rule.type,
                    category=rule.category,
                    amount=rule.amount,
                    memo=rule.memo,
                    tags=["자동생성", "반복내역"]
                )
                created_count += 1
        return created_count