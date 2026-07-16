# # from typing import List, Dict


# # class FIFAWorldCupParser:
# #     """Парсер расписания FIFA World Cup 2026 с Flashscore (этап 1)."""

# #     FIXTURES_URL = "https://www.flashscorekz.com/football/world/world-championship/fixtures/"

# #     @staticmethod
# #     def parse_fixtures_with_browser(page) -> List[Dict]:
# #         """Парсинг расписания через Playwright. Возвращает список матчей."""
# #         print("📄 Открываем страницу фикстур...")
# #         page.goto(FIFAWorldCupParser.FIXTURES_URL, wait_until="domcontentloaded")
# #         page.wait_for_timeout(5000)

# #         FIFAWorldCupParser._close_cookie_banner(page)

# #         matches_data = page.evaluate("""
# #             () => {
# #                 const matches = [];
# #                 const rows = document.querySelectorAll('.event__match');

# #                 rows.forEach(row => {
# #                     const link = row.querySelector('a.eventRowLink');
# #                     if (!link) return;

# #                     const url = link.href;
# #                     const midMatch = url.match(/[?&]mid=([a-zA-Z0-9]+)/);
# #                     const mid = midMatch ? midMatch[1] : '';

# #                     const homeEl = row.querySelector('.event__homeParticipant .wcl-name_jjfMf');
# #                     const awayEl = row.querySelector('.event__awayParticipant .wcl-name_jjfMf');

# #                     const homeScoreEl = row.querySelector('.event__score--home');
# #                     const awayScoreEl = row.querySelector('.event__score--away');

# #                     const timeEl = row.querySelector('.event__time');

# #                     const statusClasses = row.className;

# #                     matches.push({
# #                         url: url,
# #                         mid: mid,
# #                         homeTeam: homeEl ? homeEl.innerText.trim() : '',
# #                         awayTeam: awayEl ? awayEl.innerText.trim() : '',
# #                         homeScore: homeScoreEl ? homeScoreEl.innerText.trim() : '',
# #                         awayScore: awayScoreEl ? awayScoreEl.innerText.trim() : '',
# #                         time: timeEl ? timeEl.innerText.trim() : '',
# #                         statusClasses: statusClasses,
# #                     });
# #                 });

# #                 return matches;
# #             }
# #         """)

# #         print(f"🔗 Найдено матчей: {len(matches_data)}")

# #         matches = []
# #         for data in matches_data:
# #             match = {
# #                 "flashscore_id": data["mid"],
# #                 "match_url": data["url"],
# #                 "home_team": data["homeTeam"],
# #                 "away_team": data["awayTeam"],
# #                 "time_display": data["time"],
# #                 "status": FIFAWorldCupParser._parse_status(data["statusClasses"]),
# #             }

# #             home_score = data["homeScore"]
# #             away_score = data["awayScore"]
# #             if home_score.isdigit() and away_score.isdigit():
# #                 match["home_score"] = int(home_score)
# #                 match["away_score"] = int(away_score)

# #             matches.append(match)

# #         return matches

# #     # ------------------------------------------------------------------
# #     # Вспомогательные методы
# #     # ------------------------------------------------------------------

# #     @staticmethod
# #     def _extract_mid(url: str) -> str:
# #         """Извлекает mid из URL матча."""
# #         if "?mid=" in url:
# #             return url.split("?mid=")[-1]
# #         return ""

# #     @staticmethod
# #     def _parse_status(class_string: str) -> str:
# #         """Определяет статус матча по строке CSS-классов."""
# #         if "live" in class_string:
# #             return "live"
# #         if "finished" in class_string:
# #             return "finished"
# #         if "postponed" in class_string:
# #             return "postponed"
# #         return "scheduled"

# #     @staticmethod
# #     def _close_cookie_banner(page):
# #         """Закрывает баннер кук, если он есть."""
# #         cookie_selectors = [
# #             "#onetrust-accept-btn-handler",
# #             ".ot-sdk-container button",
# #             "[data-testid='cookie-policy-accept']",
# #             ".cookie-accept",
# #         ]
# #         for selector in cookie_selectors:
# #             try:
# #                 el = page.query_selector(selector)
# #                 if el and el.is_visible():
# #                     el.click()
# #                     page.wait_for_timeout(1000)
# #                     break
# #             except Exception:
# #                 continue


# from typing import List, Dict
# from datetime import datetime


