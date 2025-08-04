import os
import shutil
import subprocess
import time
import logging
import logging.handlers
import pyfiglet
import tkinter as tk
from tkinter import filedialog
from colorama import init as colorama_init, Fore, Back, Style
import winreg
import sys
import ctypes
import requests
from tqdm import tqdm
import faq

LANGUAGE_SET = False
try:
    # Use a separate, minimal import for the initial prompt
    from translations import _, set_language, MESSAGES
    print(MESSAGES["select_language_prompt"]["ru"]) # Print prompt in both languages
    lang_choice = input().strip().lower()
    while not set_language(lang_choice):
        print(MESSAGES["invalid_language_choice"]["ru"] + " / " + MESSAGES["invalid_language_choice"]["en"])
        print(MESSAGES["select_language_prompt"]["ru"])
        lang_choice = input().strip().lower()
    LANGUAGE_SET = True
except ImportError as e:
    print(f"FATAL: Cannot import translations.py: {e}", file=sys.stderr)
    # Provide a way to exit if translations are missing
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"FATAL: Error during language selection: {e}", file=sys.stderr)
    input("Press Enter to exit...")
    sys.exit(1)

# Now that language is set, continue with other imports and initialization
if not LANGUAGE_SET:
    print("FATAL: Language was not set.", file=sys.stderr)
    sys.exit(1)

# Import functions from other modules AFTER language is potentially set
from id_changer import change_id
from backup_restore import (
    backup_user_conf,
    restore_user_conf_interactive,
    restore_user_conf_default,
    set_backup_location_interactive,
    get_current_backup_path,
    get_current_recordings_backup_path,
    backup_screen_recordings,
    restore_screen_recordings
)

# --- Настройка логирования ---
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILENAME = f'anydesk_utils_{timestamp}.log'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

for handler in logger.handlers[:]:
    logger.removeHandler(handler)
    handler.close()

try:
    file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as log_e:
    print(f"Warning: Could not configure file logging to {LOG_FILENAME}: {log_e}", file=sys.stderr)


logger.info("="*30 + f" Запуск скрипта AnyDesk Utils (Лог: {LOG_FILENAME}) " + "="*30)
logger.info(f"Выбран язык / Language selected: {lang_choice}") # Log selected language

colorama_init(autoreset=True) # Инициализация colorama

# --- Утилиты ---

def is_admin():
    """Проверяет, запущен ли скрипт с правами администратора (Windows)."""
    try:
        is_admin_flag = ctypes.windll.shell32.IsUserAnAdmin()
        logger.debug(f"Проверка прав администратора: результат={is_admin_flag}")
        return is_admin_flag
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + _("admin_rights_check_failed"), file=sys.stderr)
        logger.error(f"Не удалось определить права доступа: {e}", exc_info=True)
        return False

def ask_yes_no(prompt_key):
    """Запрашивает у пользователя ввод 'y' или 'n' и возвращает True/False."""
    prompt_message = _(prompt_key) # Translate the key
    while True:
        # Pass the translated prompt to the generic yes/no prompt key
        choice = input(Style.BRIGHT + Fore.LIGHTCYAN_EX + _("yes_no_prompt", prompt=prompt_message)).strip().lower()
        logger.debug(f"Запрос (y/n): '{prompt_message}' Ответ: '{choice}'")
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print(Style.BRIGHT + Fore.RED + _("invalid_yes_no"))
            logger.warning(f"Неверный ввод для (y/n) prompt: '{choice}'")

# --- Функции поиска и управления AnyDesk ---

def find_anydesk_installation_path():
    """
    Ищет путь установки AnyDesk.
    Возвращает путь или None. Выводит сообщение только при нахождении.
    """
    possible_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    anydesk_install_path = None
    found_paths = []

    logger.info("Поиск установки AnyDesk...")
    # Поиск в реестре
    for hive, key_path in possible_keys:
        try:
            access_mask = winreg.KEY_READ | winreg.KEY_WOW64_64KEY
            with winreg.OpenKey(hive, key_path, 0, access_mask) as main_key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(main_key, i)
                        subkey_path = os.path.join(key_path, subkey_name).replace('/', '\\')
                        # logger.debug(f"Проверка ключа: {hive}\\{subkey_path}") # Less verbose logging
                        try:
                            with winreg.OpenKey(hive, subkey_path, 0, access_mask) as sub_key:
                                display_name, install_location = "", ""
                                try:
                                    display_name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                                    # logger.debug(f"  DisplayName: {display_name}")
                                except FileNotFoundError:
                                    pass
                                try:
                                    install_location, _ = winreg.QueryValueEx(sub_key, "InstallLocation")
                                    # logger.debug(f"  InstallLocation: {install_location}")
                                except FileNotFoundError:
                                    pass

                                if "anydesk" in display_name.lower() and install_location:
                                    potential_exe = os.path.join(install_location, "AnyDesk.exe")
                                    if os.path.isdir(install_location) and os.path.exists(potential_exe):
                                        normalized_path = os.path.normpath(install_location)
                                        if normalized_path not in found_paths:
                                            logger.info(f"Найден возможный путь в реестре: {normalized_path}")
                                            found_paths.append(normalized_path)
                                    # else: logger.debug(f"...") # Less verbose
                        except OSError:
                             # logger.debug(f"  Не удалось открыть или прочитать подраздел {subkey_path}: {e_inner}")
                             pass
                        i += 1
                    except OSError:
                        # logger.debug(f"Закончились подразделы в {key_path}")
                        break
        except FileNotFoundError:
            # logger.debug(f"Ветка реестра не найдена: {key_path} в {hive}")
            pass
        except Exception as e_outer:
            logger.error(f"Ошибка доступа к ветке реестра '{key_path}': {e_outer}", exc_info=False)

    # Поиск в стандартных папках, если реестр не дал результатов
    if not found_paths:
        logger.info("Поиск в реестре не дал результатов. Проверка стандартных папок...")
        standard_locations = [
            os.path.expandvars(r"%ProgramFiles(x86)%\AnyDesk"),
            os.path.expandvars(r"%ProgramFiles%\AnyDesk"),
        ]
        for loc in standard_locations:
            potential_exe = os.path.join(loc, "AnyDesk.exe")
            if os.path.isdir(loc) and os.path.exists(potential_exe):
                 normalized_path = os.path.normpath(loc)
                 if normalized_path not in found_paths:
                      logger.info(f"Найден путь в стандартной папке: {normalized_path}")
                      found_paths.append(normalized_path)
            # else: logger.debug(f"Стандартная папка/EXE не найден: {potential_exe}")


    # Обработка найденных путей
    if found_paths:
        unique_paths = sorted(list(set(found_paths)))
        if len(unique_paths) > 1:
            print(Style.BRIGHT + Fore.YELLOW + _("find_path_multiple_found"))
            logger.warning(f"Обнаружено несколько путей AnyDesk: {unique_paths}")
            for idx, p in enumerate(unique_paths):
                print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + f"  {idx + 1}. {p}")
            while True:
                try:
                    choice_idx = int(input(Style.BRIGHT + Fore.LIGHTCYAN_EX + _("find_path_select_prompt")).strip())
                    if 1 <= choice_idx <= len(unique_paths):
                        anydesk_install_path = unique_paths[choice_idx - 1]
                        logger.info(f"Пользователь выбрал путь: {anydesk_install_path}")
                        break
                    else:
                        print(Style.BRIGHT + Fore.RED + _("find_path_invalid_number"))
                        logger.warning(f"Неверный номер пути: {choice_idx}")
                except ValueError:
                    print(Style.BRIGHT + Fore.RED + _("find_path_enter_number"))
                    logger.warning("Нечисловой ввод при выборе пути.")
        else:
            anydesk_install_path = unique_paths[0]

        if anydesk_install_path:
             print(Style.BRIGHT + Fore.GREEN + _("find_path_success", path=f"{Fore.YELLOW}{anydesk_install_path}"))
             logger.info(f"Итоговый путь установки AnyDesk: {anydesk_install_path}")
    else:
         print(Style.BRIGHT + Fore.RED + _("find_path_failed"))
         logger.error("Не удалось найти папку установки AnyDesk.")

    return anydesk_install_path


