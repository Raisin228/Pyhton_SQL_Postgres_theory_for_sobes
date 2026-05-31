import re
import time
from dataclasses import dataclass

from playwright.sync_api import Playwright, sync_playwright

COVER_LETTER = """Привет

Мой ТГ: @BogdanAtroshenko

Меня зовут Богдан, я AI/ML Engineer с 3+ годами коммерческого опыта разработки AI-сервисов и агентных систем на базе LLM.

На последнем месте работы (ООО Тензор) реализовал RAG-based систему для поиска по внутренним базам знаний: retrieval pipeline с chunking + embedding + semantic search, оркестрацию агентов на LangGraph. Поддерживал FastAPI-бэкенд AI-сервисов с асинхронной обработкой запросов и интеграцией с PostgreSQL. Снижал hallucination rate через оптимизацию промптов и chunking-стратегий.

До этого 2 года разрабатывал Python Backend в стартап-студии: проектировал REST API с нуля, внедрял TDD + GitLab CI/CD (покрытие до 51%), снизил latency с 4602 мс до 324 мс через Redis-кэширование.

Стек: Python, LangChain, LangGraph, RAG, FastAPI, PostgreSQL, asyncio, Docker, Pytest.

Хочу пособеседоваться к вам) Готов к тестовому заданию и техническому интервью. Буду рад обсудить детали!

Жду ответа, желательно в тг)"""


# -------------------- МОДЕЛИ --------------------

@dataclass(frozen=True)
class Vacancy:
    vacancy_id: str
    title: str
    watchers_text: str
    watchers_count: int | None


def _parse_int(text: str) -> int | None:
    if not text:
        return None
    text = text.replace("\xa0", " ")
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None


# -------------------- SERP: ПРОГРУЗКА --------------------

def scroll_until_all_loaded(page, pause_ms: int = 900, max_scrolls: int = 50, stable_rounds_needed: int = 3) -> None:
    cards = page.locator('[data-qa="vacancy-serp__vacancy"]')
    stable = 0
    prev = cards.count()

    print(f"Начинаю прогрузку скроллом. Сейчас карточек: {prev}")

    for i in range(1, max_scrolls + 1):
        # Скроллим к последней карточке — остаёмся в зоне ленты, не уходим в подвал
        page.evaluate("""
            const cards = document.querySelectorAll('[data-qa="vacancy-serp__vacancy"]');
            if (cards.length > 0) {
                cards[cards.length - 1].scrollIntoView({block: 'center', behavior: 'instant'});
            } else {
                window.scrollTo(0, document.body.scrollHeight);
            }
        """)
        page.wait_for_timeout(pause_ms)
        page.wait_for_timeout(int(pause_ms * 0.6))

        cur = cards.count()
        if cur > prev:
            print(f"  Скролл {i}: +{cur - prev} (стало {cur})")
            prev = cur
            stable = 0
        else:
            stable += 1
            print(f"  Скролл {i}: новых нет (стало {cur}), стабильность {stable}/{stable_rounds_needed}")
            if stable >= stable_rounds_needed:
                break

    print(f"Прогрузка завершена. Итого карточек: {prev}")


# -------------------- SERP: ПАРСИНГ --------------------

def collect_vacancies_for_apply(page, limit: int = 10) -> list[Vacancy]:
    page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=30_000)
    cards = page.locator('[data-qa="vacancy-serp__vacancy"]')

    result: list[Vacancy] = []
    for i in range(cards.count()):
        card = cards.nth(i)

        # есть кнопка "Откликнуться" в карточке?
        resp = card.locator('[data-qa="vacancy-serp__vacancy_response"]').first
        if resp.count() == 0:
            continue

        title = card.locator('[data-qa="serp-item__title-text"]').first.inner_text().strip()
        href = card.locator('a[data-qa="serp-item__title"]').first.get_attribute("href") or ""
        m = re.search(r"/vacancy/(\d+)", href)
        if not m:
            continue
        vacancy_id = m.group(1)

        watchers_loc = card.locator('span:has-text("Сейчас смотрят")').first
        watchers_text = watchers_loc.inner_text().strip() if watchers_loc.count() else "Сейчас смотрят —"
        watchers_count = _parse_int(watchers_text)

        result.append(Vacancy(vacancy_id=vacancy_id, title=title, watchers_text=watchers_text, watchers_count=watchers_count))
        if len(result) >= limit:
            break

    return result