# class FIFAWorldCupParser:
#     """Парсер FIFA World Cup 2026 с Flashscore: расписание (этап 1) + результаты/статистика (этап 2)."""

#     FIXTURES_URL = "https://www.flashscorekz.com/football/world/world-championship/fixtures/"

#     @staticmethod
#     def parse_fixtures_with_browser(page) -> List[Dict]:
#         """Парсинг расписания через Playwright. Возвращает список матчей."""
#         print("📄 Открываем страницу фикстур...")
#         page.goto(FIFAWorldCupParser.FIXTURES_URL, wait_until="domcontentloaded")
#         page.wait_for_timeout(5000)

#         FIFAWorldCupParser._close_cookie_banner(page)

#         matches_data = page.evaluate("""
#             () => {
#                 const matches = [];
#                 const rows = document.querySelectorAll('.event__match');

#                 rows.forEach(row => {
#                     const link = row.querySelector('a.eventRowLink');
#                     if (!link) return;

#                     const url = link.href;
#                     const midMatch = url.match(/[?&]mid=([a-zA-Z0-9]+)/);
#                     const mid = midMatch ? midMatch[1] : '';

#                     const homeEl = row.querySelector('.event__homeParticipant .wcl-name_jjfMf');
#                     const awayEl = row.querySelector('.event__awayParticipant .wcl-name_jjfMf');

#                     const homeScoreEl = row.querySelector('.event__score--home');
#                     const awayScoreEl = row.querySelector('.event__score--away');

#                     const timeEl = row.querySelector('.event__time');

#                     const statusClasses = row.className;

#                     matches.push({
#                         url: url,
#                         mid: mid,
#                         homeTeam: homeEl ? homeEl.innerText.trim() : '',
#                         awayTeam: awayEl ? awayEl.innerText.trim() : '',
#                         homeScore: homeScoreEl ? homeScoreEl.innerText.trim() : '',
#                         awayScore: awayScoreEl ? awayScoreEl.innerText.trim() : '',
#                         time: timeEl ? timeEl.innerText.trim() : '',
#                         statusClasses: statusClasses,
#                     });
#                 });

#                 return matches;
#             }
#         """)

#         print(f"🔗 Найдено матчей: {len(matches_data)}")

#         matches = []
#         for data in matches_data:
#             match = {
#                 "flashscore_id": data["mid"],
#                 "match_url": data["url"],
#                 "home_team": data["homeTeam"],
#                 "away_team": data["awayTeam"],
#                 "time_display": data["time"],
#                 "status": FIFAWorldCupParser._parse_status(data["statusClasses"]),
#             }

#             home_score = data["homeScore"]
#             away_score = data["awayScore"]
#             if home_score.isdigit() and away_score.isdigit():
#                 match["home_score"] = int(home_score)
#                 match["away_score"] = int(away_score)

#             matches.append(match)

#         return matches

#     @staticmethod
#     def parse_match_details_with_browser(page, match_url: str) -> Dict:
#         """
#         Парсинг детальной страницы матча: дата, команды, счёт, статус, стадион.
#         Используется на этапе 2 для обновления результатов.
#         """
#         print(f"📄 Открываем детали матча: {match_url}")
#         page.goto(match_url, wait_until="domcontentloaded")
#         page.wait_for_timeout(3000)

#         details = page.evaluate("""
#             () => {
#                 const data = {};

#                 const timeEl = document.querySelector('.duelParticipant__startTime div');
#                 if (timeEl) data.matchDate = timeEl.innerText.trim();

#                 const homeEl = document.querySelector('.duelParticipant__home .participant__participantName a');
#                 if (homeEl) data.homeTeam = homeEl.innerText.trim();

#                 const awayEl = document.querySelector('.duelParticipant__away .participant__participantName a');
#                 if (awayEl) data.awayTeam = awayEl.innerText.trim();

#                 const wrapper = document.querySelector('.detailScore__wrapper');
#                 if (wrapper) {
#                     const spans = wrapper.querySelectorAll('span');
#                     if (spans.length >= 3) {
#                         data.homeScore = spans[0].innerText.trim();
#                         data.awayScore = spans[2].innerText.trim();
#                     }
#                 }

#                 const statusEl = document.querySelector('.detailScore__status span');
#                 if (statusEl) data.statusText = statusEl.innerText.trim();

#                 const venueEl = document.querySelector('.duelParticipant__venue');
#                 if (venueEl) data.venue = venueEl.innerText.trim();