def killing_anydesk():
    """Завершает процесс AnyDesk.exe и останавливает службу AnyDesk."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("kill_attempting_process"))
    logger.info("Попытка завершения процесса AnyDesk.exe")
    process_killed = False
    try:
        result = subprocess.run(
            ["taskkill", "/IM", "AnyDesk.exe", "/F"],
            check=False, capture_output=True, text=True, encoding='cp866', errors='ignore'
        )
        logger.debug(f"taskkill /IM AnyDesk.exe /F -> Код: {result.returncode}, stdout: {result.stdout.strip()}, stderr: {result.stderr.strip()}")
        if result.returncode == 0:
            print(Style.BRIGHT + Fore.GREEN + _("kill_process_success"))
            logger.info("Процесс AnyDesk.exe успешно завершен командой taskkill.")
            process_killed = True
        elif result.returncode == 128:
            print(Style.BRIGHT + Fore.YELLOW + _("kill_process_not_found"))
            logger.info("Процесс AnyDesk.exe не найден taskkill (код 128).")
            process_killed = True
        else:
             print(Style.BRIGHT + Fore.LIGHTRED_EX + _("kill_process_error", code=result.returncode))
             logger.error(f"Ошибка taskkill /IM AnyDesk.exe /F: код {result.returncode}. Вывод: [{result.stdout.strip()}] [{result.stderr.strip()}]")
             if "отказано в доступе" in result.stderr.lower() or "access is denied" in result.stderr.lower():
                 print(Style.BRIGHT + Fore.YELLOW + _("kill_process_perm_error"))
                 logger.warning("Taskkill отказано в доступе.")
    except FileNotFoundError:
        print(Style.BRIGHT + Fore.RED + _("kill_taskkill_not_found"))
        logger.error("Команда taskkill не найдена.")
    except Exception as e:
         print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
         logger.exception(f"Непредвиденная ошибка при taskkill AnyDesk.exe: {e}")

    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("kill_attempting_service"))
    logger.info("Попытка остановки службы AnyDesk (sc stop)")
    service_names_to_try = ["AnyDesk", "AnyDeskService"]
    service_stopped_successfully = False

    for service_name in service_names_to_try:
        try:
            logger.debug(f"Попытка остановить службу '{service_name}'...")
            result = subprocess.run(
                ["sc", "stop", service_name],
                capture_output=True, text=True, encoding='cp866', errors='ignore', check=False
            )
            logger.debug(f"sc stop {service_name} -> Код: {result.returncode}, stdout: {result.stdout.strip()}, stderr: {result.stderr.strip()}")
            if result.returncode == 0:
                print(Style.BRIGHT + Fore.GREEN + _("kill_service_stop_sent", name=f"{Fore.YELLOW}{service_name}{Fore.GREEN}"))
                logger.info(f"Команда 'sc stop {service_name}' успешно отправлена.")
                service_stopped_successfully = True
                break
            elif result.returncode == 1060:
                print(Style.BRIGHT + Fore.YELLOW + _("kill_service_not_found", name=f"{Fore.WHITE}{service_name}{Fore.YELLOW}"))
                logger.info(f"Служба '{service_name}' не найдена (код 1060).")
            elif result.returncode == 1062:
                print(Style.BRIGHT + Fore.YELLOW + _("kill_service_already_stopped", name=f"{Fore.WHITE}{service_name}{Fore.YELLOW}"))
                logger.info(f"Служба '{service_name}' уже остановлена (код 1062).")
                service_stopped_successfully = True
            elif result.returncode == 5:
                 print(Style.BRIGHT + Fore.RED + _("kill_service_perm_error", name=service_name))
                 logger.error(f"Ошибка прав доступа (5) при попытке остановить службу '{service_name}'.")
            else:
                print(Style.BRIGHT + Fore.RED + _("kill_service_stop_error", name=service_name, code=result.returncode))
                logger.error(f"Ошибка 'sc stop {service_name}': код {result.returncode}. Вывод: [{result.stdout.strip()}] [{result.stderr.strip()}]")
        except FileNotFoundError:
            print(Style.BRIGHT + Fore.RED + _("kill_sc_not_found"))
            logger.error("Команда 'sc' не найдена.")
            break
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
            logger.exception(f"Непредвиденная ошибка при 'sc stop {service_name}': {e}")

    if not process_killed and not service_stopped_successfully:
        print(Style.BRIGHT + Fore.YELLOW + _("kill_summary_failed"))
    elif not process_killed:
        print(Style.BRIGHT + Fore.YELLOW + _("kill_summary_process_failed"))
    elif not service_stopped_successfully:
        print(Style.BRIGHT + Fore.YELLOW + _("kill_summary_service_failed"))
    else:
        logger.info("Процесс и служба AnyDesk успешно остановлены/завершены (или не были запущены/найдены).")


def remove_anydesk(confirm=True):
    """Удаляет папки и файлы AnyDesk."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("remove_starting"))
    logger.info("Начало удаления AnyDesk.")

    install_path = find_anydesk_installation_path() # Prints path if found

    data_paths = [
        os.path.expandvars(r"%PROGRAMDATA%\AnyDesk"),
        os.path.expandvars(r"%APPDATA%\AnyDesk"),
        os.path.expandvars(r"%LOCALAPPDATA%\AnyDesk"),
    ]

    all_paths_to_consider = list(data_paths)
    if install_path:
         normalized_install_path = os.path.normpath(install_path)
         if normalized_install_path not in [os.path.normpath(p) for p in all_paths_to_consider]:
             all_paths_to_consider.append(normalized_install_path)

    all_paths_to_consider = sorted(list(set([os.path.normpath(p) for p in all_paths_to_consider])))

    print(Style.BRIGHT + Fore.CYAN + _("remove_paths_to_check"))
    logger.info("Пути, предназначенные для удаления:")
    for p in all_paths_to_consider:
        print(Style.BRIGHT + Fore.WHITE + f"  - {Fore.YELLOW}{p}")
        logger.info(f"  - {p}")

    if confirm:
        if not ask_yes_no("remove_confirm"):
             print(Style.BRIGHT + Fore.YELLOW + _("remove_cancelled"))
             logger.info("Удаление AnyDesk отменено пользователем.")
             return False

    paths_to_remove = list(all_paths_to_consider)
    deleted_count = 0
    failed_count = 0
    print(Style.BRIGHT + Fore.MAGENTA + _("remove_process_start"))
    logger.info("Начало фактического удаления файлов/папок AnyDesk.")
    for path in paths_to_remove:
        logger.debug(f"Обработка пути для удаления: {path}")
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    print(Style.BRIGHT + Fore.YELLOW + _("remove_deleting_folder", path=f"{Fore.WHITE}{path}"))
                    logger.info(f"Удаление папки: {path}")
                    try:
                        shutil.rmtree(path, ignore_errors=False)
                    except OSError as e_rmtree:
                        if not isinstance(e_rmtree, PermissionError):
                            logger.warning(f"Первая попытка rmtree не удалась: {e_rmtree}. Повторная попытка через 0.5 сек...")
                            time.sleep(0.5)
                            shutil.rmtree(path, ignore_errors=False)
                        else:
                            raise
                elif os.path.isfile(path):
                     print(Style.BRIGHT + Fore.YELLOW + _("remove_deleting_file", path=f"{Fore.WHITE}{path}"))
                     logger.info(f"Удаление файла: {path}")
                     os.remove(path)

                if not os.path.exists(path):
                    print(Style.BRIGHT + Fore.GREEN + _("remove_delete_success", path=f"{Fore.WHITE}{path}"))
                    logger.info(f"  Успешно удалено: {path}")
                    deleted_count += 1
                else:
                    print(Style.BRIGHT + Fore.RED + _("remove_still_exists", path=path))
                    logger.error(f"Объект {path} все еще существует после попытки удаления без явной ошибки.")
                    failed_count += 1

            except PermissionError:
                 print(Style.BRIGHT + Fore.RED + _("remove_perm_error", path=path))
                 logger.error(f"Ошибка прав доступа при удалении: {path}.")
                 failed_count +=1
            except OSError as e:
                 print(Style.BRIGHT + Fore.RED + _("remove_os_error", path=path, error=e.strerror, errno=e.errno))
                 logger.error(f"Ошибка файловой системы при удалении {path}: {e}", exc_info=True)
                 failed_count += 1
            except Exception as e:
                 print(Style.BRIGHT + Fore.RED + _("remove_unexpected_error", path=path, error=e), file=sys.stderr)
                 logger.exception(f"Непредвиденная ошибка при удалении {path}: {e}")
                 failed_count += 1
        else:
            logger.debug(f"Путь не найден, пропуск удаления: {path}")

    print(Style.BRIGHT + Fore.MAGENTA + _("remove_summary_complete"))
    logger.info(f"Удаление завершено. Удалено: {deleted_count}, Ошибок: {failed_count}.")
    if deleted_count > 0:
         print(Style.BRIGHT + Fore.GREEN + _("remove_summary_deleted", count=deleted_count))
    if failed_count > 0:
         print(Style.BRIGHT + Fore.RED + _("remove_summary_failed", count=failed_count, log_file=LOG_FILENAME))
    if deleted_count == 0 and failed_count == 0:
         print(Style.BRIGHT + Fore.YELLOW + _("remove_summary_nothing"))

    return failed_count == 0

