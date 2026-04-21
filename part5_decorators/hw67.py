import functools
import json
import datetime
from urllib.request import urlopen
from typing import Any, Callable

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


class BreakerError(Exception):
    def __init__(
        self,
        func_name: str,
        block_time: datetime.datetime,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time
        if cause is not None:
            self.__cause__ = cause


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        errs: list[ValueError] = []
        if not isinstance(critical_count, int) or critical_count <= 0:
            errs.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errs.append(ValueError(INVALID_RECOVERY_TIME))
        if errs:
            raise ExceptionGroup(VALIDATIONS_FAILED, errs)

        self._critical = critical_count
        self._recovery = time_to_recover
        self._triggers_on = triggers_on
        self._failures = 0
        self._block_until: datetime.datetime | None = None

    def __call__(self, fn: Callable) -> Callable:
        fn_full = f"{fn.__module__}.{fn.__name__}"

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            now = datetime.datetime.now(datetime.UTC)

            if self._block_until is not None:
                if now < self._block_until:
                    raise BreakerError(fn_full, self._block_until - datetime.timedelta(seconds=self._recovery))
                self._failures = 0
                self._block_until = None

            try:
                result = fn(*args, **kwargs)
            except self._triggers_on as exc:
                self._failures += 1
                if self._failures >= self._critical:
                    block_start = datetime.datetime.now(datetime.UTC)
                    self._block_until = block_start + datetime.timedelta(seconds=self._recovery)
                    self._failures = 0
                    raise BreakerError(fn_full, block_start, exc) from exc
                raise
            else:
                self._failures = 0
                return result

        return wrapped


circuit_breaker = CircuitBreaker(5, 30, Exception)


def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
