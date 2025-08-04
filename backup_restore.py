import os
import shutil
import logging
import sys
import zipfile
from colorama import init, Fore, Style
import tkinter as tk
from tkinter import filedialog

try:
    from translations import _, set_language, MESSAGES, CURRENT_LANGUAGE
except ImportError:
    print("Error: translations.py not found. Using default English strings.")
    # Define a fallback _ function if import fails
    def _(key, **kwargs):
        # Simple fallback returning the key or a basic message
        return MESSAGES.get(key, {}).get('en', key).format(**kwargs) if kwargs else MESSAGES.get(key, {}).get('en', key)
    # Set default language if not imported
    CURRENT_LANGUAGE = "en"
    def set_language(lang): pass # No-op


init(autoreset=True)
logger = logging.getLogger(__name__)

# --- Константы и глобальные переменные ---
USER_CONF_PATH = os.path.expandvars(r"%APPDATA%\AnyDesk\user.conf")
DEFAULT_BACKUP_DIR = os.path.expanduser("~/Desktop")
_backup_filename = "user.conf.backup"
DEFAULT_RECORDINGS_DIR = os.path.join(os.path.expanduser("~"), "Videos", "AnyDesk", "screen recordings")
RECORDINGS_BACKUP_FILENAME_BASE = "AnyDesk_Screen_Recordings_Backup"

_current_backup_dir = DEFAULT_BACKUP_DIR

# --- Функции для управления путем бэкапа ---

def get_current_backup_path():
    """Возвращает полный путь к файлу бэкапа user.conf в текущей выбранной директории."""
    return os.path.join(_current_backup_dir, _backup_filename)

def get_current_recordings_backup_path():
    """Возвращает полный путь к файлу бэкапа записей (.zip) в текущей выбранной директории."""
    return os.path.join(_current_backup_dir, RECORDINGS_BACKUP_FILENAME_BASE + ".zip")

def set_backup_location_interactive():
    """Интерактивно запрашивает у пользователя новую папку для бэкапов."""
    global _current_backup_dir
    print(Style.BRIGHT + Fore.CYAN + _("br_change_backup_loc_current", folder=f"{Fore.YELLOW}{_current_backup_dir}"))
    logger.info(f"Текущая папка для бэкапов: {_current_backup_dir}")

    while True:
        choice = input(Style.BRIGHT + Fore.CYAN + _("yes_no_prompt", prompt=_("br_change_backup_loc_ask"))).strip().lower()
        if choice in ['y', 'n']:
            break
        else:
            print(Style.BRIGHT + Fore.RED + _("invalid_yes_no"))
            logger.warning("Неверный ввод при выборе папки бэкапа (ожидалось y/n).")

    if choice == 'y':
        logger.info("Пользователь выбрал изменить папку бэкапа.")
        print(Style.BRIGHT + Fore.YELLOW + _("br_change_backup_loc_select_prompt"))
        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        selected_dir = filedialog.askdirectory(
            title=_("br_change_backup_loc_title"),
            initialdir=_current_backup_dir
        )
        root.destroy()

        if selected_dir:
            logger.info(f"Пользователь выбрал папку: {selected_dir}")
            if os.access(selected_dir, os.W_OK):
                _current_backup_dir = selected_dir
                print(Style.BRIGHT + Fore.GREEN + _("br_change_backup_loc_success", folder=f"{Fore.YELLOW}{_current_backup_dir}"))
                logger.info(f"Новая папка для бэкапов установлена: {_current_backup_dir}")
            else:
                print(Style.BRIGHT + Fore.RED + _("br_change_backup_loc_no_write", folder=selected_dir))
                print(Style.BRIGHT + Fore.YELLOW + _("br_change_backup_loc_not_changed"))
                logger.error(f"Нет прав на запись в выбранную папку '{selected_dir}'. Папка не изменена.")
        else:
            print(Style.BRIGHT + Fore.YELLOW + _("br_change_backup_loc_cancelled"))
            logger.info("Выбор папки отменен пользователем.")
    else:
         print(Style.BRIGHT + Fore.GREEN + _("br_change_backup_loc_no_change"))
         logger.info("Пользователь оставил папку для бэкапов без изменений.")