# --- Скачивание AnyDesk ---
ANYDESK_DOWNLOAD_URL = "https://download.anydesk.com/AnyDesk.exe"

def download_latest_anydesk(save_dir=None):
    """Скачивает последнюю версию AnyDesk.exe."""
    if save_dir is None:
        downloads_dir = os.path.expanduser("~/Downloads")
        desktop_dir = os.path.expanduser("~/Desktop")
        if os.path.isdir(downloads_dir):
            save_dir = downloads_dir
            logger.debug("Папка для скачивания по умолчанию: Downloads.")
        elif os.path.isdir(desktop_dir):
            save_dir = desktop_dir
            logger.debug("Папка Downloads не найдена, используется Desktop.")
        else:
            save_dir = "."
            logger.warning("Папки Downloads и Desktop не найдены, используется текущая директория.")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"AnyDesk_{timestamp}.exe"
    save_path = os.path.join(save_dir, filename)

    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("download_starting"))
    print(_("download_source", url=f"{Fore.CYAN}{ANYDESK_DOWNLOAD_URL}"))
    print(_("download_destination", path=f"{Fore.YELLOW}{save_path}"))
    logger.info(f"Начало скачивания AnyDesk с {ANYDESK_DOWNLOAD_URL} в {save_path}")

    try:
        response = requests.get(ANYDESK_DOWNLOAD_URL, stream=True, timeout=(10, 60))
        logger.debug(f"HTTP статус ответа: {response.status_code}")
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        logger.debug(f"Ожидаемый размер файла (content-length): {total_size}")
        block_size = 8192

        os.makedirs(save_dir, exist_ok=True)

        print(Style.BRIGHT + Fore.CYAN + _("download_progress"))
        # Use basename for tqdm description
        tqdm_desc = Fore.GREEN + os.path.basename(save_path)
        with open(save_path, 'wb') as file, tqdm(
            desc=tqdm_desc,
            total=total_size,
            unit='iB', unit_scale=True, unit_divisor=1024,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]',
            ncols=70
        ) as bar:
            for data in response.iter_content(block_size):
                size = file.write(data)
                bar.update(size)

        downloaded_size = os.path.getsize(save_path)
        logger.debug(f"Фактический размер скачанного файла: {downloaded_size}")

        if total_size != 0 and downloaded_size != total_size:
             print(Style.BRIGHT + Fore.RED + _("download_error_size_mismatch", downloaded=downloaded_size, expected=total_size))
             logger.error(f"Размер скачанного AnyDesk ({downloaded_size}) не совпадает с заголовком ({total_size}).")
             try: os.remove(save_path); logger.info(f"Удален неполный файл: {save_path}")
             except OSError: logger.warning(f"Не удалось удалить неполный файл {save_path}")
             return None
        if downloaded_size == 0 and total_size != 0:
             print(Style.BRIGHT + Fore.RED + _("download_error_empty_file"))
             logger.error("Скачан пустой файл AnyDesk (размер 0).")
             try: os.remove(save_path); logger.info(f"Удален пустой файл: {save_path}")
             except OSError: logger.warning(f"Не удалось удалить пустой файл {save_path}")
             return None

        print(Style.BRIGHT + Fore.GREEN + _("download_success", path=f"{Fore.YELLOW}{save_path}"))
        logger.info(f"Файл AnyDesk успешно скачан: {save_path}")
        return save_path

    except requests.exceptions.Timeout:
         print(Style.BRIGHT + Fore.RED + _("download_error_timeout"))
         logger.error(f"Таймаут при скачивании AnyDesk с {ANYDESK_DOWNLOAD_URL}", exc_info=True)
         return None
    except requests.exceptions.RequestException as e:
         print(Style.BRIGHT + Fore.RED + _("download_error_network", error=e))
         logger.error(f"Ошибка сети при скачивании AnyDesk: {e}", exc_info=True)
         return None
    except OSError as e:
         print(Style.BRIGHT + Fore.RED + _("download_error_write", error=e.strerror))
         logger.error(f"Ошибка записи файла при скачивании AnyDesk: {e}", exc_info=True)
         if 'save_path' in locals() and os.path.exists(save_path):
            try: os.remove(save_path); logger.info(f"Удален частично записанный файл: {save_path}")
            except OSError: logger.warning(f"Не удалось удалить частично записанный файл {save_path}")
         return None
    except Exception as e:
         print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
         logger.exception(f"Непредвиденная ошибка при скачивании AnyDesk: {e}")
         return None


