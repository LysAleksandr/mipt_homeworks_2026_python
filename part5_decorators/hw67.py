import datetime
import functools
import json
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


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

    def __call__(self, fn: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        fn_full = f"{fn.__module__}.{fn.__name__}"

        @functools.wraps(fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> R_co:
            self._check_blocked(fn_full)

            try:
                result = fn(*args, **kwargs)
            except self._triggers_on as exc:
                return self._on_failure(exc, fn_full)
            else:
                self._failures = 0
                return result

        return wrapped

    def _check_blocked(self, fn_full: str) -> None:
        if self._block_until is None:
            return

        now = datetime.datetime.now(datetime.UTC)
        if now >= self._block_until:
            self._failures = 0
            self._block_until = None
            return

        raise BreakerError(fn_full, now)

    def _on_failure(self, exc: Exception, fn_full: str) -> None:
        self._failures += 1
        if self._failures < self._critical:
            raise exc

        block_time = datetime.datetime.now(datetime.UTC)
        self._block_until = block_time + datetime.timedelta(seconds=self._recovery)
        self._failures = 0
        raise BreakerError(fn_full, block_time, exc) from exc


circuit_breaker = CircuitBreaker(5, 30, Exception)


def get_comments(post_id: int) -> Any:
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
