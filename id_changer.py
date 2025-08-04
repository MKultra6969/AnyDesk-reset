import os
import sys
import logging
from colorama import init, Fore, Style

# Import translations - assuming translations.py is in the same directory
try:
    from translations import _, set_language, MESSAGES, CURRENT_LANGUAGE
except ImportError:
    print("Error: translations.py not found. Using default English strings.")
    # Define a fallback _ function if import fails
    def _(key, **kwargs):
        return MESSAGES.get(key, {}).get('en', key).format(**kwargs) if kwargs else MESSAGES.get(key, {}).get('en', key)
    # Set default language if not imported
    CURRENT_LANGUAGE = "en"
    def set_language(lang): pass # No-op

# Initialize colorama here as well for standalone use
init(autoreset=True)
logger = logging.getLogger(__name__)

def change_id():
    """
    Пытается удалить файл service.conf для сброса AnyDesk ID.
    Требует прав администратора.
    """
    service_conf_path = os.path.expandvars(r"%ALLUSERSPROFILE%\AnyDesk\service.conf")
    service_conf_filename = os.path.basename(service_conf_path)
    print(Style.BRIGHT + Fore.CYAN + _("idc_attempting_delete", path=f"{Fore.YELLOW}{service_conf_path}"))
    logger.info(f"Попытка удаления файла {service_conf_path} для смены ID.")

    if os.path.exists(service_conf_path):
        try:
            os.remove(service_conf_path)
            print(Style.BRIGHT + Fore.GREEN + _("idc_delete_success", filename=f"'{Fore.YELLOW}{service_conf_filename}{Style.BRIGHT+Fore.GREEN}'"))
            print(Style.BRIGHT + Fore.YELLOW + _("idc_id_reset_info"))
            logger.info(f"Файл {service_conf_filename} успешно удален.")
            return True # Успех
        except PermissionError:
            print(Style.BRIGHT + Fore.RED + _("idc_delete_perm_error", path=f"'{service_conf_path}'"))
            print(Style.BRIGHT + Fore.YELLOW + _("idc_run_as_admin_hint"))
            logger.error(f"Ошибка прав доступа при удалении {service_conf_filename}.")
            return False
        except OSError as e:
            print(Style.BRIGHT + Fore.RED + _("idc_delete_os_error", filename=f"'{service_conf_filename}'"))
            print(Style.BRIGHT + Fore.RED + _("idc_os_error_details", error=e.strerror, errno=e.errno))
            logger.error(f"Ошибка файловой системы при удалении {service_conf_filename}: {e}", exc_info=False)
            return False
        except Exception as e:
             print(Style.BRIGHT + Fore.RED + _("idc_delete_unexpected_error", filename=f"'{service_conf_filename}'", error=e), file=sys.stderr)
             logger.exception(f"Непредвиденная ошибка при удалении {service_conf_filename}: {e}")
             return False
    else:
        print(Style.BRIGHT + Fore.YELLOW + _("idc_file_already_missing", path=f"'{service_conf_path}'"))
        logger.info(f"Файл {service_conf_filename} не существует, удаление не требуется.")
        return True

# --- Точка входа для запуска как отдельного скрипта (для тестов) ---
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

    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger.info("Запуск модуля id_changer как отдельного скрипта.")

    print(Style.BRIGHT + Fore.MAGENTA + "--- AnyDesk ID Changer (Test Mode) ---")
    change_id()
    if sys.stdin.isatty():
        input(_("press_enter_to_continue"))