def install_anydesk(installer_path_param=None, silent=False):
    """Скачивает/выбирает и запускает установщик AnyDesk."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("install_starting"))
    logger.info(f"Начало процесса установки AnyDesk (silent={silent}).")
    installer_path = installer_path_param

    if not installer_path:
        if not silent and ask_yes_no("install_ask_download"):
            downloaded_path = download_latest_anydesk()
            if downloaded_path:
                if ask_yes_no("install_use_downloaded", filename=f"{Fore.YELLOW}{os.path.basename(downloaded_path)}{Style.BRIGHT+Fore.LIGHTCYAN_EX}"):
                     installer_path = downloaded_path
                else:
                     print(Style.BRIGHT + Fore.YELLOW + _("install_downloaded_not_used"))
                     logger.info("Скачанный файл не будет использован для установки.")
            else:
                print(Style.BRIGHT + Fore.RED + _("install_download_failed"))
                logger.error("Скачивание AnyDesk не удалось.")

        if not installer_path and not silent:
            if ask_yes_no("install_ask_select_manual"):
                logger.info("Запрос выбора файла установщика вручную.")
                print(Style.BRIGHT + Fore.YELLOW + _("install_select_prompt"))
                root = tk.Tk(); root.attributes('-topmost', True); root.withdraw()
                selected_path = filedialog.askopenfilename(
                    title=_("install_select_title"),
                    filetypes=_("install_filetypes"),
                )
                root.destroy()
                if selected_path:
                    installer_path = selected_path
                    logger.info(f"Пользователь выбрал установщик: {installer_path}")
                else:
                     print(Style.BRIGHT + Fore.YELLOW + _("file_not_selected"))
                     logger.info("Выбор файла установщика отменен.")

    if not installer_path:
        print(Style.BRIGHT + Fore.YELLOW + _("install_cancelled"))
        logger.warning("Установка AnyDesk отменена, т.к. установщик не найден/не выбран.")
        return False

    print(_("install_using_installer", path=f"{Fore.YELLOW}{installer_path}"))
    logger.info(f"Запуск установщика: {installer_path}")

    install_dir_pf = os.path.expandvars(r"%ProgramFiles%\AnyDesk")
    install_dir_pf86 = os.path.expandvars(r"%ProgramFiles(x86)%\AnyDesk")

    install_command = [installer_path]

    if silent:
        print(Style.BRIGHT + Fore.CYAN + _("install_attempting_silent"))
        logger.info("Добавление параметров тихой установки.")
        # Use ProgramFiles path as default target for silent install
        install_command = [installer_path, "--install", install_dir_pf, "--silent", "--start-with-win", "--create-desktop-icon"]

    try:
        if silent:
            print(Style.BRIGHT + Fore.YELLOW + _("install_running_command", command=f"{Fore.WHITE}{' '.join(install_command)}"))
            logger.info(f"Команда тихой установки: {' '.join(install_command)}")
            process = subprocess.Popen(install_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866', errors='ignore')
            try:
                stdout, stderr = process.communicate(timeout=300) # 5 minutes
                return_code = process.returncode
                logger.info(f"Тихая установка завершена. Код возврата: {return_code}")
                if stdout: logger.debug(f"Вывод stdout тихой установки:\n{stdout}")
                if stderr: logger.debug(f"Вывод stderr тихой установки:\n{stderr}")

                if return_code != 0:
                     logger.error(f"Тихая установка завершилась с ошибкой (код {return_code}).")
                     print(Style.BRIGHT + Fore.RED + _("install_silent_error_code", code=return_code))
                     if stderr and "progress" not in stderr.lower():
                         print(Style.BRIGHT + Fore.RED + _("install_silent_error_stderr", stderr=stderr.strip()))
                     return False

            except subprocess.TimeoutExpired:
                print(Style.BRIGHT + Fore.RED + _("install_silent_timeout"))
                logger.error("Таймаут тихой установки AnyDesk.")
                process.kill()
                logger.warning("Процесс установки AnyDesk принудительно завершен из-за таймаута.")
                return False
        else:
            print(Style.BRIGHT + Fore.YELLOW + _("install_interactive_prompt"))
            process = subprocess.run(install_command, check=False)
            logger.info(f"Интерактивный установщик завершил работу. Код возврата: {process.returncode}")

        print(Style.BRIGHT + Fore.GREEN + _("install_finished"))
        logger.info("Проверка наличия AnyDesk.exe после установки...")
        final_exe_path_pf = os.path.join(install_dir_pf, "AnyDesk.exe")
        final_exe_path_pf86 = os.path.join(install_dir_pf86, "AnyDesk.exe")

        if os.path.exists(final_exe_path_pf):
            logger.info(f"Найден {final_exe_path_pf} после установки.")
            print(Style.BRIGHT + Fore.GREEN + _("install_verify_success_found", path=final_exe_path_pf))
            return True
        elif os.path.exists(final_exe_path_pf86):
            logger.info(f"Найден {final_exe_path_pf86} после установки.")
            print(Style.BRIGHT + Fore.GREEN + _("install_verify_success_found", path=final_exe_path_pf86))
            return True
        else:
            if silent and 'return_code' in locals() and return_code == 0:
                print(Style.BRIGHT + Fore.YELLOW + _("install_verify_failed_silent_ok"))
                logger.warning(f"Тихая установка вернула 0, но AnyDesk.exe не найден в '{install_dir_pf}' или '{install_dir_pf86}'.")
            elif not silent or ('return_code' in locals() and return_code != 0):
                 print(Style.BRIGHT + Fore.YELLOW + _("install_verify_failed_generic"))
                 logger.warning(f"AnyDesk.exe не найден в '{install_dir_pf}' или '{install_dir_pf86}' после установки.")
            return False

    except FileNotFoundError:
         print(Style.BRIGHT + Fore.RED + _("install_error_installer_not_found", path=f"'{installer_path}'"))
         logger.error(f"Файл установщика не найден: '{installer_path}'")
         return False
    except subprocess.CalledProcessError as e:
        print(Style.BRIGHT + Fore.RED + _("install_error_called_process", code=e.returncode))
        logger.error(f"Установщик '{installer_path}' вернул код ошибки {e.returncode}.")
        if e.stdout: logger.error(f"  stdout: {e.stdout}")
        if e.stderr: logger.error(f"  stderr: {e.stderr}")
        return False
    except PermissionError:
         print(Style.BRIGHT + Fore.RED + _("install_error_permission"))
         logger.error(f"Ошибка прав доступа при запуске '{installer_path}'.")
         return False
    except Exception as e:
         print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
         logger.exception(f"Непредвиденная ошибка при запуске установки '{installer_path}': {e}")
         return False


def run_anydesk():
    """Ищет и запускает AnyDesk."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("run_starting"))
    logger.info("Попытка запуска AnyDesk.")
    anydesk_exe_path = None
    install_dir = find_anydesk_installation_path()
    if install_dir:
        potential_path = os.path.join(install_dir, "AnyDesk.exe")
        if os.path.exists(potential_path):
            anydesk_exe_path = potential_path
            logger.info(f"Используем AnyDesk.exe из папки установки: {anydesk_exe_path}")
        else:
            logger.warning(f"Найден каталог установки {install_dir}, но AnyDesk.exe там нет.")

    if anydesk_exe_path:
        print(_("run_using_path", path=f"{Fore.YELLOW}{anydesk_exe_path}"))
        logger.info(f"Запуск AnyDesk: {anydesk_exe_path}")
        try:
            subprocess.Popen([anydesk_exe_path])
            print(Style.BRIGHT + Fore.CYAN + _("run_command_sent"))
            logger.info("Команда запуска AnyDesk отправлена (Popen).")
            print(Style.BRIGHT + Fore.YELLOW + _("run_checking_status"))
            time.sleep(2)
            if check_anydesk_running():
                print(Style.BRIGHT + Fore.GREEN + _("run_process_found"))
                logger.info("Процесс AnyDesk.exe обнаружен после запуска.")
            else:
                print(Style.BRIGHT + Fore.YELLOW + _("run_process_not_found"))
                logger.warning("Процесс AnyDesk.exe не обнаружен после Popen.")
            return True
        except PermissionError:
             print(Style.BRIGHT + Fore.RED + _("run_error_permission"))
             logger.error(f"Ошибка прав доступа при запуске {anydesk_exe_path}.")
             return False
        except OSError as e:
             print(Style.BRIGHT + Fore.RED + _("run_error_os", error=e.strerror))
             logger.error(f"Ошибка системы при запуске {anydesk_exe_path}: {e}", exc_info=True)
             return False
        except Exception as e:
             print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
             logger.exception(f"Ошибка при запуске AnyDesk из {anydesk_exe_path}: {e}")
             return False
    else:
        # find_anydesk_installation_path already printed an error
        print(Style.BRIGHT + Fore.YELLOW + _("run_error_not_found_final"))
        logger.error("Не удалось найти AnyDesk.exe для запуска.")
        return False


def check_anydesk_running():
    """Проверяет, запущен ли процесс AnyDesk.exe."""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq AnyDesk.exe'],
            capture_output=True, text=True, check=False,
            encoding='cp866', errors='ignore'
        )
        is_running = result.returncode == 0 and "anydesk.exe" in result.stdout.lower()
        logger.debug(f"Проверка AnyDesk.exe через tasklist: {'запущен' if is_running else 'не запущен'} (Код: {result.returncode})")
        return is_running
    except FileNotFoundError:
        logger.error("Команда 'tasklist' не найдена для проверки процесса.")
        return None
    except Exception as e:
        logger.error(f"Ошибка при проверке процесса AnyDesk через tasklist: {e}", exc_info=True)
        return None

def id_changer_question():
    """Спрашивает пользователя, нужно ли сменить ID AnyDesk, и выполняет действие."""
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("id_change_starting"))
    logger.info("Запрос на смену ID AnyDesk.")
    # Format the prompt string with the filename
    service_conf_filename = os.path.basename(os.path.expandvars(r"%ALLUSERSPROFILE%\AnyDesk\service.conf"))
    prompt_text = _("id_change_prompt", filename=f"{Fore.YELLOW}{service_conf_filename}{Style.BRIGHT+Fore.LIGHTCYAN_EX}")

    # Use ask_yes_no with the already formatted prompt text as the 'key' (it will be displayed directly)
    # We need a temporary key for ask_yes_no or modify ask_yes_no
    # Let's just pass the formatted text directly for simplicity here.
    # Modify ask_yes_no slightly to accept pre-formatted text.
    # Or, create a specific prompt key for this complex case. Let's do the latter.

    if ask_yes_no("id_change_prompt", filename=f"{Fore.YELLOW}{service_conf_filename}{Style.BRIGHT+Fore.LIGHTCYAN_EX}"): # Pass filename for formatting
        logger.info("Пользователь подтвердил смену ID.")
        print(Style.BRIGHT + Fore.CYAN + _("id_change_stopping_service"))
        killing_anydesk()
        print(Style.BRIGHT + Fore.GREEN + _("id_change_executing"))
        success = change_id()
        if success:
            print(Style.BRIGHT + Fore.LIGHTGREEN_EX + _("id_change_success"))
        else:
            print(Style.BRIGHT + Fore.RED + _("id_change_failed"))
    else:
        print(Style.BRIGHT + Fore.GREEN + _("id_change_skipping"))
        logger.info("Пользователь отменил смену ID.")

# --- Управление автозапуском (Реестр HKCU) ---
REG_AUTOSTART_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_AUTOSTART_VALUE_NAME = "AnyDesk"