#                 return data;
#             }
#         """)

#         result = {}
#         if details.get("homeTeam"):
#             result["home_team"] = details["homeTeam"]
#         if details.get("awayTeam"):
#             result["away_team"] = details["awayTeam"]
#         if details.get("venue"):
#             result["venue_raw"] = details["venue"]

#         date_str = details.get("matchDate", "")
#         if date_str:
#             # Детальная страница матча отдаёт полную дату с годом (в отличие
#             # от списка фикстур, где год не указан) — формат "11.06.2026 22:00".
#             # Если формат другой, сохраняем сырую строку для диагностики,
#             # не теряя остальные поля.
#             try:
#                 result["match_date"] = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
#             except ValueError:
#                 result["match_date_raw"] = date_str

#         home_score = details.get("homeScore", "")
#         away_score = details.get("awayScore", "")
#         if home_score.isdigit() and away_score.isdigit():
#             result["home_score"] = int(home_score)
#             result["away_score"] = int(away_score)

#         status_text = details.get("statusText", "").lower()
#         if "завершен" in status_text or "finished" in status_text:
#             result["status"] = "finished"
#         elif "live" in status_text:
#             result["status"] = "live"
#         else:
#             result["status"] = "scheduled"

#         return result

#     @staticmethod
#     def parse_match_stats_with_browser(page, match_url: str) -> Dict:
#         """
#         Парсинг страницы статистики матча. Имеет смысл вызывать только
#         для матчей, у которых parse_match_details_with_browser уже
#         вернул status == "finished" — иначе страница статистики либо
#         пуста, либо ещё не сформирована.
#         """
#         stats_url = FIFAWorldCupParser.build_stats_url(match_url)
#         print(f"📊 Открываем статистику: {stats_url}")
#         page.goto(stats_url, wait_until="domcontentloaded")
#         page.wait_for_timeout(3000)

#         stats = page.evaluate("""
#             () => {
#                 const result = {};
#                 const rows = document.querySelectorAll('[data-testid="wcl-statistics"]');
#                 rows.forEach(row => {
#                     const categoryEl = row.querySelector('.wcl-category_6sT1J span');
#                     const homeEl = row.querySelector('.wcl-homeValue_3Q-7P span');
#                     const awayEl = row.querySelector('.wcl-awayValue_Y-QR1 span');
#                     if (categoryEl && homeEl && awayEl) {
#                         let category = categoryEl.innerText.trim().toLowerCase();
#                         category = category.replace(/\\s*\\(.*?\\)\\s*/g, '').replace(/ /g, '_');
#                         const homeText = Array.from(homeEl.parentNode.querySelectorAll('span')).map(s => s.innerText.trim()).join(' ').trim();
#                         const awayText = Array.from(awayEl.parentNode.querySelectorAll('span')).map(s => s.innerText.trim()).join(' ').trim();
#                         result[category] = { home: homeText, away: awayText };
#                     }
#                 });
#                 return result;
#             }
#         """)

#         return stats

#     @staticmethod
#     def build_stats_url(match_url: str) -> str:
#         """Преобразует ссылку на матч в ссылку на страницу статистики."""
#         parts = match_url.split("/")
#         base = "/".join(parts[:7])
#         query = parts[-1] if "?" in parts[-1] else ""
#         return f"{base}/summary/stats/overall/{query}"

#     # ------------------------------------------------------------------
#     # Вспомогательные методы
#     # ------------------------------------------------------------------

#     @staticmethod
#     def _extract_mid(url: str) -> str:
#         """Извлекает mid из URL матча."""
#         if "?mid=" in url:
#             return url.split("?mid=")[-1]
#         return ""

#     @staticmethod
#     def _parse_status(class_string: str) -> str:
#         """Определяет статус матча по строке CSS-классов."""
#         if "live" in class_string:
#             return "live"
#         if "finished" in class_string:
#             return "finished"
#         if "postponed" in class_string:
#             return "postponed"
#         return "scheduled"

#     @staticmethod
#     def _close_cookie_banner(page):
#         """Закрывает баннер кук, если он есть."""
#         cookie_selectors = [
#             "#onetrust-accept-btn-handler",
#             ".ot-sdk-container button",
#             "[data-testid='cookie-policy-accept']",
#             ".cookie-accept",
#         ]
#         for selector in cookie_selectors:
#             try:
#                 el = page.query_selector(selector)
#                 if el and el.is_visible():
#                     el.click()
#                     page.wait_for_timeout(1000)
#                     break
#             except Exception:
#                 continue


