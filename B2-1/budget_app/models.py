import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Literal

TransactionType = Literal["income", "expense"]

@dataclass
class Transaction:
    id: str
    type: TransactionType
    date: str  # YYYY-MM-DD
    amount: int
    category: str
    memo: str = ""
    tags: List[str] = field(default_factory=list)

    def validate(self) -> None:
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"올바르지 않은 날짜 형식입니다 ({self.date}). YYYY-MM-DD 형식이어야 합니다.")
        
        if self.type not in ("income", "expense"):
            raise ValueError(f"타입은 'income' 또는 'expense'이어야 합니다. 입력값: {self.type}")
        
        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValueError(f"금액은 0보다 큰 양의 정수여야 합니다. 입력값: {self.amount}")

@dataclass
class Budget:
    month: str  # YYYY-MM
    amount: int

    def validate(self) -> None:
        try:
            datetime.strptime(self.month, "%Y-%m")
        except ValueError:
            raise ValueError(f"월 형식이 올바르지 않습니다 ({self.month}). YYYY-MM 형식이어야 합니다.")
        if self.amount < 0:
            raise ValueError("예산 금액은 0 이상이어야 합니다.")

# [보너스] 반복 내역 규칙 모델
@dataclass
class RecurringRule:
    type: TransactionType
    category: str
    amount: int
    day: int   # 생성 일자 (1~28)
    memo: str