def check_autostart_status():
    """Проверяет статус автозапуска AnyDesk в HKCU\...\Run."""
    logger.debug(f"Проверка статуса автозапуска AnyDesk в HKCU\\{REG_AUTOSTART_KEY_PATH}, значение '{REG_AUTOSTART_VALUE_NAME}'")
    key = None
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_AUTOSTART_KEY_PATH, 0, winreg.KEY_READ)
        try:
            value, reg_type = winreg.QueryValueEx(key, REG_AUTOSTART_VALUE_NAME)
            logger.info(f"Автозапуск AnyDesk включен. Путь в реестре: {value}")
            return True
        except FileNotFoundError:
            logger.info("Автозапуск AnyDesk отключен (запись не найдена).")
            return False
        finally:
            if key: winreg.CloseKey(key); logger.debug("Ключ реестра автозапуска закрыт.")
    except FileNotFoundError:
        logger.warning(f"Ключ автозапуска HKCU\\{REG_AUTOSTART_KEY_PATH} не найден.")
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке статуса автозапуска AnyDesk: {e}", exc_info=True)
        if key:
            try: winreg.CloseKey(key)
            except Exception: pass
        return None # Status unknown

def get_autostart_status_display():
    """Gets the display string for autostart status."""
    status_raw = check_autostart_status()
    if status_raw is True: return Fore.GREEN + _("autostart_status_enabled")
    elif status_raw is False: return Fore.YELLOW + _("autostart_status_disabled")
    else: return Fore.RED + _("autostart_status_unknown")

def set_autostart_registry(enable=True):
    """Включает или отключает автозапуск AnyDesk через реестр HKCU."""
    action_key = "autostart_action_enabling" if enable else "autostart_action_disabling"
    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("autostart_setting_action", action=_(action_key)))
    logger.info(f"{_(action_key)} автозапуска AnyDesk через HKCU\\{REG_AUTOSTART_KEY_PATH}.")

    install_path = find_anydesk_installation_path()
    if not install_path:
        print(Style.BRIGHT + Fore.RED + _("autostart_path_not_found"))
        logger.error("Не найден путь установки AnyDesk, управление автозапуском невозможно.")
        return False

    exe_path = os.path.join(install_path, "AnyDesk.exe")
    if not os.path.exists(exe_path):
         print(Style.BRIGHT + Fore.RED + _("autostart_exe_not_found", path=exe_path))
         print(Style.BRIGHT + Fore.RED + _("autostart_cannot_manage"))
         logger.error(f"AnyDesk.exe не найден в '{install_path}', управление автозапуском невозможно.")
         return False

    key = None
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_AUTOSTART_KEY_PATH, 0, winreg.KEY_WRITE)
        if enable:
            value_data = f'"{exe_path}" --tray'
            winreg.SetValueEx(key, REG_AUTOSTART_VALUE_NAME, 0, winreg.REG_SZ, value_data)
            print(Style.BRIGHT + Fore.GREEN + _("autostart_enabled_success"))
            print(_("autostart_registry_info_added", name=f"{Fore.YELLOW}{REG_AUTOSTART_VALUE_NAME}{Fore.GREEN}"))
            logger.info(f"Запись автозапуска '{REG_AUTOSTART_VALUE_NAME}' добавлена/обновлена: {value_data}")
        else:
            try:
                winreg.DeleteValue(key, REG_AUTOSTART_VALUE_NAME)
                print(Style.BRIGHT + Fore.GREEN + _("autostart_disabled_success"))
                print(_("autostart_registry_info_removed", name=f"{Fore.YELLOW}{REG_AUTOSTART_VALUE_NAME}{Fore.GREEN}"))
                logger.info(f"Запись автозапуска '{REG_AUTOSTART_VALUE_NAME}' удалена.")
            except FileNotFoundError:
                print(Style.BRIGHT + Fore.YELLOW + _("autostart_already_disabled"))
                logger.info(f"Запись автозапуска '{REG_AUTOSTART_VALUE_NAME}' не найдена при попытке удаления.")
        return True
    except PermissionError:
         print(Style.BRIGHT + Fore.RED + _("autostart_registry_perm_error"))
         logger.error("Ошибка прав доступа при изменении реестра автозапуска HKCU.")
         return False
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + _("autostart_registry_error", error=e), file=sys.stderr)
        logger.error(f"Ошибка при доступе к реестру автозапуска HKCU: {e}", exc_info=True)
        return False
    finally:
         if key:
             try: winreg.CloseKey(key)
             except Exception: pass


# --- Управление службой AnyDesk ---
ANYDESK_SERVICE_NAMES = ["AnyDesk", "AnyDeskService"] # Возможные имена службы

def get_service_status_display(status_code):
    """Gets the display string for a service status code."""
    status_map = {
        "RUNNING": Fore.GREEN + _("service_status_running"),
        "STOPPED": Fore.YELLOW + _("service_status_stopped"),
        "NOT_FOUND": Fore.RED + _("service_status_not_found"),
        "ACCESS_DENIED": Fore.RED + _("service_status_access_denied"),
        "START_PENDING": Fore.CYAN + _("service_status_start_pending"),
        "STOP_PENDING": Fore.CYAN + _("service_status_stop_pending"),
        "ALREADY_RUNNING": Fore.GREEN + _("service_status_already_running"),
        "ALREADY_STOPPED": Fore.YELLOW + _("service_status_already_stopped"),
        "STARTED": Fore.GREEN + _("service_status_running"), # Treat STARTED as RUNNING for display
        "STOPPED_OK": Fore.YELLOW + _("service_status_stopped"), # Treat STOPPED_OK as STOPPED for display
        "UNKNOWN_STATE": Fore.MAGENTA + _("service_status_unknown"),
        "QUERY_FAILED": Fore.MAGENTA + _("service_status_query_failed"),
        "START_FAILED": Fore.RED + _("service_status_start_failed"),
        "STOP_FAILED": Fore.RED + _("service_status_stop_failed"),
        "SC_NOT_FOUND": Fore.RED + _("service_status_sc_not_found"),
        "EXCEPTION": Fore.RED + _("service_status_exception"),
        "START_SENT_UNKNOWN": Fore.CYAN + _("service_status_start_pending"), # Map intermediate states
        "STOP_SENT_UNKNOWN": Fore.CYAN + _("service_status_stop_pending"),  # Map intermediate states
    }
    return status_map.get(status_code, Fore.MAGENTA + str(status_code))


