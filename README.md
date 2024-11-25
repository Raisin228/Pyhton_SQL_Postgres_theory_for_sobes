**Подготовка к теоретической части собеседования [Python | SQL | Postgres]**

1) *Что такое SQL?*

-> SQL - стандартный язык, для взаимодействия с *реляционными* бд. Позволяет создавать и модифицировать структуру бд DDL
(Data Definition Language), управлять данными DML (Data Manipulation Language) и контролировать доступ к данным DCL
(Data Control Language).

Основные команды SQL:

* SELECT - для выборки данных
* INSERT - для вставки данных
* UPDATE - для изменения существующих записей
* DELETE - удаление записей
* CREATE TABLE - создание таблиц
* ALTER TABLE - изменение сущ. таблицы
* DROP TABLE - удаление таблицы

---

2) *В чем отличие между DDL, DML, DCL и TCL? Какие операции входят в каждую из групп?*

->

* **DDL (Data Definition Language)** - группа команд, которые используются для создания и изменения структуры объектов
  бд.
  Таких как: таблицы, представления и индексы.
  Наиболее известные команды: CREATE, ALTER, DROP.
* **DML (Data Manipulation Language)** - позволяет получать доступ к данным и манипулировать ими.
  Наиболее известные команды: SELECT, INSERT, UPDATE, DELETE.
* **DCL (Data Control Language)** - группа операций, которые используются для предоставления и отзыва привилегий
  пользователя бд.
  Наиболее известные: GRANT - предоставления доступа, REVOKE - отозвать ранее выданные права.
* **TCL (Transaction Control Language)** - используется для управления согласованностью данными и управления
  транзакциями.
  Наиболее частые команды: BEGIN/COMMIT - старт и фиксация изменений, ROLLBACK - откатывает изменения.

Транзакция - блок из нескольких SQL запросов, которые объединены в атомарную единицу. Либо все одновременно выполняются
либо отменяются в случае ошибки.

---

3) *Перечислите все типы связей таблиц в SQL.*
   ->

* **One-to-One** - связь, когда каждой записи из одной таблицы соответствует максимум одна запись из другой таблицы.
  В качестве примера: есть таблица сотрудники и таблица is_worker_student. Показывает, является ли сотрудник студентом.
  Необходимо чтоб внешний ключ из таблицы is_worker_student был уникальным. Ведь один сотрудник может быть студентом
  только 1 раз.
* **One-to-Many & Many-to-One** - одна запись в таблице связана с несколькими записями в другой таблице. Пример:
  Таблица пользователь и номера телефонов. У одного пользователя может быть *несколько* номеров, в то время
  как, номер может быть *только* у одного пользователя.
* **Many-to-Many** - связь, когда для определения отношения требуется несколько экзэмпляров с обеих сторон. Например:
  таблица сотрудников employer и должностей position. Работник может одновременно занимать несколько должностей
  (программист и администратор) в то же время в одной должности одновременно может находиться много сотрудников. Для
  описания такой связи необходимо заводить отдельную таблицу. [id, emp_id, position_id]
* **Self-Referencing Relationship** - тип связи, когда таблица ссылается на другую запись, находящуюся в ней самой.
  Обычно используется для иерархий. Например: сотрудник и его начальник (начальник это id другого пользователя в этой же
  таблице)

---

4) *Что такое СУБД?*
   -> СУБД - система управления базами данных. Программное обеспечение, которое взаимодействует с пользователем и самой
   бд для сбора и анализа данных. БД - это просто структурированные файлики с информацией на ПК. Сама БД не умеет
   ничего (быстро искать данные, делать сложные вычисления и т.д) без существования СУБД каждому разработчику
   самостоятельно с чистого листа пришлось бы прописывать всю эту логику.
   По своей сути СУБД это стандартизированный инструмент для более простой и эффективной работы с БД.

<u>Существует 2 типа СУБД:</u>

* Реляционные (PostgreSQL, MySQL) где данные хранятся в отношениях (таблицах).
* Нереляционные (Redis, MongoDB). Это документо ориентированные, графовые и ключ значение.

---

5) *В чем разница между базой данных и схемой?*
   -> БД - это хранилище данных, схема - это описание структуры этих данных. В SQL база данных - это набор связанных
   данных, которые хранятся в организованном структурированном виде. Обычно содержит несколько схем каждая из
   которых содержит свои таблицы, представления, процедуры и индексы.
   Схема позволяет логически сгруппировать связанные объекты и отделить их от других объектов. Что повышает
   безопасность, организованность и контроль доступа к данным.
   Пример: БД - это многоэтажный дом (панелька), который состоит из большого количества квартир (схем). Каждая квартира
   группирует связанных между собой людей (объекты бд) для повышения организованности, безопасности и контроля...

--- 

6) *Что такое нормализация и каковы ее преимущества?*
   -> Нормализация - это способ организации данных, цель избежать дублирования, избыточности и упростить организацию
   информации. В нормализованной базе нет повторяющихся данных, с ней проще работать и можно легко менять её структуру
   для разных задач. В процессе нормализации данные преобразуют, так чтоб они занимали меньше места, а поиск был быстрым
   и эффективным. Для этого создаются дополнительные таблицы, их в свою очередь связывают между собой.

<u>Преимущества</u>:

* Лучшая организация данных
* Таблицы меньших размеров
* Быстрый поиск информации
* Легко модифицировать
* Сокращение дублирования и избыточности данных
* Обеспечение согласованности данных после внесения изменений

---

7) *Какие уровни нормализации есть в SQL?*

<u>Существует 5 уровней нормализации БД:</u>

* *Первая нормальная форма.* Таблица находится в 1-ой нормальной форме если:
    - Каждый столбец содержит только атомарные (неделимые) значения
    - Нет дублирующихся строк
    - Нет повторяющися атрибутов с одинаковым смыслом
* *Вторая нормальная форма.*
    - Таблица находится в 1NF
    - Есть первичный ключ PK
    - Каждый неключевой столбец полностью функционально зависит от всего первичного ключа. Пример: есть таблица "Заказы"
      с полями "Идентификатор заказа", "Идентификатор товара", "Количество". Если "Идентификатор товара" и "Количество"
      зависят только от "Идентификатора заказа" тогда таблица во 2NF.
* *Третья нормальная форма.*
    - Таблица находится во 2NF
    - Каждый неключевой столбец не зависит от других неключевых столбцов, нет транзитивных (непрямых) зависимостей. Т.е
      неключевые атрибуты напрямую зависят только от PK.
* *Четвёртая нормальная форма.*
    - Таблица находится в 3NF
    - Устранены мультизависимости т.е если один ключ связан с несколькими независимыми наборами данных их следует
      разделить на отдельные таблицы. Пример: Student_id, course, hobby. Хобби и курс не зависят друг от друга.
      Следовательно следует разделить на 2 таблицы.
* *Пятая нормальная форма.*
    - Таблица находится в 4NF
    - Если несколько таблиц можно соединить в 1-у при помощи JOIN и нет избыточности и не теряется информация.

---

8) *В чем разница между типом данных CHAR и VARCHAR в SQL?*
   -> В CHAR хранятся строковые данные фиксированной длинны. Например если создать CHAR(5) и сохранить слово "cat" то
   оставшиеся символы будут заполнены space. В то время как VARCHAR(5) может хранить строку произвольной длины до 5
   символов.

---

9) *Как вычислить разницу между двумя датами в SQL?*
   -> select extract(day from 'DATE_A'::timestamp - 'DATE_B'::timestamp); Вроде как нет оператора DATEDIFF!
