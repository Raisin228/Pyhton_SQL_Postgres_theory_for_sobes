# Передавать контроль управления
# Менеджер управления, куда и передаётся контроль управления => событийный цикл

# callback, corutine, async | await

import socket
from select import select

tasks = []  # список задач с генераторами
to_read = {}
to_write = {}


def server():
    # Инициализация серверного сокета
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 5002))
    server_socket.listen()

    while True:
        # Отдали управление, до тех пор пока не получим событие
        yield "read", server_socket
        # Подключиться мы сможем как только придёт клиентское соединение
        client_socket, addr = server_socket.accept()  # read
        print("Connection from", addr)
        # Среди списка задач будет клиентское соединение
        tasks.append(client(client_socket))


def client(client_socket):
    while True:
        yield "read", client_socket
        # Сюда мы попадём только тогда, когда как клиент получит данные на запись
        request = client_socket.recv(4096)  # read

        # Запроса нет - клиент отвалился
        if not request:
            break
        else:
            response = "Hello world\n".encode()
            # Отдаём управление до тех пор пока сокет не будет готов к записи.
            yield "write", client_socket
            # Буфер готов к записи - делаем отправку
            client_socket.send(response)  # write
    # Закрываем соединение после того как клиент отвалился
    client_socket.close()


def event_loop():
    """Здесь программа крутится"""
    while any([tasks, to_read, to_write]):

        while not tasks:
            # Когда мы, первый раз добавили сервер в список задач на чтение
            # фактически программа замирает и ждёт ответа от ОС. Пока кто-то
            # подключится на сокет.
            ready_to_read, ready_to_write, _ = select(to_read, to_write, [])
            # Можно сказать что select следит за всеми сокетами на чтение

            # Когда я замечаю что с сокетом связались -> возвращаю его в задачи.
            for sock in ready_to_read:
                tasks.append(to_read.pop(sock))

            # Если нашли сокет готовый работать на запись -> возвращаемся в связную задачу.
            for sock in ready_to_write:
                tasks.append(to_write.pop(sock))

        # Достаю задачу -> прогоняю
        try:
            # в задаче всегда лежит генератор
            task = tasks.pop(0)
            reason, sock = next(task)
            # в разные списки отправляем разные состояния сокетов
            if reason == "read":
                to_read[sock] = task
            if reason == "write":
                to_write[sock] = task
        # Когда генератор полностью завершился
        except StopIteration:
            print("Done!")


if __name__ == "__main__":
    tasks.append(server())
    event_loop()

# для реализации нам нужно:
# - определить какие сокеты готовы для чтения и записи => select
# - механизм переключения между клиентским и серверным сокетом

# server_socket готов - есть новое подключение
# client_socket готов - есть данные для подключения
# client_socket готов к write - есть для отправки