def control_anydesk_service(action="status"):
    """Управляет службой AnyDesk (status, start, stop). Возвращает статус."""
    if action not in ["status", "start", "stop"]:
        print(Style.BRIGHT + Fore.RED + _("service_invalid_action"))
        logger.error(f"Недопустимое действие для control_anydesk_service: {action}")
        return "INVALID_ACTION"

    if action != "status":
        print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("service_control_action", action=action))
    logger.info(f"Выполнение действия '{action}' для службы AnyDesk.")

    final_status = "NOT_FOUND"

    for service_name in ANYDESK_SERVICE_NAMES:
        try:
            logger.debug(f"Попытка '{action}' для службы '{service_name}'...")
            command = ["sc", action, service_name] if action != "status" else ["sc", "query", service_name]

            result = subprocess.run(command, capture_output=True, text=True, encoding='cp866', errors='ignore', check=False)

            logger.debug(f"Команда: {' '.join(command)}")
            logger.debug(f"  Код возврата: {result.returncode}")
            logger.debug(f"  stdout: {result.stdout.strip()}")
            logger.debug(f"  stderr: {result.stderr.strip()}")

            output_lower = result.stdout.lower() if result.stdout else ""
            error_output = result.stderr.lower() if result.stderr else ""

            if "1060:" in error_output or "does not exist" in error_output:
                logger.info(f"Служба '{service_name}' не найдена (код 1060).")
                continue

            if "5:" in error_output or "access is denied" in error_output:
                 if action != "status": print(Style.BRIGHT + Fore.RED + _("service_control_perm_error", name=service_name))
                 logger.error(f"Ошибка прав доступа (5) для службы '{service_name}'.")
                 if final_status == "NOT_FOUND": final_status = "ACCESS_DENIED"
                 continue

            # --- Analysis for existing service ---
            if action == "status":
                if "state" in output_lower:
                    if "running" in output_lower:
                        logger.info(f"Статус службы '{service_name}': Running.")
                        return "RUNNING"
                    elif "stopped" in output_lower:
                        logger.info(f"Статус службы '{service_name}': Stopped.")
                        final_status = "STOPPED"
                    elif "start_pending" in output_lower:
                         logger.info(f"Статус службы '{service_name}': Start Pending.")
                         return "START_PENDING"
                    elif "stop_pending" in output_lower:
                         logger.info(f"Статус службы '{service_name}': Stop Pending.")
                         return "STOP_PENDING"
                    else:
                         state_info = [line for line in output_lower.splitlines() if "state" in line]
                         unknown_state_str = state_info[0].strip() if state_info else "Неизвестное состояние"
                         logger.warning(f"Неизвестное состояние службы '{service_name}': {unknown_state_str}.")
                         if final_status == "NOT_FOUND": final_status = "UNKNOWN_STATE"
                else:
                     logger.warning(f"Не удалось определить состояние службы '{service_name}' (нет 'STATE' в выводе). Код: {result.returncode}.")
                     if final_status == "NOT_FOUND": final_status = "QUERY_FAILED"

            elif action == "start":
                if result.returncode == 0:
                    print(Style.BRIGHT + Fore.GREEN + _("service_control_start_sent", name=f"{Fore.YELLOW}{service_name}{Fore.GREEN}"))
                    logger.info(f"Команда 'sc start {service_name}' успешно отправлена.")
                    print(Style.BRIGHT + Fore.YELLOW + _("service_control_checking_status", name=service_name))
                    time.sleep(3)
                    current_status = control_anydesk_service("status")
                    if current_status == "RUNNING":
                        print(Style.BRIGHT + Fore.LIGHTGREEN_EX + _("service_control_start_confirmed", name=service_name))
                        return "STARTED" # Return a specific success code for start
                    elif current_status == "START_PENDING":
                         print(Style.BRIGHT + Fore.CYAN + _("service_control_start_pending_final", name=service_name))
                         return "START_PENDING"
                    else:
                         print(Style.BRIGHT + Fore.YELLOW + _("service_control_start_status_after", name=service_name, status=current_status))
                         if final_status not in ["STARTED", "ALREADY_RUNNING", "START_PENDING"]:
                             final_status = current_status if current_status != "NOT_FOUND" else "START_SENT_UNKNOWN"

                elif "1056" in error_output or "already running" in error_output:
                     print(Style.BRIGHT + Fore.YELLOW + _("kill_service_already_stopped", name=f"{Fore.WHITE}{service_name}{Fore.YELLOW}")) # Re-use existing translation
                     logger.info(f"Служба '{service_name}' уже запущена (код 1056).")
                     return "ALREADY_RUNNING"
                else:
                     print(Style.BRIGHT + Fore.RED + _("service_control_start_error", name=service_name, code=result.returncode))
                     logger.error(f"Не удалось запустить службу '{service_name}'. Код sc: {result.returncode}. stderr: {result.stderr.strip()}")
                     if final_status not in ["STARTED", "ALREADY_RUNNING", "START_PENDING"]: final_status = "START_FAILED"

            elif action == "stop":
                if result.returncode == 0:
                    print(Style.BRIGHT + Fore.GREEN + _("service_control_stop_sent", name=f"{Fore.YELLOW}{service_name}{Fore.GREEN}"))
                    logger.info(f"Команда 'sc stop {service_name}' успешно отправлена.")
                    print(Style.BRIGHT + Fore.YELLOW + _("service_control_checking_status", name=service_name))
                    time.sleep(3)
                    current_status = control_anydesk_service("status")
                    if current_status == "STOPPED":
                        print(Style.BRIGHT + Fore.LIGHTGREEN_EX + _("service_control_stop_confirmed", name=service_name))
                        return "STOPPED_OK" # Return specific success code for stop
                    elif current_status == "STOP_PENDING":
                         print(Style.BRIGHT + Fore.CYAN + _("service_control_stop_pending_final", name=service_name))
                         return "STOP_PENDING"
                    else:
                         print(Style.BRIGHT + Fore.YELLOW + _("service_control_stop_status_after", name=service_name, status=current_status))
                         if final_status not in ["STOPPED_OK", "ALREADY_STOPPED", "STOP_PENDING"]:
                             final_status = current_status if current_status != "NOT_FOUND" else "STOP_SENT_UNKNOWN"

                elif "1062" in error_output or "has not been started" in error_output:
                    print(Style.BRIGHT + Fore.YELLOW + _("kill_service_already_stopped", name=f"{Fore.WHITE}{service_name}{Fore.YELLOW}"))
                    logger.info(f"Служба '{service_name}' уже остановлена (код 1062).")
                    final_status = "ALREADY_STOPPED"
                else:
                    print(Style.BRIGHT + Fore.RED + _("service_control_stop_error", name=service_name, code=result.returncode))
                    logger.error(f"Не удалось остановить службу '{service_name}'. Код sc: {result.returncode}. stderr: {result.stderr.strip()}")
                    if final_status not in ["STOPPED_OK", "ALREADY_STOPPED", "STOP_PENDING"]: final_status = "STOP_FAILED"

            # Break loop if a definitive action succeeded for this service name
            if action != "status" and final_status in ["STARTED", "ALREADY_RUNNING", "STOPPED_OK", "ALREADY_STOPPED"]:
                 logger.debug(f"Действие '{action}' успешно выполнено для службы '{service_name}'. Прерывание поиска других имен.")
                 # Return the final success status directly
                 if action == "start" and final_status in ["STARTED", "ALREADY_RUNNING"]: return final_status
                 if action == "stop" and final_status in ["STOPPED_OK", "ALREADY_STOPPED"]: return final_status

        except FileNotFoundError:
            print(Style.BRIGHT + Fore.RED + _("kill_sc_not_found"))
            logger.error("Команда 'sc' не найдена.")
            return "SC_NOT_FOUND"
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
            logger.exception(f"Непредвиденная ошибка при управлении службой '{service_name}' ({action}): {e}")
            if final_status == "NOT_FOUND": final_status = "EXCEPTION"

    logger.info(f"Итоговый результат для действия '{action}': {final_status}")
    return final_status


# --- Основная логика и меню ---

try:
    anydesk_text = pyfiglet.figlet_format(_("main_title_anydesk"), font="slant")
    utils_text = pyfiglet.figlet_format(_("main_title_utils"), font="slant")
    anydesk_colored = Style.BRIGHT + Fore.RED + anydesk_text + Style.RESET_ALL
    utils_colored = Style.BRIGHT + Fore.CYAN + utils_text + Style.RESET_ALL
except Exception as e:
     logger.warning(f"Не удалось создать ASCII лого: {e}")
     anydesk_colored = Style.BRIGHT + Fore.RED + _("main_title_anydesk")
     utils_colored = Style.BRIGHT + Fore.CYAN + _("main_title_utils")