# --- Основные функции бэкапа и восстановления ---

def backup_user_conf():
    """Создает резервную копию файла user.conf."""
    backup_path = get_current_backup_path()
    backup_dir = os.path.dirname(backup_path)
    conf_filename = os.path.basename(USER_CONF_PATH)
    print(Style.BRIGHT + Fore.CYAN + _("br_backup_conf_starting", filename=f"{Fore.YELLOW}{conf_filename}{Fore.CYAN}", path=f"{Fore.YELLOW}{backup_path}{Fore.CYAN}"))
    logger.info(f"Начало резервного копирования {conf_filename} в {backup_path}")

    if not os.path.exists(USER_CONF_PATH):
        print(Style.BRIGHT + Fore.YELLOW + _("br_backup_conf_source_missing", path=USER_CONF_PATH))
        logger.warning(f"Исходный файл {USER_CONF_PATH} не найден, бэкап пропущен.")
        return

    try:
        os.makedirs(backup_dir, exist_ok=True)
        shutil.copy2(USER_CONF_PATH, backup_path) # copy2 сохраняет метаданные
        print(Style.BRIGHT + Fore.GREEN + _("br_backup_conf_success", path=f"{Fore.YELLOW}{backup_path}"))
        logger.info(f"Резервная копия {conf_filename} успешно создана/обновлена: {backup_path}")
    except PermissionError:
        print(Style.BRIGHT + Fore.RED + _("br_backup_conf_perm_error", folder=backup_dir))
        print(Style.BRIGHT + Fore.YELLOW + _("br_backup_conf_perm_error_advice"))
        logger.error(f"Ошибка прав доступа при создании бэкапа в '{backup_dir}'.")
    except OSError as e:
         print(Style.BRIGHT + Fore.RED + _("br_backup_conf_os_error", path=backup_path, error=e.strerror, errno=e.errno))
         logger.error(f"Ошибка файловой системы при создании бэкапа {conf_filename} в '{backup_path}': {e}", exc_info=True)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
        logger.exception(f"Непредвиденная ошибка при создании резервной копии {conf_filename}: {e}")


