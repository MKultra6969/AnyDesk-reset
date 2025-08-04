import os
import sys
from colorama import init, Fore, Style

try:
    from translations import _, set_language, MESSAGES, CURRENT_LANGUAGE
except ImportError:
    print("Error: translations.py not found. Using default English strings for FAQ.", file=sys.stderr)
    def _(key, **kwargs):
        faq_data = {
            "faq_title": {"en": "--- Frequently Asked Questions (FAQ) ---", "ru": "--- Часто Задаваемые Вопросы (FAQ) ---"},
            "faq_q_origin": {"en": "Q: What is this script and where did it come from?", "ru": "В: Что это за скрипт и откуда он взялся?"},
            "faq_a_origin": {"en": "A: This script is a collection of utilities for managing AnyDesk on Windows. It started as a simple .bat file primarily designed to reset the AnyDesk ID (often needed after license expiration or conflicts) by deleting specific configuration files. It has since evolved to include backup/restore features, service control, and other helpful actions.", "ru": "О: Этот скрипт - набор утилит для управления AnyDesk в Windows. Изначально он был простым .bat файлом, предназначенным в основном для сброса ID AnyDesk (что часто требуется после истечения лицензии или при конфликтах) путем удаления определенных файлов конфигурации. Со временем он развился, включив функции резервного копирования/восстановления, управления службой и другие полезные действия."},
        }
        return faq_data.get(key, {}).get('en', key).format(**kwargs) if kwargs else faq_data.get(key, {}).get('en', key)
    CURRENT_LANGUAGE = "en"
    def set_language(lang): pass # No-op

init(autoreset=True)

FAQ_CONTENT = [
    ("faq_q_origin", "faq_a_origin"),
    ("faq_q_language", "faq_a_language"),
    ("faq_q_admin", "faq_a_admin"),
    ("faq_q_cleanup_what", "faq_a_cleanup_what"),
    ("faq_q_cleanup_modes", "faq_a_cleanup_modes"),
    ("faq_q_cleanup_id_change", "faq_a_cleanup_id_change"),
    ("faq_q_utils_id_change", "faq_a_utils_id_change"),
    ("faq_q_utils_autostart", "faq_a_utils_autostart"),
    ("faq_q_backup_what", "faq_a_backup_what"),
    ("faq_q_backup_where", "faq_a_backup_where"),
    ("faq_q_backup_recordings", "faq_a_backup_recordings"),
    ("faq_q_logging", "faq_a_logging"),
    ("faq_q_risks", "faq_a_risks"),
]

def display_faq():
    print("\n" + Style.BRIGHT + Fore.MAGENTA + "=" * 70)
    print(Style.BRIGHT + Fore.CYAN + _("faq_title"))
    print(Style.BRIGHT + Fore.MAGENTA + "=" * 70)

    for q_key, a_key in FAQ_CONTENT:
        print(Style.BRIGHT + Fore.YELLOW + _(q_key))
        print(Fore.WHITE + _(a_key))
        print("-" * 60) # Separator between questions

    print(Style.BRIGHT + Fore.MAGENTA + "=" * 70)


if __name__ == "__main__":
    # --- Language Selection (Standalone Mode) ---
    print("Select language (en) / Выберите язык (ru): ", end="")
    lang_choice = input().strip().lower()
    while lang_choice not in ['en', 'ru']:
        print("Invalid choice. Please enter 'en' or 'ru'. / Неверный выбор. Пожалуйста, введите 'en' или 'ru'.")
        print("Select language (en) / Выберите язык (ru): ", end="")
        lang_choice = input().strip().lower()
    set_language(lang_choice)
    # --- End Language Selection ---

    display_faq()
    if sys.stdin.isatty():
        input(_("press_enter_to_continue")) # Use translated prompt