def main_cleanup(auto_mode=False):
    """Основная последовательность очистки и переустановки AnyDesk."""
    mode_key = "cleanup_mode_automatic" if auto_mode else "cleanup_mode_interactive"
    mode_color = Fore.YELLOW if auto_mode else Fore.CYAN
    print(Style.BRIGHT + Fore.MAGENTA + _("cleanup_main_start_mode", mode=f"{mode_color}{_(mode_key)}{Fore.MAGENTA}"))
    logger.info(f"Начало {_(mode_key)} очистки AnyDesk.")
    if not auto_mode:
        print(Style.BRIGHT + Fore.YELLOW + _("cleanup_intro_interactive"))

    def confirm_step(prompt_key):
        if auto_mode:
            logger.info(f"Автоматическое подтверждение шага: {prompt_key}")
            print(f"{Style.BRIGHT + Fore.WHITE}{_(prompt_key)}{Fore.GREEN}{_('cleanup_step_confirm_auto', prompt='')}") # Pass empty prompt to avoid double text
            return True
        else:
            # Pass the key directly to ask_yes_no
            return ask_yes_no(prompt_key)

    if confirm_step("cleanup_step1_prompt"):
        killing_anydesk()
    else:
        print(Style.BRIGHT + Fore.YELLOW + _("cleanup_step1_skip"))
        logger.info("Пропуск остановки AnyDesk.")

    if confirm_step("cleanup_step2_prompt"):
        backup_user_conf()
    else:
        print(Style.BRIGHT + Fore.YELLOW + _("cleanup_step2_skip"))
        logger.info("Пропуск создания бэкапа user.conf.")

    if confirm_step("cleanup_step3_prompt"):
        remove_anydesk(confirm=(not auto_mode))
    else:
        print(Style.BRIGHT + Fore.YELLOW + _("cleanup_step3_skip"))
        logger.info("Пропуск удаления файлов AnyDesk.")

    installation_succeeded = False
    installer_to_use = None

    if confirm_step("cleanup_step4_prompt"):
        if auto_mode:
            logger.info("Автоматический режим: попытка скачать установщик.")
            installer_to_use = download_latest_anydesk()
            if installer_to_use:
                logger.info(f"Установщик скачан: {installer_to_use}. Попытка тихой установки.")
                installation_succeeded = install_anydesk(installer_path_param=installer_to_use, silent=True)
            else:
                logger.error("Автоматический режим: не удалось скачать установщик, установка пропущена.")
                print(Style.BRIGHT + Fore.RED + _("cleanup_step4_auto_download_fail"))
        else:
            installation_succeeded = install_anydesk(silent=False)

        if not installation_succeeded:
            logger.warning("Установка AnyDesk не удалась или была отменена.")
            # Error messages are printed inside install_anydesk
    else:
        print(Style.BRIGHT + Fore.YELLOW + _("cleanup_step4_skip"))
        logger.info("Пропуск установки AnyDesk.")

    if confirm_step("cleanup_step5_prompt"):
        restore_user_conf_default()
    else:
        print(Style.BRIGHT + Fore.YELLOW + _("cleanup_step5_skip"))
        logger.info("Пропуск восстановления user.conf.")

    if confirm_step("cleanup_step6_prompt"):
         id_changer_question() # Handles its own messages/logging for skipping
    else:
        # Log skipping step 6 explicitly
        logger.info("Пропуск смены ID (пользователь отказался от шага 6).")


    if installation_succeeded:
        if confirm_step("cleanup_step7_prompt"):
             run_anydesk()
        else:
            print(Style.BRIGHT + Fore.YELLOW + _("cleanup_step7_skip"))
            logger.info("Пропуск запуска AnyDesk после установки.")
    elif not auto_mode:
        print(Style.BRIGHT + Fore.YELLOW + _("cleanup_step7_skip_no_install"))
        logger.info("Запуск AnyDesk пропущен (установка не удалась/пропущена).")

    print(Style.BRIGHT + Fore.MAGENTA + _("cleanup_main_end_mode", mode=f"{mode_color}{_(mode_key)}{Fore.MAGENTA}"))
    logger.info(f"{_(mode_key)} очистка AnyDesk завершена.")
    print(Style.BRIGHT + Fore.LIGHTGREEN_EX + _("cleanup_finished"))