def restore_user_conf_interactive():
    """Интерактивно восстанавливает user.conf."""
    current_default_backup = get_current_backup_path()
    target_dir = os.path.dirname(USER_CONF_PATH)
    conf_filename = os.path.basename(USER_CONF_PATH)

    print(Style.BRIGHT + Fore.CYAN + _("br_restore_conf_starting", filename=f"{Fore.YELLOW}{conf_filename}{Fore.CYAN}", target_dir=f"{Fore.YELLOW}{target_dir}{Fore.CYAN}"))
    logger.info(f"Начало интерактивного восстановления {conf_filename} в {target_dir}")

    while True:
        print(Style.BRIGHT + Fore.CYAN + _("br_restore_conf_ask_source"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_restore_conf_option1", folder=f"{Fore.YELLOW}{_current_backup_dir}{Style.BRIGHT + Fore.LIGHTYELLOW_EX}"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_restore_conf_option2"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_restore_conf_option3"))

        choice = input(Style.BRIGHT + Fore.CYAN + _("enter_your_choice", options="1, 2, 3")).strip()
        logger.debug(f"Пользователь выбрал опцию восстановления user.conf: {choice}")

        if choice not in ['1', '2', '3']:
            print(Style.BRIGHT + Fore.RED + _("invalid_choice_options", options="1, 2, 3"))
            logger.warning("Неверный ввод в меню восстановления user.conf.")
            continue

        backup_source = None
        if choice == '1':
            backup_source = current_default_backup
            if not os.path.exists(backup_source):
                print(Style.BRIGHT + Fore.RED + _("br_restore_conf_default_missing", path=f"{Fore.YELLOW}{backup_source}"))
                print(Style.BRIGHT + Fore.YELLOW + _("br_restore_conf_try_manual"))
                logger.warning(f"Файл бэкапа user.conf не найден в текущей папке: {backup_source}")
                backup_source = None
                continue

        elif choice == '2':
            logger.info("Пользователь выбрал указать файл бэкапа user.conf вручную.")
            print(Style.BRIGHT + Fore.YELLOW + _("br_restore_conf_select_prompt"))
            root = tk.Tk()
            root.attributes('-topmost', True)
            root.withdraw()
            selected_file = filedialog.askopenfilename(
                title=_("br_restore_conf_select_title"),
                filetypes=_("br_restore_conf_filetypes"), # Get list of tuples
                initialdir=_current_backup_dir
            )
            root.destroy()

            if selected_file:
                backup_source = selected_file
                logger.info(f"Пользователь выбрал файл бэкапа: {backup_source}")
            else:
                print(Style.BRIGHT + Fore.YELLOW + _("file_not_selected") + _("submenu_return_to_main"))
                logger.info("Пользователь отменил выбор файла бэкапа user.conf.")
                continue

        elif choice == '3':
            print(Style.BRIGHT + Fore.YELLOW + _("br_restore_conf_cancelled"))
            logger.info("Восстановление user.conf отменено пользователем.")
            return

        if backup_source:
            print(Style.BRIGHT + Fore.GREEN + _("br_restore_conf_file_selected", path=f"'{Fore.YELLOW}{backup_source}{Style.BRIGHT + Fore.GREEN}'"))
            logger.info(f"Попытка восстановления {conf_filename} из {backup_source}")
            try:
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(backup_source, USER_CONF_PATH)
                print(Style.BRIGHT + Fore.GREEN + _("br_restore_conf_success", filename=f"'{Fore.YELLOW}{conf_filename}{Style.BRIGHT + Fore.GREEN}'", target_dir=f"'{Fore.YELLOW}{target_dir}{Style.BRIGHT + Fore.GREEN}'"))
                logger.info(f"Файл {conf_filename} успешно восстановлен из {backup_source} в {target_dir}.")
                return
            except FileNotFoundError:
                 print(Style.BRIGHT + Fore.RED + _("br_restore_conf_source_not_found_final", path=f"'{backup_source}'"))
                 logger.error(f"Исходный файл бэкапа '{backup_source}' не найден при попытке восстановления.")
                 return
            except PermissionError:
                 print(Style.BRIGHT + Fore.RED + _("br_restore_conf_perm_error", source=f"'{backup_source}'", target=f"'{target_dir}'"))
                 logger.error(f"Ошибка прав доступа при восстановлении из '{backup_source}' в '{target_dir}'.")
                 return
            except shutil.SameFileError:
                 print(Style.BRIGHT + Fore.YELLOW + _("br_restore_conf_same_file"))
                 logger.warning("Источник и назначение user.conf совпадают, восстановление пропущено.")
                 return
            except OSError as e:
                 print(Style.BRIGHT + Fore.RED + _("br_restore_conf_os_error", error=e.strerror, errno=e.errno))
                 logger.error(f"Ошибка файловой системы при восстановлении {conf_filename}: {e}", exc_info=True)
                 return
            except Exception as e:
                 print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
                 logger.exception(f"Непредвиденная ошибка при восстановлении {conf_filename}: {e}")
                 return

def restore_user_conf_default():
    """Пытается неинтерактивно восстановить user.conf из текущей папки для бэкапов."""
    backup_path = get_current_backup_path()
    target_dir = os.path.dirname(USER_CONF_PATH)
    conf_filename = os.path.basename(USER_CONF_PATH)
    print(Style.BRIGHT + Fore.CYAN + _("br_restore_conf_auto_starting", filename=f"{Fore.YELLOW}{conf_filename}{Fore.CYAN}", path=f"'{Fore.YELLOW}{backup_path}{Fore.CYAN}'"))
    logger.info(f"Попытка автоматического восстановления {conf_filename} из {backup_path}")

    if not os.path.exists(backup_path):
        print(Style.BRIGHT + Fore.YELLOW + _("br_restore_conf_auto_not_found", path=backup_path))
        logger.warning(f"Файл бэкапа user.conf не найден в '{backup_path}', автоматическое восстановление пропущено.")
        return

    try:
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(backup_path, USER_CONF_PATH)
        print(Style.BRIGHT + Fore.GREEN + _("br_restore_conf_auto_success"))
        logger.info(f"Конфигурация {conf_filename} успешно восстановлена из {backup_path}.")
    except FileNotFoundError:
         print(Style.BRIGHT + Fore.RED + _("br_restore_conf_auto_source_missing_final", path=f"'{backup_path}'"))
         logger.error(f"Файл бэкапа '{backup_path}' внезапно не найден при автоматическом восстановлении.")
    except PermissionError:
        print(Style.BRIGHT + Fore.RED + _("br_restore_conf_auto_perm_error", source=f"'{backup_path}'", target=f"'{target_dir}'"))
        logger.error(f"Ошибка прав доступа при автоматическом восстановлении из '{backup_path}' в '{target_dir}'.")
    except shutil.SameFileError:
        print(Style.BRIGHT + Fore.YELLOW + _("br_restore_conf_same_file"))
        logger.warning("Источник и назначение user.conf совпадают при автоматическом восстановлении, пропущено.")
    except OSError as e:
        print(Style.BRIGHT + Fore.RED + _("br_restore_conf_auto_os_error", error=e.strerror, errno=e.errno))
        logger.error(f"Ошибка файловой системы при автоматическом восстановлении {conf_filename}: {e}", exc_info=True)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
        logger.exception(f"Непредвиденная ошибка при автоматическом восстановлении {conf_filename}: {e}")


def select_directory(prompt_title_key, initial_dir=None):
    """Вспомогательная функция для выбора директории пользователем."""
    prompt_title_text = _(prompt_title_key) # Translate the key first
    print(Style.BRIGHT + Fore.YELLOW + prompt_title_text)
    logger.info(f"Запрос выбора директории: {prompt_title_text}")
    root = tk.Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    selected_dir = filedialog.askdirectory(title=prompt_title_text, initialdir=initial_dir)
    root.destroy()
    if not selected_dir:
        print(Style.BRIGHT + Fore.YELLOW + _("folder_not_selected"))
        logger.info("Пользователь отменил выбор директории.")
    else:
        logger.info(f"Пользователь выбрал директорию: {selected_dir}")
    return selected_dir

def backup_screen_recordings():
    """Создает ZIP-архив с записями экрана AnyDesk."""
    print(Style.BRIGHT + Fore.MAGENTA + _("br_backup_rec_title"))
    logger.info("Начало резервного копирования записей экрана.")

    # 1. Определяем исходную папку
    recordings_source_dir = None
    print(_("br_backup_rec_default_path_info", path=f"{Fore.YELLOW}{DEFAULT_RECORDINGS_DIR}"))
    logger.debug(f"Стандартный путь к записям: {DEFAULT_RECORDINGS_DIR}")
    while True:
        choice = input(Style.BRIGHT + Fore.CYAN + _("br_backup_rec_ask_source_path")).strip().lower()
        logger.debug(f"Выбор источника записей: {choice}")
        if choice == 'd':
            recordings_source_dir = DEFAULT_RECORDINGS_DIR
            if not os.path.isdir(recordings_source_dir):
                 print(Style.BRIGHT + Fore.RED + _("br_backup_rec_source_default_not_found", path=recordings_source_dir))
                 print(Style.BRIGHT + Fore.YELLOW + _("br_backup_rec_cancelled"))
                 logger.error(f"Стандартная папка записей не найдена: {recordings_source_dir}. Бэкап отменен.")
                 return
            break
        elif choice == 'c':
            recordings_source_dir = select_directory("br_backup_rec_select_source_title", os.path.dirname(DEFAULT_RECORDINGS_DIR))
            if not recordings_source_dir:
                 logger.info("Бэкап записей отменен (папка не выбрана).")
                 return
            if not os.path.isdir(recordings_source_dir):
                 print(Style.BRIGHT + Fore.RED + _("br_backup_rec_selected_path_invalid", path=recordings_source_dir))
                 logger.error(f"Выбранная папка записей не существует: {recordings_source_dir}. Бэкап отменен.")
                 return
            break
        else:
             print(Style.BRIGHT + Fore.RED + _("invalid_choice"))
             logger.warning("Неверный ввод при выборе источника записей (ожидалось d/c).")

    print(_("br_backup_rec_source_folder_info", path=f"{Fore.YELLOW}{recordings_source_dir}"))
    logger.info(f"Исходная папка для бэкапа записей: {recordings_source_dir}")

    try:
        # Проверка на пустоту ДО вычисления пути архива
        if not os.listdir(recordings_source_dir):
             print(Style.BRIGHT + Fore.YELLOW + _("br_backup_rec_source_empty"))
             logger.warning("Исходная папка записей пуста, бэкап пропущен.")
             return
    except FileNotFoundError:
        # Если папка исчезла между выбором и проверкой
        print(Style.BRIGHT + Fore.RED + _("error_folder_not_found", path=f"'{recordings_source_dir}'"))
        logger.error(f"Исходная папка записей '{recordings_source_dir}' не найдена перед созданием архива.")
        return
    except OSError as e:
        print(Style.BRIGHT + Fore.RED + _("br_backup_rec_source_access_error", path=f"'{recordings_source_dir}'", error=e.strerror))
        logger.error(f"Ошибка доступа к исходной папке записей '{recordings_source_dir}': {e}", exc_info=True)
        return


    # 2. Определяем путь для сохранения архива
    backup_archive_base = os.path.join(_current_backup_dir, RECORDINGS_BACKUP_FILENAME_BASE)
    backup_archive_path = backup_archive_base + ".zip"
    print(_("br_backup_rec_archive_path_info", path=f"{Fore.YELLOW}{backup_archive_path}"))
    logger.info(f"Путь для сохранения архива записей: {backup_archive_path}")

    if os.path.exists(backup_archive_path):
         print(Style.BRIGHT + Fore.YELLOW + _("br_backup_rec_archive_exists_warn",
                filename=f"'{Fore.WHITE}{os.path.basename(backup_archive_path)}{Style.BRIGHT + Fore.YELLOW}'",
                folder=f"'{Fore.WHITE}{os.path.dirname(backup_archive_path)}{Style.BRIGHT + Fore.YELLOW}'"))
         logger.warning(f"Архив бэкапа записей '{backup_archive_path}' уже существует.")
         if input(Style.BRIGHT + Fore.CYAN + _("yes_no_prompt", prompt=_("br_backup_rec_archive_overwrite_confirm"))).strip().lower() != 'y':
              print(Style.BRIGHT + Fore.YELLOW + _("br_backup_rec_cancelled"))
              logger.info("Пользователь отменил перезапись архива, бэкап записей отменен.")
              return
         logger.info("Пользователь подтвердил перезапись архива.")

    # 3. Создаем архив
    try:
        print(Style.BRIGHT + Fore.YELLOW + _("br_backup_rec_creating_archive"))
        logger.info("Начало создания ZIP-архива записей.")
        # Убедимся, что папка для архива существует
        os.makedirs(os.path.dirname(backup_archive_path), exist_ok=True)
        shutil.make_archive(base_name=backup_archive_base,
                              format='zip',
                              root_dir=recordings_source_dir)
        print(Style.BRIGHT + Fore.GREEN + _("br_backup_rec_success", path=f"{Fore.YELLOW}{backup_archive_path}"))
        logger.info(f"Резервная копия записей экрана успешно создана: {backup_archive_path}")
    except FileNotFoundError:
        print(Style.BRIGHT + Fore.RED + _("br_backup_rec_source_missing_during_zip", path=f"'{recordings_source_dir}'"))
        logger.error(f"Не удалось найти исходную папку '{recordings_source_dir}' во время архивации записей.")
    except PermissionError:
        print(Style.BRIGHT + Fore.RED + _("br_backup_rec_zip_perm_error"))
        logger.error("Ошибка прав доступа при архивации записей.")
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
        logger.exception(f"Непредвиденная ошибка при создании архива записей: {e}")

def restore_screen_recordings():
    """Восстанавливает записи экрана AnyDesk из ZIP-архива."""
    print(Style.BRIGHT + Fore.MAGENTA + _("br_restore_rec_title"))
    logger.info("Начало восстановления записей экрана.")

    # 1. Определяем источник архива
    backup_archive_path = None
    default_backup_path = get_current_recordings_backup_path()
    print(_("br_restore_rec_default_archive_info", path=f"{Fore.YELLOW}{default_backup_path}"))
    logger.debug(f"Стандартный путь к архиву бэкапа записей: {default_backup_path}")
    while True:
        choice = input(Style.BRIGHT + Fore.CYAN + _("br_restore_rec_ask_archive_source")).strip().lower()
        logger.debug(f"Выбор источника архива записей: {choice}")
        if choice == 'd':
            backup_archive_path = default_backup_path
            if not os.path.isfile(backup_archive_path):
                print(Style.BRIGHT + Fore.RED + _("br_restore_rec_default_archive_missing", path=backup_archive_path))
                print(Style.BRIGHT + Fore.YELLOW + _("br_restore_rec_cancelled"))
                logger.error(f"Архив бэкапа записей не найден по стандартному пути: {backup_archive_path}. Восстановление отменено.")
                return
            break
        elif choice == 'c':
            logger.info("Пользователь выбрал указать архив бэкапа записей вручную.")
            print(Style.BRIGHT + Fore.YELLOW + _("br_restore_rec_select_archive_prompt"))
            root = tk.Tk()
            root.attributes('-topmost', True)
            root.withdraw()
            selected_file = filedialog.askopenfilename(
                title=_("br_restore_rec_select_archive_title"),
                filetypes=_("br_restore_rec_archive_filetypes"),
                initialdir=_current_backup_dir
            )
            root.destroy()
            if not selected_file:
                print(Style.BRIGHT + Fore.YELLOW + _("file_not_selected"));
                logger.info("Восстановление записей отменено (архив не выбран).")
                return
            if not os.path.isfile(selected_file):
                 print(Style.BRIGHT + Fore.RED + _("br_restore_rec_selected_archive_invalid", path=selected_file))
                 logger.error(f"Выбранный архив бэкапа записей не найден: {selected_file}. Восстановление отменено.")
                 return
            backup_archive_path = selected_file
            logger.info(f"Пользователь выбрал архив бэкапа записей: {backup_archive_path}")
            break
        else:
            print(Style.BRIGHT + Fore.RED + _("invalid_choice"))
            logger.warning("Неверный ввод при выборе источника архива записей (ожидалось d/c).")

    print(_("br_restore_rec_using_archive", path=f"{Fore.YELLOW}{backup_archive_path}"))
    logger.info(f"Используется архив для восстановления записей: {backup_archive_path}")

    # 2. Определяем папку назначения
    restore_destination_dir = None
    print(_("br_restore_rec_default_dest_info", path=f"{Fore.YELLOW}{DEFAULT_RECORDINGS_DIR}"))
    logger.debug(f"Стандартный путь назначения для восстановления записей: {DEFAULT_RECORDINGS_DIR}")
    while True:
        choice = input(Style.BRIGHT + Fore.CYAN + _("br_restore_rec_ask_dest_path")).strip().lower()
        logger.debug(f"Выбор папки назначения для записей: {choice}")
        if choice == 'd':
            restore_destination_dir = DEFAULT_RECORDINGS_DIR
            break
        elif choice == 'c':
            restore_destination_dir = select_directory("br_restore_rec_select_dest_title", os.path.dirname(DEFAULT_RECORDINGS_DIR))
            if not restore_destination_dir:
                logger.info("Восстановление записей отменено (папка назначения не выбрана).")
                return
            break
        else:
            print(Style.BRIGHT + Fore.RED + _("invalid_choice"))
            logger.warning("Неверный ввод при выборе папки назначения для записей (ожидалось d/c).")

    print(_("br_restore_rec_dest_folder_info", path=f"{Fore.YELLOW}{restore_destination_dir}"))
    logger.info(f"Папка назначения для восстановления записей: {restore_destination_dir}")

    # 3. Создаем папку назначения и предупреждаем о перезаписи
    try:
        should_warn = False
        if os.path.exists(restore_destination_dir):
            # Проверяем, есть ли *файлы* (а не только папки) в директории
            if any(os.path.isfile(os.path.join(restore_destination_dir, i)) for i in os.listdir(restore_destination_dir)):
                should_warn = True
        else:
             # Если папки нет, создаем ее
             os.makedirs(restore_destination_dir, exist_ok=True)
             logger.debug(f"Папка назначения для записей создана: {restore_destination_dir}")

        if should_warn:
            print(Style.BRIGHT + Fore.YELLOW + _("br_restore_rec_dest_not_empty_warn", path=f"'{Fore.WHITE}{restore_destination_dir}{Style.BRIGHT + Fore.YELLOW}'"))
            # Split warning into two lines for clarity
            print(Style.BRIGHT + Fore.YELLOW + _("br_restore_rec_dest_overwrite_warn").format(Style=Style, Fore=Fore)) # Pass Style/Fore if needed inside translation
            logger.warning(f"Папка назначения '{restore_destination_dir}' для записей не пуста.")
            if input(Style.BRIGHT + Fore.CYAN + _("yes_no_prompt", prompt=_("br_restore_rec_dest_overwrite_confirm"))).strip().lower() != 'y':
                print(Style.BRIGHT + Fore.YELLOW + _("br_restore_rec_cancelled"))
                logger.info("Пользователь отменил восстановление в непустую папку.")
                return
            logger.info("Пользователь подтвердил восстановление в непустую папку.")
        # Если папка существовала, но была пустой, или если ее только что создали, просто продолжаем
        elif os.path.exists(restore_destination_dir):
             logger.debug(f"Папка назначения для записей существует и пуста (или содержит только подпапки): {restore_destination_dir}")


    except OSError as e:
         print(Style.BRIGHT + Fore.RED + _("br_restore_rec_dest_create_error", path=f"'{restore_destination_dir}'", error=e.strerror))
         logger.error(f"Не удалось создать/проверить папку назначения '{restore_destination_dir}': {e}", exc_info=True)
         return

    # 4. Распаковываем архив
    try:
        print(Style.BRIGHT + Fore.YELLOW + _("br_restore_rec_unpacking"))
        logger.info(f"Начало распаковки архива '{backup_archive_path}' в '{restore_destination_dir}'.")
        shutil.unpack_archive(filename=backup_archive_path,
                                extract_dir=restore_destination_dir,
                                format='zip')
        print(Style.BRIGHT + Fore.GREEN + _("br_restore_rec_success", path=f"{Fore.YELLOW}{restore_destination_dir}"))
        logger.info(f"Записи экрана успешно восстановлены из '{backup_archive_path}' в '{restore_destination_dir}'.")
    except FileNotFoundError:
         print(Style.BRIGHT + Fore.RED + _("br_restore_rec_archive_missing_during_unpack", path=f"'{backup_archive_path}'"))
         logger.error(f"Не удалось найти архив '{backup_archive_path}' во время распаковки записей.")
    except PermissionError:
         print(Style.BRIGHT + Fore.RED + _("br_restore_rec_unpack_perm_error"))
         logger.error(f"Ошибка прав доступа при распаковке записей из '{backup_archive_path}' в '{restore_destination_dir}'.")
    except (shutil.ReadError, zipfile.BadZipFile) as e:
         print(Style.BRIGHT + Fore.RED + _("br_restore_rec_archive_read_error", error=e))
         logger.error(f"Ошибка чтения архива '{backup_archive_path}': {e}. Возможно, поврежден.", exc_info=True)
    except Exception as e:
         print(Style.BRIGHT + Fore.RED + _("error_unexpected", error=e), file=sys.stderr)
         logger.exception(f"Непредвиденная ошибка при распаковке архива записей '{backup_archive_path}': {e}")


# --- Точка входа для запуска как отдельного скрипта (для тестов) ---
if __name__ == "__main__":
    # --- Language Selection (Standalone Mode) ---
    # Use simple print before colorama/logging for this initial prompt
    print("Select language (en) / Выберите язык (ru): ", end="")
    lang_choice = input().strip().lower()
    while lang_choice not in ['en', 'ru']:
        print("Invalid choice. Please enter 'en' or 'ru'. / Неверный выбор. Пожалуйста, введите 'en' или 'ru'.")
        print("Select language (en) / Выберите язык (ru): ", end="")
        lang_choice = input().strip().lower()
    set_language(lang_choice)
    # --- End Language Selection ---

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logger.info("Запуск модуля backup_restore как отдельного скрипта.")

    print(Style.BRIGHT + Fore.MAGENTA + _("br_test_mode_title"))
    while True:
        current_backup_path_display = get_current_backup_path()
        current_rec_backup_path = get_current_recordings_backup_path()
        print(Style.BRIGHT + Fore.CYAN + _("br_menu_title"))
        print(Style.BRIGHT + Fore.BLUE + _("br_current_backup_folder_info", folder=f"{Fore.YELLOW}{_current_backup_dir}{Style.BRIGHT+Fore.BLUE}"))
        print(Style.BRIGHT + Fore.GREEN +   _("br_menu_conf_section"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_menu_conf_backup"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_menu_conf_restore"))
        print(Style.BRIGHT + Fore.GREEN +   _("br_menu_rec_section"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_menu_rec_backup"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_menu_rec_restore"))
        print(Style.BRIGHT + Fore.GREEN +   _("br_menu_settings_section"))
        print(Style.BRIGHT + Fore.LIGHTYELLOW_EX + _("br_menu_change_folder"))
        print(Style.BRIGHT + Fore.LIGHTRED_EX +    _("br_menu_exit"))

        choice = input(Style.BRIGHT + Fore.CYAN + _("enter_your_choice", options="1-6")).strip()
        logger.debug(f"Тестовый режим: пользователь выбрал {choice}")

        if choice not in ['1', '2', '3', '4', '5', '6']:
            print(Style.BRIGHT + Fore.RED + _("invalid_choice_range", min=1, max=6))
            logger.warning(f"Тестовый режим: неверный ввод {choice}")
            continue

        if choice == '1':
            backup_user_conf()
        elif choice == '2':
            restore_user_conf_interactive()
        elif choice == '3':
             backup_screen_recordings()
        elif choice == '4':
             restore_screen_recordings()
        elif choice == '5':
             set_backup_location_interactive()
        elif choice == '6':
            print(Style.BRIGHT + Fore.GREEN + _("br_exit_message"))
            logger.info("Завершение работы модуля backup_restore (тестовый режим).")
            break

        if sys.stdin.isatty():
             input(_("press_enter_to_continue"))