def find_card_by_vacancy_id(page, vacancy_id: str):
    return page.locator(
        '[data-qa="vacancy-serp__vacancy"]',
        has=page.locator(f'a[data-qa="serp-item__title"][href*="/vacancy/{vacancy_id}"]'),
    ).first


# -------------------- ТЕСТ/ВОПРОСЫ (РЕДИРЕКТ) --------------------

def is_test_page(page) -> bool:
    """
    Детект "вопросов работодателя":
      - data-qa="title-container"
      - data-qa="title-description" содержит "Для отклика необходимо ответить..."
    """
    container = page.locator('[data-qa="title-container"]').first
    if container.count() == 0:
        return False

    desc = page.locator('[data-qa="title-description"]:has-text("Для отклика необходимо ответить")').first
    return desc.count() > 0


def safe_go_back_to_serp(page, fallback_url: str) -> None:
    """
    ВАЖНО: networkidle на HH часто не наступает, поэтому ждём выдачу селектором.
    """
    try:
        page.go_back(wait_until="domcontentloaded")
    except Exception:
        page.goto(fallback_url, wait_until="domcontentloaded")

    # ждём возвращение выдачи
    page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=15_000)


# -------------------- МОДАЛКА ОТКЛИКА С ПИСЬМОМ --------------------

def is_response_modal_with_letter(page) -> bool:
    """Открылась модалка отклика с полем для сопроводительного письма."""
    dlg = page.locator('[role="dialog"]').first
    if dlg.count() == 0:
        return False
    return dlg.locator('[data-qa="vacancy-response-popup-form-letter-input"]').count() > 0


def fill_and_submit_cover_letter(page, letter_text: str) -> bool:
    dlg = page.locator('[role="dialog"]').first
    if dlg.count() == 0:
        return False

    letter_input = dlg.locator('[data-qa="vacancy-response-popup-form-letter-input"]').first
    if letter_input.count() == 0:
        return False

    letter_input.click()
    letter_input.fill(letter_text)

    submit_btn = dlg.locator('[data-qa="vacancy-response-submit-popup"]').first
    if submit_btn.count() == 0:
        return False

    try:
        # Кнопка disabled пока поле пустое — ждём активации React-состояния
        submit_btn.wait_for(state="enabled", timeout=5_000)
        submit_btn.click(timeout=10_000)
        return True
    except Exception:
        return False


def close_response_modal_if_open(page) -> None:
    close_btn = page.locator('[data-qa="response-popup-close"]').first
    if close_btn.count():
        close_btn.click()
        try:
            page.locator('[role="dialog"]').first.wait_for(state="hidden", timeout=5000)
        except Exception:
            pass


# -------------------- СКРЫТИЕ ВАКАНСИИ --------------------

def hide_vacancy_card(page, card, *, timeout_ms: int = 5000) -> bool:
    """
    1) В карточке: button[data-qa="vacancy__blacklist-show-add"]
    2) В меню:    button[data-qa="vacancy__blacklist-menu-add-vacancy"]
    """
    hide_icon = card.locator('button[data-qa="vacancy__blacklist-show-add"]').first
    if hide_icon.count() == 0:
        return False

    card.scroll_into_view_if_needed(timeout=timeout_ms)

    try:
        hide_icon.click(timeout=timeout_ms)
    except Exception:
        return False

    menu_item = page.locator('button[data-qa="vacancy__blacklist-menu-add-vacancy"]').first
    try:
        menu_item.wait_for(state="visible", timeout=timeout_ms)
        menu_item.click(timeout=timeout_ms)
    except Exception:
        return False

    # иногда карточка реально удаляется из DOM
    try:
        card.wait_for(state="detached", timeout=3000)
    except Exception:
        pass

    return True


# -------------------- ОТКЛИК "В ОДИН КЛИК" --------------------