# --- Точка входа ---
if __name__ == "__main__":
    # Language already selected at the top
    logger.info("Проверка прав администратора...")
    if not is_admin():
       print(Style.BRIGHT + Fore.RED + "="*60)
       print(Style.BRIGHT + Fore.YELLOW + _("admin_rights_required"))
       print(Style.BRIGHT + Fore.CYAN +   _("restarting_with_admin"))
       print(Style.BRIGHT + Fore.RED + "="*60)
       logger.warning("Недостаточно прав администратора. Попытка перезапуска.")
       try:
           script_path = os.path.abspath(sys.argv[0])
           params = " ".join([f'"{p}"' for p in sys.argv[1:]])
           logger.debug(f"Перезапуск с правами: Исполняемый файл: {sys.executable}, Скрипт: {script_path}, Параметры: {params}")

           result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}" {params}', None, 1)
           logger.debug(f"Результат ShellExecuteW: {result}")

           if result <= 32:
               error_codes_en = { # English error codes for logging/fallback
                   0: "The operating system is out of memory or resources.",
                   2: "The specified file was not found.",
                   3: "The specified path was not found.",
                   5: "Access is denied.", # Often UAC denial
                   8: "There is not enough memory to complete the operation.",
                   27: "The disk is full.",
                   31: "A device attached to the system is not functioning.",
                   32: "The process cannot access the file because it is being used by another process."
               }
               error_codes_ru = { # Russian for display
                   0: "Операционная система испытывает нехватку памяти или ресурсов.",
                   2: "Указанный файл не найден.",
                   3: "Указанный путь не найден.",
                   5: "Отказано в доступе.", # Часто означает отказ пользователя в UAC
                   8: "Недостаточно памяти для завершения операции.",
                   27: "Диск переполнен.",
                   31: "К системе не подключено устройство.",
                   32: "Процесс не может получить доступ к файлу, так как этот файл занят другим процессом."
               }
               # Get message based on current language
               error_message = MESSAGES.get(f"shellexec_error_{result}", {}).get(lang_choice,
                                 error_codes_ru.get(result, f"Неизвестная ошибка ShellExecuteW ({result})"))
               print(Style.BRIGHT + Fore.RED + _("restart_failed_code", code=result, message=error_message))
               logger.error(f"Не удалось запросить повышение прав через ShellExecuteW. Код ошибки: {result} - {error_codes_en.get(result, 'Unknown ShellExecuteW error')}")
               print(Style.BRIGHT + Fore.YELLOW + _("restart_failed_manual"))
               if sys.stdin.isatty(): input(_("press_enter_to_continue"))
               sys.exit(1)
           else:
               logger.info("Запрос на повышение прав отправлен успешно (или права уже есть). Текущий процесс завершается.")
               sys.exit(0)
       except Exception as e:
           print(Style.BRIGHT + Fore.RED + _("restart_critical_error", error=e))
           logger.critical(f"Критическая ошибка при перезапуске с правами администратора: {e}", exc_info=True)
           if sys.stdin.isatty(): input(_("press_enter_to_continue"))
           sys.exit(1)

    print(Style.BRIGHT + Fore.GREEN + _("admin_rights_confirmed"))
    logger.info("Скрипт запущен с правами администратора.")

    # --- Главный цикл меню ---
    while True:
        current_backup_folder = os.path.dirname(get_current_backup_path())
        logger.debug(f"Текущая папка для бэкапов: {current_backup_folder}")

        print("\n\n" + Style.BRIGHT + Fore.MAGENTA + "="*70)
        print(anydesk_colored + " " + utils_colored)
        print(Style.BRIGHT + Fore.WHITE + _("main_author_info"))
        print(Style.BRIGHT + Fore.BLUE + _("main_backup_folder_info", folder=f"{Fore.YELLOW}{current_backup_folder}{Style.BRIGHT+Fore.BLUE}"))
        print(Style.BRIGHT + Fore.CYAN + _("main_menu_title"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("main_menu_option1_cleanup"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("main_menu_option2_utils"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("main_menu_option3_backup"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + "  4. FAQ")
        print(Style.BRIGHT + Fore.LIGHTRED_EX +    "  5. Exit")
        print(Style.BRIGHT + Fore.MAGENTA + "="*70)

        main_choice = input(
            Style.BRIGHT + Fore.LIGHTCYAN_EX + _("main_menu_enter_choice").replace("(1-4)", "(1-5)")).strip()
        logger.info(f"Выбор в главном меню: {main_choice}")

        if main_choice == '1':
            # --- Подменю Очистки ---
            while True:
                print("\n" + Style.BRIGHT + Fore.CYAN + "-"*60)
                print(Style.BRIGHT + Fore.CYAN + _("submenu_cleanup_title"))
                print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("submenu_cleanup_option_a"))
                # Format option b with color codes INSIDE the translation call if needed, or apply outside. Applying outside is safer.
                print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("submenu_cleanup_option_b").replace("DANGEROUS!", f"{Fore.RED}DANGEROUS!{Fore.LIGHTYELLOW_EX}").replace("ОПАСНО!", f"{Fore.RED}ОПАСНО!{Fore.LIGHTYELLOW_EX}"))
                print(Style.BRIGHT + Fore.LIGHTRED_EX +    _("submenu_cleanup_option_c"))
                print(Style.BRIGHT + Fore.CYAN + "-"*60)
                cleanup_choice = input(Style.BRIGHT + Fore.LIGHTCYAN_EX + _("submenu_cleanup_enter_choice")).strip().lower()
                logger.info(f"Выбор в подменю очистки: {cleanup_choice}")

                if cleanup_choice == 'a':
                    main_cleanup(auto_mode=False)
                    break
                elif cleanup_choice == 'b':
                    print(Style.BRIGHT + Fore.RED + _("submenu_cleanup_auto_warning_title"))
                    print(Style.BRIGHT + Fore.YELLOW + _("submenu_cleanup_auto_warning_details"))
                    logger.warning("Запрос подтверждения автоматической очистки.")
                    if ask_yes_no("submenu_cleanup_auto_confirm"):
                        logger.info("Пользователь подтвердил запуск автоматической очистки.")
                        main_cleanup(auto_mode=True)
                    else:
                        print(Style.BRIGHT + Fore.YELLOW + _("submenu_cleanup_auto_cancelled"))
                        logger.info("Пользователь отменил запуск автоматической очистки.")
                    break
                elif cleanup_choice == 'c':
                    print(Style.BRIGHT + Fore.YELLOW + _("submenu_return_to_main"))
                    logger.info("Возврат в главное меню из подменю очистки.")
                    break
                else:
                     print(Style.BRIGHT + Fore.RED + _("submenu_cleanup_invalid_choice"))
                     logger.warning(f"Неверный выбор в меню очистки: {cleanup_choice}")

        elif main_choice == '2':
             # --- Подменю Утилит ---
             while True:
                print("\n" + Style.BRIGHT + Fore.CYAN + "-"*60)
                print(Style.BRIGHT + Fore.CYAN + _("submenu_utils_title"))

                logger.debug("Запрос статуса службы для меню...")
                service_status_raw = control_anydesk_service("status")
                service_status_display = get_service_status_display(service_status_raw) # Get display string

                logger.debug("Запрос статуса автозапуска для меню...")
                autostart_display = get_autostart_status_display() # Get display string

                opt_color = Style.BRIGHT + Fore.LIGHTYELLOW_EX
                reset_color = opt_color # To reset color after status

                print(Style.BRIGHT + Fore.GREEN +   _("submenu_utils_section_service"))
                print(f"{opt_color}  a. {_('kill_attempting_service').split('...')[0].strip()}") # Use translation key, trim
                print(f"{opt_color}  b. {_('service_control_action', action='start').split('...')[0].strip()}")
                print(f"{opt_color}  c. {_('service_control_action', action='stop').split('...')[0].strip()}")
                print(f"{opt_color}  d. {_('submenu_utils_option_d_status_svc', status=service_status_display + reset_color)}")

                print(Style.BRIGHT + Fore.GREEN +   _("submenu_utils_section_app"))
                print(f"{opt_color}  e. {_('run_starting').split('...')[0].strip()}")
                print(f"{opt_color}  f. {_('id_change_starting').split('...')[0].strip()}")

                print(Style.BRIGHT + Fore.GREEN +   _("submenu_utils_section_windows"))
                print(f"{opt_color}  g. {_('autostart_setting_action', action=_('autostart_action_enabling')).split('...')[0].strip()}")
                print(f"{opt_color}  h. {_('autostart_setting_action', action=_('autostart_action_disabling')).split('...')[0].strip()}")
                print(f"{opt_color}  i. {_('submenu_utils_option_i_status_autostart', status=autostart_display + reset_color)}")

                print(Style.BRIGHT + Fore.GREEN +   _("submenu_utils_section_install"))
                print(f"{opt_color}  j. {_('download_starting').split('...')[0].strip()}")
                print(f"{opt_color}  k. {_('find_path_searching').split('...')[0].strip()}") # Use translation key

                print(Style.BRIGHT + Fore.LIGHTRED_EX +    _("submenu_utils_option_z_exit"))
                print(Style.BRIGHT + Fore.CYAN + "-"*60)

                util_choice = input(Style.BRIGHT + Fore.LIGHTCYAN_EX + _("submenu_utils_enter_choice")).strip().lower()
                logger.info(f"Выбор в меню утилит: {util_choice}")

                if util_choice == 'a': killing_anydesk()
                elif util_choice == 'b': control_anydesk_service("start")
                elif util_choice == 'c': control_anydesk_service("stop")
                elif util_choice == 'd':
                    print(Style.BRIGHT + Fore.YELLOW + _("submenu_utils_checking_svc_status"))
                    status_code = control_anydesk_service("status")
                    status_disp = get_service_status_display(status_code)
                    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("submenu_utils_current_svc_status", status=status_disp))
                elif util_choice == 'e': run_anydesk()
                elif util_choice == 'f': id_changer_question()
                elif util_choice == 'g': set_autostart_registry(enable=True)
                elif util_choice == 'h': set_autostart_registry(enable=False)
                elif util_choice == 'i':
                    print(Style.BRIGHT + Fore.YELLOW + _("submenu_utils_checking_autostart_status"))
                    status_text = get_autostart_status_display()
                    print(Style.BRIGHT + Fore.LIGHTBLUE_EX + _("submenu_utils_current_autostart_status", status=status_text))
                elif util_choice == 'j': download_latest_anydesk()
                elif util_choice == 'k':
                    path = find_anydesk_installation_path()
                    if not path:
                         print(Style.BRIGHT + Fore.YELLOW + _("submenu_utils_path_not_found"))
                elif util_choice == 'z':
                     print(Style.BRIGHT + Fore.YELLOW + _("submenu_return_to_main"))
                     logger.info("Возврат в главное меню из утилит.")
                     break
                else:
                     print(Style.BRIGHT + Fore.RED + _("submenu_utils_invalid_choice"))
                     logger.warning(f"Неверный выбор в меню утилит: {util_choice}")

                if sys.stdin.isatty(): input(Fore.CYAN + _("press_enter_to_continue"))

        elif main_choice == '3':
             # --- Подменю Бэкапа/Восстановления ---
             while True:
                print("\n" + Style.BRIGHT + Fore.CYAN + "-"*60)
                print(Style.BRIGHT + Fore.CYAN + _("submenu_backup_title"))
                opt_color = Style.BRIGHT + Fore.LIGHTYELLOW_EX
                cat_color = Style.BRIGHT + Fore.GREEN

                conf_backup_path_display = get_current_backup_path()
                rec_backup_path_display = get_current_recordings_backup_path()
                print(Style.BRIGHT + Fore.BLUE + _("submenu_backup_conf_path_info", path=f"{Fore.YELLOW}{conf_backup_path_display}{Style.BRIGHT+Fore.BLUE}"))
                print(Style.BRIGHT + Fore.BLUE + _("submenu_backup_rec_path_info", path=f"{Fore.YELLOW}{rec_backup_path_display}{Style.BRIGHT+Fore.BLUE}"))


                print(cat_color +   _("submenu_backup_section_conf"))
                print(f"{opt_color}  a. {_('submenu_backup_option_a_backup_conf')}")
                print(f"{opt_color}  b. {_('submenu_backup_option_b_restore_conf')}")

                print(cat_color +   _("submenu_backup_section_rec"))
                print(f"{opt_color}  c. {_('submenu_backup_option_c_backup_rec')}")
                print(f"{opt_color}  d. {_('submenu_backup_option_d_restore_rec')}")

                print(cat_color +   _("submenu_backup_section_settings"))
                print(f"{opt_color}  e. {_('submenu_backup_option_e_change_folder')}")

                print(Style.BRIGHT + Fore.LIGHTRED_EX +    _("submenu_backup_option_f_exit"))
                print(Style.BRIGHT + Fore.CYAN + "-"*60)

                backup_choice = input(Style.BRIGHT + Fore.LIGHTCYAN_EX + _("submenu_backup_enter_choice")).strip().lower()
                logger.info(f"Выбор в меню резервных копий: {backup_choice}")

                if backup_choice == 'a': backup_user_conf()
                elif backup_choice == 'b': restore_user_conf_interactive()
                elif backup_choice == 'c': backup_screen_recordings()
                elif backup_choice == 'd': restore_screen_recordings()
                elif backup_choice == 'e': set_backup_location_interactive()
                elif backup_choice == 'f':
                     print(Style.BRIGHT + Fore.YELLOW + _("submenu_return_to_main"))
                     logger.info("Возврат в главное меню из бэкапов.")
                     break
                else:
                     print(Style.BRIGHT + Fore.RED + _("submenu_backup_invalid_choice"))
                     logger.warning(f"Неверный выбор в меню бэкапа: {backup_choice}")

                if sys.stdin.isatty(): input(Fore.CYAN + _("press_enter_to_continue"))

        elif main_choice == '4':
            faq.display_faq()
            if sys.stdin.isatty(): input(Fore.CYAN + _("press_enter_to_continue"))  # Пауза после FAQ

        elif main_choice == '5': # Выход
            print(Style.BRIGHT + Fore.GREEN + _("exiting_program"))
            logger.info("Завершение работы скрипта по команде пользователя.")
            break
        else:
             print(Style.BRIGHT + Fore.RED + _("main_invalid_choice"))
             logger.warning(f"Неверный выбор в главном меню: {main_choice}")
             if sys.stdin.isatty(): input(Fore.CYAN + _("main_press_enter_to_return"))


    logger.info("="*30 + " Завершение скрипта AnyDesk Utils " + "="*30)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)