from typing import List, Dict
from datetime import datetime


class FIFAWorldCupParser:
    """Парсер FIFA World Cup 2026 с Flashscore: расписание (этап 1) + результаты/статистика (этап 2)."""

    FIXTURES_URL = "https://www.flashscorekz.com/football/world/world-championship/fixtures/"

    @staticmethod
    def parse_fixtures_with_browser(page) -> List[Dict]:
        """Парсинг расписания через Playwright. Возвращает список матчей."""
        print("📄 Открываем страницу фикстур...")
        # Явный таймаут 60 сек вместо дефолтных 30000ms Playwright.
        # Замерено: страница фикстур грузится ~14.7 сек в обычных условиях,
        # но при первом старте контейнера (Postgres/Qdrant тоже
        # инициализируются, конкурируя за CPU/память) этого может не
        # хватить — отсюда таймауты на практике при холодном старте.
        page.goto(FIFAWorldCupParser.FIXTURES_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        FIFAWorldCupParser._close_cookie_banner(page)

        matches_data = page.evaluate("""
            () => {
                const matches = [];
                const rows = document.querySelectorAll('.event__match');

                rows.forEach(row => {
                    const link = row.querySelector('a.eventRowLink');
                    if (!link) return;

                    const url = link.href;
                    const midMatch = url.match(/[?&]mid=([a-zA-Z0-9]+)/);
                    const mid = midMatch ? midMatch[1] : '';

                    const homeEl = row.querySelector('.event__homeParticipant .wcl-name_jjfMf');
                    const awayEl = row.querySelector('.event__awayParticipant .wcl-name_jjfMf');

                    const homeScoreEl = row.querySelector('.event__score--home');
                    const awayScoreEl = row.querySelector('.event__score--away');

                    const timeEl = row.querySelector('.event__time');

                    const statusClasses = row.className;

                    matches.push({
                        url: url,
                        mid: mid,
                        homeTeam: homeEl ? homeEl.innerText.trim() : '',
                        awayTeam: awayEl ? awayEl.innerText.trim() : '',
                        homeScore: homeScoreEl ? homeScoreEl.innerText.trim() : '',
                        awayScore: awayScoreEl ? awayScoreEl.innerText.trim() : '',
                        time: timeEl ? timeEl.innerText.trim() : '',
                        statusClasses: statusClasses,
                    });
                });

                return matches;
            }
        """)

        print(f"🔗 Найдено матчей: {len(matches_data)}")

        matches = []
        for data in matches_data:
            match = {
                "flashscore_id": data["mid"],
                "match_url": data["url"],
                "home_team": data["homeTeam"],
                "away_team": data["awayTeam"],
                "time_display": data["time"],
                "status": FIFAWorldCupParser._parse_status(data["statusClasses"]),
            }

            home_score = data["homeScore"]
            away_score = data["awayScore"]
            if home_score.isdigit() and away_score.isdigit():
                match["home_score"] = int(home_score)
                match["away_score"] = int(away_score)

            matches.append(match)

        return matches

    @staticmethod
    def parse_results_with_browser(page) -> List[Dict]:
        """
        Парсинг страницы результатов через Playwright. Страница содержит
        несколько турниров подряд (основной ЧМ-2026 + отборочные циклы
        разных континентов) без чёткого разделения в DOM — все блоки
        матчей идут плоским потоком. Различаем их по дате в .event__time:
          - строка содержит год (например "19.11.2025") → отборочный
            турнир, пропускаем;
          - год не указан (например "19.06. 06:00" или "01.04. 08:00")
            → подставляем год турнира (2026) и сравниваем с датой старта
            ЧМ-2026 (11.06.2026): раньше неё — тоже отборочный/плей-офф
            квалификации, пропускаем.
        Возвращает только матчи основного турнира.
        """
        print("📄 Открываем страницу результатов...")
        page.goto(FIFAWorldCupParser.RESULTS_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        FIFAWorldCupParser._close_cookie_banner(page)

        matches_data = page.evaluate("""
            () => {
                const matches = [];
                const rows = document.querySelectorAll('.event__match');

                rows.forEach(row => {
                    const link = row.querySelector('a.eventRowLink');
                    if (!link) return;

                    const url = link.href;
                    const midMatch = url.match(/[?&]mid=([a-zA-Z0-9]+)/);
                    const mid = midMatch ? midMatch[1] : '';

                    const homeEl = row.querySelector('.event__homeParticipant .wcl-name_jjfMf');
                    const awayEl = row.querySelector('.event__awayParticipant .wcl-name_jjfMf');

                    const homeScoreEl = row.querySelector('.event__score--home');
                    const awayScoreEl = row.querySelector('.event__score--away');

                    const timeEl = row.querySelector('.event__time');

                    matches.push({
                        url: url,
                        mid: mid,
                        homeTeam: homeEl ? homeEl.innerText.trim() : '',
                        awayTeam: awayEl ? awayEl.innerText.trim() : '',
                        homeScore: homeScoreEl ? homeScoreEl.innerText.trim() : '',
                        awayScore: awayScoreEl ? awayScoreEl.innerText.trim() : '',
                        time: timeEl ? timeEl.innerText.trim() : '',
                    });
                });

                return matches;
            }
        """)

        print(f"🔗 Найдено строк на странице результатов: {len(matches_data)}")

        matches = []
        skipped = 0
        for data in matches_data:
            time_display = data["time"]
            if not FIFAWorldCupParser._is_current_tournament_date(time_display):
                skipped += 1
                continue

            home_score = data["homeScore"]
            away_score = data["awayScore"]
            has_score = home_score.isdigit() and away_score.isdigit()

            match = {
                "flashscore_id": data["mid"],
                "match_url": data["url"],
                "home_team": data["homeTeam"],
                "away_team": data["awayTeam"],
                "time_display": time_display,
                # На странице результатов нет CSS-класса со статусом
                # (в отличие от фикстур) — если есть оба значения счёта,
                # матч завершён, иначе оставляем как запланированный.
                "status": "finished" if has_score else "scheduled",
            }

            if has_score:
                match["home_score"] = int(home_score)
                match["away_score"] = int(away_score)

            matches.append(match)

        print(f"✅ Матчей текущего турнира: {len(matches)}, отсеяно (квалификация): {skipped}")
        return matches

    @staticmethod
    def _is_current_tournament_date(time_display: str) -> bool:
        """
        Определяет, относится ли дата матча к основному турниру ЧМ-2026
        (а не к отборочному циклу), по правилу:
          - если строка содержит год → это прошлый цикл (квалификация),
            не относится к турниру;
          - если года нет → подставляем TOURNAMENT_YEAR и сравниваем
            с датой старта турнира; раньше старта — не относится.
        """
        if not time_display:
            return False

        text = time_display.strip()

        # Явный год в строке, например "19.11.2025" → отборочный цикл.
        if re.search(r"\d{4}", text):
            return False

        # "19.06. 06:00" или "19.06. 06:00<вложенный event__stage>" —
        # JS отдаёt innerText, вложенный текст блока event__stage (если
        # есть, например "После д.в.") окажется приклеен к строке без
        # разделителя; день.месяц всё равно в начале строки, извлекаем
        # только его.
        m = re.match(r"^(\d{1,2})\.(\d{1,2})\.", text)
        if not m:
            # Формат не распознан — на всякий случай не включаем матч,
            # чтобы не затащить в БД мусорную запись без даты.
            return False

        day, month = int(m.group(1)), int(m.group(2))
        try:
            match_date = datetime(TOURNAMENT_START_DATE.year, month, day)
        except ValueError:
            return False

        return match_date >= TOURNAMENT_START_DATE

    @staticmethod
    def parse_match_details_with_browser(page, match_url: str) -> Dict:
        """
        Парсинг детальной страницы матча: дата, команды, счёт, статус, стадион.
        Используется на этапе 2 для обновления результатов.
        """
        print(f"📄 Открываем детали матча: {match_url}")
        page.goto(match_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        details = page.evaluate("""
            () => {
                const data = {};

                const timeEl = document.querySelector('.duelParticipant__startTime div');
                if (timeEl) data.matchDate = timeEl.innerText.trim();

                const homeEl = document.querySelector('.duelParticipant__home .participant__participantName a');
                if (homeEl) data.homeTeam = homeEl.innerText.trim();

                const awayEl = document.querySelector('.duelParticipant__away .participant__participantName a');
                if (awayEl) data.awayTeam = awayEl.innerText.trim();

                const wrapper = document.querySelector('.detailScore__wrapper');
                if (wrapper) {
                    const spans = wrapper.querySelectorAll('span');
                    if (spans.length >= 3) {
                        data.homeScore = spans[0].innerText.trim();
                        data.awayScore = spans[2].innerText.trim();
                    }
                }

                const statusEl = document.querySelector('.detailScore__status span');
                if (statusEl) data.statusText = statusEl.innerText.trim();

                const venueEl = document.querySelector('.duelParticipant__venue');
                if (venueEl) data.venue = venueEl.innerText.trim();

                return data;
            }
        """)

        result = {}
        if details.get("homeTeam"):
            result["home_team"] = details["homeTeam"]
        if details.get("awayTeam"):
            result["away_team"] = details["awayTeam"]
        if details.get("venue"):
            result["venue_raw"] = details["venue"]

        date_str = details.get("matchDate", "")
        if date_str:
            # Детальная страница матча отдаёт полную дату с годом (в отличие
            # от списка фикстур, где год не указан) — формат "11.06.2026 22:00".
            # Если формат другой, сохраняем сырую строку для диагностики,
            # не теряя остальные поля.
            try:
                result["match_date"] = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
            except ValueError:
                result["match_date_raw"] = date_str

        home_score = details.get("homeScore", "")
        away_score = details.get("awayScore", "")
        if home_score.isdigit() and away_score.isdigit():
            result["home_score"] = int(home_score)
            result["away_score"] = int(away_score)

        status_text = details.get("statusText", "").lower()
        if "завершен" in status_text or "finished" in status_text:
            result["status"] = "finished"
        elif "live" in status_text:
            result["status"] = "live"
        else:
            result["status"] = "scheduled"

        return result

    @staticmethod
    def parse_match_stats_with_browser(page, match_url: str) -> Dict:
        """
        Парсинг страницы статистики матча. Имеет смысл вызывать только
        для матчей, у которых parse_match_details_with_browser уже
        вернул status == "finished" — иначе страница статистики либо
        пуста, либо ещё не сформирована.
        """
        stats_url = FIFAWorldCupParser.build_stats_url(match_url)
        print(f"📊 Открываем статистику: {stats_url}")
        page.goto(stats_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        stats = page.evaluate("""
            () => {
                const result = {};
                const rows = document.querySelectorAll('[data-testid="wcl-statistics"]');
                rows.forEach(row => {
                    const categoryEl = row.querySelector('.wcl-category_6sT1J span');
                    const homeEl = row.querySelector('.wcl-homeValue_3Q-7P span');
                    const awayEl = row.querySelector('.wcl-awayValue_Y-QR1 span');
                    if (categoryEl && homeEl && awayEl) {
                        let category = categoryEl.innerText.trim().toLowerCase();
                        category = category.replace(/\\s*\\(.*?\\)\\s*/g, '').replace(/ /g, '_');
                        const homeText = Array.from(homeEl.parentNode.querySelectorAll('span')).map(s => s.innerText.trim()).join(' ').trim();
                        const awayText = Array.from(awayEl.parentNode.querySelectorAll('span')).map(s => s.innerText.trim()).join(' ').trim();
                        result[category] = { home: homeText, away: awayText };
                    }
                });
                return result;
            }
        """)

        return stats

    @staticmethod
    def build_stats_url(match_url: str) -> str:
        """Преобразует ссылку на матч в ссылку на страницу статистики."""
        parts = match_url.split("/")
        base = "/".join(parts[:7])
        query = parts[-1] if "?" in parts[-1] else ""
        return f"{base}/summary/stats/overall/{query}"

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_mid(url: str) -> str:
        """Извлекает mid из URL матча."""
        if "?mid=" in url:
            return url.split("?mid=")[-1]
        return ""

    @staticmethod
    def _parse_status(class_string: str) -> str:
        """Определяет статус матча по строке CSS-классов."""
        if "live" in class_string:
            return "live"
        if "finished" in class_string:
            return "finished"
        if "postponed" in class_string:
            return "postponed"
        return "scheduled"

    @staticmethod
    def _close_cookie_banner(page):
        """Закрывает баннер кук, если он есть."""
        cookie_selectors = [
            "#onetrust-accept-btn-handler",
            ".ot-sdk-container button",
            "[data-testid='cookie-policy-accept']",
            ".cookie-accept",
        ]
        for selector in cookie_selectors:
            try:
                el = page.query_selector(selector)
                if el and el.is_visible():
                    el.click()
                    page.wait_for_timeout(1000)
                    break
            except Exception:
                continue