def click_apply_on_card(page, card, *, poll_timeout_sec: float = 6.0) -> str:
    """
    Возвращаем:
      - sent
      - test_required
      - cover_letter_required
      - extra_steps
      - unknown
    """
    original_url = page.url

    apply_btn = card.locator('[data-qa="vacancy-serp__vacancy_response"]').first
    if apply_btn.count() == 0:
        return "no_apply_button"

    # Центрируем кнопку в viewport через JS — иначе sticky-шапка/подвал перекрывает её
    apply_btn.evaluate("el => el.scrollIntoView({block: 'center', behavior: 'instant'})")
    page.wait_for_timeout(300)
    apply_btn.click()

    deadline = time.time() + poll_timeout_sec
    while time.time() < deadline:
        # 1) snackbar успеха
        if (page.locator('[data-qa="vacancy-response-success-standard-notification"]').count() or
                page.locator('#dialog-description:has-text("Отклик отправлен")').count()):
            return "sent"

        # 2) модалка отклика с полем письма — заполняем и отправляем
        if is_response_modal_with_letter(page):
            if fill_and_submit_cover_letter(page, COVER_LETTER):
                return "sent_with_letter"
            close_response_modal_if_open(page)
            return "cover_letter_required"

        # 3) редирект на доп.страницу (вопросы/тест)
        if page.url != original_url:
            if is_test_page(page):
                safe_go_back_to_serp(page, fallback_url=original_url)
                return "test_required"

            safe_go_back_to_serp(page, fallback_url=original_url)
            return "extra_steps"

        page.wait_for_timeout(200)

    return "unknown"


# -------------------- ПАГИНАЦИЯ --------------------

def go_to_next_page(page) -> bool:
    """Кликает «следующая страница». Возвращает False если кнопки нет."""
    next_btn = page.locator('[data-qa="pager-next"]').first
    if next_btn.count() == 0:
        return False
    next_btn.evaluate("el => el.scrollIntoView({block: 'center', behavior: 'instant'})")
    page.wait_for_timeout(300)
    next_btn.click()
    page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=15_000)
    return True


# -------------------- MAIN --------------------

def _apply_one(page, idx: int, total: int, v: "Vacancy") -> None:
    w = v.watchers_count if v.watchers_count is not None else "—"
    print(f"\n[{idx}/{total}] {v.title}")
    print(f"    Сейчас смотрят: {w}")

    card = find_card_by_vacancy_id(page, v.vacancy_id)
    if card.count() == 0:
        print("    ⚠️ Карточка не найдена. Пропускаю.")
        return

    status = click_apply_on_card(page, card)

    if status in ("sent", "sent_with_letter"):
        suffix = " (с письмом)" if status == "sent_with_letter" else ""
        print(f"    ✅ Отклик отправлен{suffix}.")
        return

    card_again = find_card_by_vacancy_id(page, v.vacancy_id)
    if card_again.count() > 0:
        hidden = hide_vacancy_card(page, card_again)
        print("    🫥 Скрыта." if hidden else "    ⚠️ Не удалось скрыть.")
    else:
        print("    ⚠️ Карточку для скрытия не нашёл.")

    msgs = {
        "test_required": "🧠 Требуется тест — пропуск.",
        "cover_letter_required": "✍️ Не удалось заполнить письмо — пропуск.",
        "extra_steps": "ℹ️ Нужны доп.шаги — пропуск.",
    }
    print(f"    {msgs.get(status, f'❓ Статус: {status} — пропуск.')}")


def run(playwright: Playwright, total_limit: int = 50) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://hh.ru/", wait_until="domcontentloaded")

    input("Залогиньтесь в браузере на hh.ru, затем нажмите Enter...")

    search_query = "Python developer"
    encoded = search_query.replace(" ", "+")
    print(f"Ищем: {search_query}")
    page.goto(f"https://hh.ru/search/vacancy?text={encoded}&area=113", wait_until="domcontentloaded")
    page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=30_000)

    applied_total = 0
    page_num = 1

    while applied_total < total_limit:
        print(f"\n{'='*50}")
        print(f"Страница {page_num}. Откликнулись всего: {applied_total}/{total_limit}")
        print('='*50)

        scroll_until_all_loaded(page)
        remaining = total_limit - applied_total
        vacancies = collect_vacancies_for_apply(page, limit=remaining)

        if not vacancies:
            print("Нет вакансий с кнопкой «Откликнуться» на этой странице.")
        else:
            print(f"Найдено {len(vacancies)} вакансий для отклика:")
            for i, v in enumerate(vacancies, 1):
                w = v.watchers_count if v.watchers_count is not None else "—"
                print(f"  {i:02d}. {v.title} | смотрят: {w}")

            for i, v in enumerate(vacancies, 1):
                _apply_one(page, applied_total + i, total_limit, v)

            applied_total += len(vacancies)

        if applied_total >= total_limit:
            break

        if not go_to_next_page(page):
            print("\nСледующей страницы нет — конец выдачи.")
            break

        page_num += 1

    print(f"\nГотово. Всего обработано вакансий: {applied_total}")
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        run(p)