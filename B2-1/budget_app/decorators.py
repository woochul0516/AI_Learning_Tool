import sys
import time
import functools
from typing import Callable, Any

def handle_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """예외 발생 시 스택트레이스를 감추고 원인과 힌트를 출력한 뒤 비정상 종료(exit 1) 처리하는 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"[오류] {e}", file=sys.stderr)
            print("[힌트] 입력값 형식이나 인자를 다시 확인해 주세요.", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"[오류] 파일을 찾을 수 없습니다: {e}", file=sys.stderr)
            print("[힌트] 파일 경로가 올바른지 확인해 주세요.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[오류] 예상치 못한 오류가 발생했습니다: {e}", file=sys.stderr)
            print("[힌트] 입력 데이터나 시스템 상태를 확인해 주세요.", file=sys.stderr)
            sys.exit(1)
    return wrapper

def measure_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """함수 실행 시간을 측정하는 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start_time
        return result
    return wrapper