import argparse
from typing import List
from .service import BudgetService
from .models import RecurringRule
from .formatter import format_table
from .decorators import handle_errors, measure_time

@handle_errors
@measure_time
def main() -> None:
    parser = argparse.ArgumentParser(prog="python3 -m budget_app", description="콘솔 가계부 프로그램")
    parser.add_argument("--data-dir", default="./data", help="데이터 저장 디렉토리 (기본값: ./data)")
    
    subparsers = parser.add_subparsers(dest="command", help="실행할 명령")

    # 1. add
    subparsers.add_parser("add", help="대화형으로 거래 내역 추가")

    # 2. list
    list_parser = subparsers.add_parser("list", help="거래 내역 목록 조회")
    list_parser.add_argument("--limit", type=int, default=10, help="출력할 개수 제한")

    # 3. search
    search_parser = subparsers.add_parser("search", help="조건별 거래 검색")
    search_parser.add_argument("--from", dest="from_date", help="시작일 (YYYY-MM-DD)")
    search_parser.add_argument("--to", dest="to_date", help="종료일 (YYYY-MM-DD)")
    search_parser.add_argument("--category", help="카테고리")
    search_parser.add_argument("--type", choices=["income", "expense"], help="타입")
    search_parser.add_argument("-q", dest="query", help="메모 검색어")
    search_parser.add_argument("--tag", help="태그")

    # 4. summary
    summary_parser = subparsers.add_parser("summary", help="월별 요약 리포트")
    summary_parser.add_argument("--month", required=True, help="조회 월 (YYYY-MM)")
    summary_parser.add_argument("--top", type=int, default=3, help="지출 카테고리 TOP N")

    # 5. budget
    budget_parser = subparsers.add_parser("budget", help="예산 설정")
    budget_sub = budget_parser.add_subparsers(dest="budget_action")
    budget_set = budget_sub.add_parser("set", help="월 예산 설정")
    budget_set.add_argument("--month", required=True, help="월 (YYYY-MM)")
    budget_set.add_argument("--amount", type=int, required=True, help="예산 금액")

    # 6. category
    cat_parser = subparsers.add_parser("category", help="카테고리 관리")
    cat_sub = cat_parser.add_subparsers(dest="cat_action")
    cat_sub.add_parser("list", help="카테고리 목록 조회")
    cat_add = cat_sub.add_parser("add", help="카테고리 추가")
    cat_add.add_argument("--name", help="추가할 카테고리명 (미입력시 대화형)")
    cat_rem = cat_sub.add_parser("remove", help="카테고리 삭제")
    cat_rem.add_argument("--name", required=True, help="삭제할 카테고리명")
    cat_rem.add_argument("--fallback", help="사용 중일 경우 대체할 카테고리명")

    # 7. update
    update_parser = subparsers.add_parser("update", help="거래 수정 (대화형 입력)")
    update_parser.add_argument("--id", required=True, help="수정할 거래 ID")

    # 8. delete
    delete_parser = subparsers.add_parser("delete", help="거래 삭제")
    delete_parser.add_argument("--id", required=True, help="삭제할 거래 ID")

    # 9. import / export
    import_parser = subparsers.add_parser("import", help="CSV 데이터 가져오기")
    import_parser.add_argument("--from", dest="from_file", required=True, help="가져올 CSV 파일 경로")

    export_parser = subparsers.add_parser("export", help="CSV 데이터 내보내기")
    export_parser.add_argument("--out", required=True, help="내보낼 CSV 파일 경로")
    export_parser.add_argument("--month", help="내보낼 월 (YYYY-MM)")
    export_parser.add_argument("--from", dest="from_date", help="시작일 (YYYY-MM-DD)")
    export_parser.add_argument("--to", dest="to_date", help="종료일 (YYYY-MM-DD)")

    # [보너스] 10. backup
    subparsers.add_parser("backup", help="타임스탬프 백업 파일 생성")

    # [보너스] 11. recurring
    rec_parser = subparsers.add_parser("recurring", help="반복 내역 자동 생성")
    rec_parser.add_argument("--month", required=True, help="생성할 월 (YYYY-MM)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    service = BudgetService(data_dir=args.data_dir)

    if args.command == "add":
        date = input("날짜(YYYY-MM-DD): ").strip()
        tx_type = input("타입(income/expense): ").strip()
        category = input("카테고리: ").strip()
        amount_str = input("금액(양수): ").strip()
        if not amount_str.isdigit():
            raise ValueError("금액은 숫자만 입력 가능합니다.")
        memo = input("메모(선택): ").strip()
        tags_raw = input("태그(쉼표로 구분, 없으면 엔터): ").strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

        tx_id = service.add_transaction(date, tx_type, category, int(amount_str), memo, tags)
        print(f"[저장 완료] id={tx_id}")

    elif args.command == "list":
        txs = service.list_transactions(limit=args.limit)
        if not txs:
            print("등록된 거래 내역이 없습니다.")
        else:
            headers = ["ID", "날짜", "타입", "카테고리", "금액", "메모"]
            rows = [[tx.id, tx.date, tx.type, tx.category, f"{tx.amount:,}원", tx.memo] for tx in txs]
            print(format_table(headers, rows))

    elif args.command == "search":
        txs = service.search_transactions(
            from_date=args.from_date,
            to_date=args.to_date,
            category=args.category,
            tx_type=args.type,
            query=args.query,
            tag=args.tag
        )
        if not txs:
            print("검색 조건에 맞는 내역이 없습니다.")
        else:
            headers = ["ID", "날짜", "타입", "카테고리", "금액", "메모"]
            rows = [[tx.id, tx.date, tx.type, tx.category, f"{tx.amount:,}원", tx.memo] for tx in txs]
            print(format_table(headers, rows))

    elif args.command == "summary":
        res = service.get_summary(month=args.month, top_n=args.top)
        if not res["has_data"]:
            print(f"[{args.month}] 해당 월의 데이터가 없습니다.")
            return

        print(f"총 수입: {res['total_income']:,}원")
        print(f"총 지출: {res['total_expense']:,}원")
        print(f"잔액: {res['balance']:,}원")

        if res["budget"] is not None:
            budget = res["budget"]
            usage_pct = (res["total_expense"] / budget * 100) if budget > 0 else 0.0
            print(f"예산: {budget:,}원 (사용률 {usage_pct:.1f}%)")
            if res["total_expense"] > budget:
                print(f"[경고] 예산을 {res['total_expense'] - budget:,}원 초과했습니다!")

        print(f"\n지출 TOP {args.top}")
        for idx, (cat, amt) in enumerate(res["top_categories"], 1):
            print(f"{idx}) {cat} {amt:,}원")

    elif args.command == "budget":
        if args.budget_action == "set":
            service.set_budget(args.month, args.amount)
            print(f"[저장 완료] {args.month} 예산 {args.amount:,}원")
        else:
            parser.parse_args(["budget", "--help"])

    elif args.command == "category":
        if args.cat_action == "list":
            cats = service.list_categories()
            for c in cats:
                print(c)
        elif args.cat_action == "add":
            name = args.name or input("카테고리명: ").strip()
            if service.add_category(name):
                print(f"[저장 완료] category={name}")
            else:
                print(f"[안내] 이미 존재하는 카테고리입니다: {name}")
        elif args.cat_action == "remove":
            service.remove_category(args.name, args.fallback)
            print(f"[삭제 완료] category={args.name}")
        else:
            parser.parse_args(["category", "--help"])

    elif args.command == "update":
        print(f"[{args.id}] 수정할 항목만 입력하세요. (변경하지 않으려면 엔터)")
        date = input("날짜(YYYY-MM-DD): ").strip() or None
        tx_type = input("타입(income/expense): ").strip() or None
        category = input("카테고리: ").strip() or None
        amount_raw = input("금액(양수): ").strip()
        amount = int(amount_raw) if amount_raw else None
        memo = input("메모: ").strip() or None
        tags_raw = input("태그(쉼표 구분): ").strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else None

        success = service.update_transaction(
            tx_id=args.id,
            date=date,
            tx_type=tx_type,
            category=category,
            amount=amount,
            memo=memo,
            tags=tags
        )
        if success:
            print(f"[수정 완료] id={args.id}")
        else:
            print(f"[오류] 해당 ID의 거래를 찾을 수 없습니다: {args.id}")

    elif args.command == "delete":
        if service.delete_transaction(args.id):
            print(f"[삭제 완료] id={args.id}")
        else:
            print(f"[오류] 해당 ID의 거래를 찾을 수 없습니다: {args.id}")

    elif args.command == "export":
        count = service.export_csv(
            out_path=args.out,
            month=args.month,
            from_date=args.from_date,
            to_date=args.to_date
        )
        print(f"[완료] {args.out} ({count} records)")

    elif args.command == "import":
        imported, skipped = service.import_csv(args.from_file)
        print(f"[완료] imported={imported}, skipped={skipped}")

    elif args.command == "backup":
        backup_path = service.create_backup()
        print(f"[백업 완료] 저장 위치: {backup_path}")

    elif args.command == "recurring":
        # 예시 반복 규칙 (필요시 추가)
        default_rules = [
            RecurringRule(type="income", category="salary", amount=3000000, day=10, memo="월급"),
            RecurringRule(type="expense", category="rent", amount=500000, day=25, memo="월세")
        ]
        created = service.generate_recurring_transactions(args.month, default_rules)
        print(f"[완료] {args.month}월 반복 내역 {created}건 생성 완료")