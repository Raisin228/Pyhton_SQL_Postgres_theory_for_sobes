from functools import wraps


# Декоратор с параметрами. Делает n попыток для вызова ф-ии.
def retry(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for i in range(n):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as ex:
                    print(f"Попытка {i}. Произошла ошибка: {ex}")
            return result

        return wrapper

    return decorator


counter = 0


def my_func():
    global counter
    counter += 1
    print('works')
    if counter < 2:
        1 / 0
    return "Good"


# ret = retry(3)
# res = ret(my_func)
#
# print(res)

# ---

# Протокол итератора.
# __iter__; __next__
class MyRange:

    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration

        var = self.current
        self.current += 1
        return var


# a = MyRange(5)
# print(*[num for num in a], sep="\n")

# ---

# Контекстный менеджер
# __enter__; __exit__
class MyContext:

    def __enter__(self):
        print("Зашли в контекст")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Вышли из контекста")
        return self


# with MyContext() as context:
#     print('yes', context)

from contextlib import contextmanager


@contextmanager
def some_func():
    print("Что-то поделала интересное")
    yield
    print("После закрытия контекста")


# with some_func() as context:
#     print("Нет")

# ---

# Асинхронщина
import asyncio


async def work(i):
    await asyncio.sleep(i)
    print(i)


async def main():
    await asyncio.gather(  # параллельный запуск кучки задач
        work(1),
        work(2)
    )


# asyncio.run(main())


async def work2(i, s):
    async with s:
        print(f"Start {i}")
        await asyncio.sleep(1)
        print(f"End {i}")


async def main():
    sem = asyncio.Semaphore(5)
    await asyncio.gather(*(work2(i, sem) for i in range(100)))


asyncio.run(main())
