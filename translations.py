import os
import sys

# --- Translation Dictionary ---
# Ключи - идентификаторы сообщений
# Значения - словари {'en': "English Text", 'ru': "Русский Текст"}
MESSAGES = {
    # --- General ---
    "select_language_prompt": {
        "en": "Select language (en) / Выберите язык (ru): ",
        "ru": "Выберите язык (ru) / Select language (en): "
    },
    "invalid_language_choice": {
        "en": "Invalid choice. Please enter 'en' or 'ru'.",
        "ru": "Неверный выбор. Пожалуйста, введите 'en' или 'ru'."
    },
    "press_enter_to_continue": {
        "en": "\nPress Enter to continue...",
        "ru": "\nНажмите Enter для продолжения..."
    },
    "error_unexpected": {
        "en": "Unexpected error: {error}",
        "ru": "Непредвиденная ошибка: {error}"
    },
    "error_permission_denied_path": {
        "en": "Error: Permission denied for '{path}'.",
        "ru": "Ошибка прав доступа: Нет доступа к '{path}'."
    },
    "error_permission_denied_action": {
        "en": "Permission Error: Could not {action}.",
        "ru": "Ошибка прав доступа: Не удалось {action}."
    },
    "error_file_not_found": {
        "en": "Error: File not found: '{path}'.",
        "ru": "Ошибка: Файл не найден: '{path}'."
    },
    "error_folder_not_found": {
        "en": "Error: Folder not found: '{path}'.",
        "ru": "Ошибка: Папка не найдена: '{path}'."
    },
    "error_os_error_generic": {
        "en": "File system error: {error} (Code: {errno})",
        "ru": "Ошибка файловой системы: {error} (Код: {errno})"
    },
    "status_success": {
        "en": "Success",
        "ru": "Успешно"
    },
    "status_error": {
        "en": "Error",
        "ru": "Ошибка"
    },
    "status_warning": {
        "en": "Warning",
        "ru": "Предупреждение"
    },
    "status_cancelled": {
        "en": "Cancelled",
        "ru": "Отменено"
    },
    "yes_no_prompt": {
        "en": "{prompt} (y/n): ",
        "ru": "{prompt} (y/n): " # В русском 'y/n' тоже понятно
    },
    "invalid_yes_no": {
        "en": "Invalid input. Please enter 'y' or 'n'.",
        "ru": "Неверный ввод. Пожалуйста, введите 'y' или 'n'."
    },
    "action_cancelled_by_user": {
        "en": "Action cancelled by user.",
        "ru": "Действие отменено пользователем."
    },
    "folder_not_selected": {
        "en": "Folder not selected.",
        "ru": "Папка не выбрана."
    },
    "file_not_selected": {
        "en": "File not selected.",
        "ru": "Файл не выбран."
    },
    "admin_rights_required": {
        "en": "Administrator rights are required for some operations.",
        "ru": "Требуются права администратора для выполнения некоторых операций."
    },
    "admin_rights_check_failed": {
        "en": "Could not determine access rights.",
        "ru": "Не удалось определить права доступа."
    },
    "admin_rights_confirmed": {
        "en": "Administrator rights confirmed.",
        "ru": "Права администратора подтверждены."
    },
    "restarting_with_admin": {
        "en": "Attempting to restart with administrator privileges...",
        "ru": "Попытка перезапуска с запросом прав..."
    },
    "restart_failed_code": {
        "en": "Failed to request elevation (Code: {code} - {message}).",
        "ru": "Не удалось запросить повышение прав (Код: {code} - {message})."
    },
    "restart_failed_manual": {
        "en": "Please run the script manually as an administrator.",
        "ru": "Пожалуйста, запустите скрипт вручную от имени администратора."
    },
    "restart_critical_error": {
        "en": "Critical error while attempting to restart with admin rights: {error}",
        "ru": "Критическая ошибка при попытке перезапуска с правами администратора: {error}"
    },
    "exiting_program": {
        "en": "\nExiting program.",
        "ru": "\nВыход из программы."
    },
    "invalid_choice": {
        "en": "Invalid choice. Please enter a valid option.",
        "ru": "Неверный выбор. Пожалуйста, введите корректный пункт."
    },
    "invalid_choice_range": {
        "en": "Invalid choice. Please enter a number between {min} and {max}.",
        "ru": "Неверный выбор. Пожалуйста, введите число от {min} до {max}."
    },
    "invalid_choice_options": {
        "en": "Invalid choice. Please enter one of the following: {options}",
        "ru": "Неверный выбор. Пожалуйста, введите один из вариантов: {options}"
    },
    "enter_your_choice": {
        "en": "Enter your choice ({options}): ",
        "ru": "Введите ваш выбор ({options}): "
    },

    # --- backup_restore.py Specific ---
    "br_test_mode_title": {
        "en": "--- AnyDesk Backup Management Utility (Test Mode) ---",
        "ru": "--- Утилита управления бэкапами AnyDesk (Тестовый режим) ---"
    },
    "br_menu_title": {
        "en": "\nSelect action:",
        "ru": "\nВыберите действие:"
    },
    "br_current_backup_folder_info": {
        "en": "(Current backup folder: {folder})",
        "ru": "(Текущая папка для бэкапов: {folder})"
    },
    "br_menu_conf_section": {
        "en": "--- Configuration (user.conf) ---",
        "ru": "--- Конфигурация (user.conf) ---"
    },
    "br_menu_conf_backup": {
        "en": "  1. Create/update user.conf backup",
        "ru": "  1. Создать/обновить резервную копию user.conf"
    },
    "br_menu_conf_restore": {
        "en": "  2. Restore user.conf from backup",
        "ru": "  2. Восстановить user.conf из резервной копии"
    },
    "br_menu_rec_section": {
        "en": "--- Screen Recordings ---",
        "ru": "--- Записи экрана ---"
    },
    "br_menu_rec_backup": {
        "en": "  3. Create screen recordings backup (.zip)",
        "ru": "  3. Создать резервную копию записей экрана (в .zip)"
    },
    "br_menu_rec_restore": {
        "en": "  4. Restore screen recordings from backup (.zip)",
        "ru": "  4. Восстановить записи экрана из резервной копии (.zip)"
    },
    "br_menu_settings_section": {
        "en": "--- Settings ---",
        "ru": "--- Настройки ---"
    },
    "br_menu_change_folder": {
        "en": "  5. Change folder for saving/searching backups",
        "ru": "  5. Изменить папку для сохранения/поиска резервных копий"
    },
    "br_menu_exit": {
        "en": "  6. Exit",
        "ru": "  6. Выход"
    },
    "br_exit_message": {
        "en": "\nExiting backup management utility.",
        "ru": "\nВыход из утилиты управления бэкапом."
    },
    "br_change_backup_loc_current": {
        "en": "\nCurrent folder for backups: {folder}",
        "ru": "\nТекущая папка для резервных копий: {folder}"
    },
    "br_change_backup_loc_ask": {
        "en": "Do you want to select a new folder?",
        "ru": "Хотите выбрать новую папку?"
    },
    "br_change_backup_loc_select_prompt": {
        "en": "Please select a folder to save backups.",
        "ru": "Пожалуйста, выберите папку для сохранения резервных копий."
    },
    "br_change_backup_loc_title": {
        "en": "Select Backup Folder",
        "ru": "Выберите папку для бэкапов"
    },
    "br_change_backup_loc_success": {
        "en": "New backup folder set: {folder}",
        "ru": "Новая папка для резервных копий установлена: {folder}"
    },
    "br_change_backup_loc_no_write": {
        "en": "Error: No write permission in the selected folder '{folder}'.",
        "ru": "Ошибка: Нет прав на запись в выбранную папку '{folder}'."
    },
    "br_change_backup_loc_not_changed": {
        "en": "Backup folder was not changed.",
        "ru": "Папка для бэкапов не изменена."
    },
    "br_change_backup_loc_cancelled": {
        "en": "Folder selection cancelled. Using previous value.",
        "ru": "Папка не выбрана. Используется предыдущее значение."
    },
    "br_change_backup_loc_no_change": {
        "en": "Backup folder remains the same.",
        "ru": "Папка для резервных копий осталась прежней."
    },
    "br_backup_conf_starting": {
        "en": "\nCreating backup of '{filename}' to '{path}'...",
        "ru": "\nСоздание резервной копии '{filename}' в '{path}'..."
    },
    "br_backup_conf_source_missing": {
        "en": "Source file {path} not found. Backup skipped.",
        "ru": "Исходный файл {path} не найден. Резервное копирование пропущено."
    },
    "br_backup_conf_success": {
        "en": "Backup successfully created/updated: {path}",
        "ru": "Резервная копия успешно создана/обновлена: {path}"
    },
    "br_backup_conf_perm_error": {
        "en": "Permission Error: Cannot create/write file in folder '{folder}'.",
        "ru": "Ошибка прав доступа: Не удается создать/записать файл в папке '{folder}'."
    },
    "br_backup_conf_perm_error_advice": {
        "en": "Check folder permissions or choose another backup location.",
        "ru": "Проверьте права доступа к папке или выберите другую папку для бэкапов."
    },
    "br_backup_conf_os_error": {
        "en": "File system error during backup to '{path}': {error} (Code: {errno})",
        "ru": "Ошибка файловой системы при создании бэкапа в '{path}': {error} (Код: {errno})"
    },
    "br_restore_conf_starting": {
        "en": "\nRestoring file '{filename}' to '{target_dir}'...",
        "ru": "\nВосстановление файла '{filename}' в '{target_dir}'..."
    },
    "br_restore_conf_ask_source": {
        "en": "\nWhere to restore the file from?",
        "ru": "\nОткуда восстановить файл?"
    },
    "br_restore_conf_option1": {
        "en": "1. From the current backup folder ({folder})",
        "ru": "1. Из текущей папки бэкапов ({folder})"
    },
    "br_restore_conf_option2": {
        "en": "2. Select backup file manually",
        "ru": "2. Выбрать файл резервной копии вручную"
    },
    "br_restore_conf_option3": {
        "en": "3. Cancel",
        "ru": "3. Отмена"
    },
    "br_restore_conf_default_missing": {
        "en": "Backup file not found at the current path: {path}",
        "ru": "Файл резервной копии не найден по текущему пути: {path}"
    },
    "br_restore_conf_try_manual": {
        "en": "Try selecting the file manually or change the backup folder.",
        "ru": "Попробуйте выбрать файл вручную или измените папку для бэкапов."
    },
    "br_restore_conf_select_prompt": {
        "en": "Please select the backup file (e.g., user.conf.backup).",
        "ru": "Пожалуйста, выберите файл резервной копии (например, user.conf.backup)."
    },
    "br_restore_conf_select_title": {
        "en": "Select user.conf.backup",
        "ru": "Выберите файл user.conf.backup"
    },
    "br_restore_conf_filetypes": {
        "en": [("Backup files", "*.backup"), ("Config files", "*.conf"), ("All files", "*.*")],
        "ru": [("Файлы бэкапа", "*.backup"), ("Файлы конфигурации", "*.conf"), ("Все файлы", "*.*")] # Tuple format for filedialog
    },
    "br_restore_conf_cancelled": {
        "en": "Restore cancelled by user.",
        "ru": "Восстановление отменено пользователем."
    },
    "br_restore_conf_file_selected": {
        "en": "Selected file: '{path}'. Attempting restore...",
        "ru": "Выбран файл: '{path}'. Попытка восстановления..."
    },
    "br_restore_conf_success": {
        "en": "File '{filename}' successfully restored to '{target_dir}'!",
        "ru": "Файл '{filename}' успешно восстановлен в '{target_dir}'!"
    },
    "br_restore_conf_source_not_found_final": {
        "en": "Error: Source backup file '{path}' not found.",
        "ru": "Ошибка: Исходный файл бэкапа '{path}' не найден."
    },
    "br_restore_conf_perm_error": {
        "en": "Permission Error: Cannot read '{source}' or write to '{target}'.",
        "ru": "Ошибка прав доступа: Не удается прочитать '{source}' или записать в '{target}'."
    },
    "br_restore_conf_same_file": {
        "en": "Source and destination point to the same file. No restore needed.",
        "ru": "Источник и назначение указывают на один и тот же файл. Восстановление не требуется."
    },
    "br_restore_conf_os_error": {
        "en": "File system error during restore: {error} (Code: {errno})",
        "ru": "Ошибка файловой системы при восстановлении: {error} (Код: {errno})"
    },
    "br_restore_conf_auto_starting": {
        "en": "\nAttempting automatic restore of {filename} from '{path}'...",
        "ru": "\nПопытка автоматического восстановления {filename} из '{path}'..."
    },
    "br_restore_conf_auto_not_found": {
        "en": "Backup file not found in the current folder ({path}). Automatic restore skipped.",
        "ru": "Файл резервной копии не найден в текущей папке ({path}). Автоматическое восстановление пропущено."
    },
    "br_restore_conf_auto_success": {
        "en": "User configuration successfully restored from the current backup.",
        "ru": "Конфигурация пользователя успешно восстановлена из текущего бэкапа."
    },
    "br_restore_conf_auto_source_missing_final": {
        "en": "Error: Backup file '{path}' was suddenly not found.",
        "ru": "Ошибка: Файл бэкапа '{path}' внезапно не найден."
    },
    "br_restore_conf_auto_perm_error": {
        "en": "Permission error reading '{source}' or writing to '{target}'. Automatic restore failed.",
        "ru": "Ошибка прав доступа при чтении '{source}' или записи в '{target}'. Автоматическое восстановление не удалось."
    },
    "br_restore_conf_auto_os_error": {
        "en": "File system error during automatic restore: {error} (Code: {errno})",
        "ru": "Ошибка файловой системы при автоматическом восстановлении: {error} (Код: {errno})"
    },
    "br_select_dir_prompt_title": {
        "en": "{prompt}", # Generic placeholder
        "ru": "{prompt}"
    },
    "br_backup_rec_title": {
        "en": "\n" + "-"*10 + " Creating AnyDesk Screen Recordings Backup " + "-"*10,
        "ru": "\n" + "-"*10 + " Создание резервной копии записей экрана AnyDesk " + "-"*10
    },
    "br_backup_rec_default_path_info": {
        "en": "Default recordings path: {path}",
        "ru": "Стандартный путь к записям: {path}"
    },
    "br_backup_rec_ask_source_path": {
        "en": "Use default path (d) or choose manually (c)? (d/c): ",
        "ru": "Использовать стандартный путь (d) или выбрать вручную (c)? (d/c): "
    },
    "br_backup_rec_source_default_not_found": {
        "en": "Default recordings folder not found: {path}",
        "ru": "Стандартная папка записей не найдена: {path}"
    },
    "br_backup_rec_cancelled": {
        "en": "Backup cancelled.",
        "ru": "Резервное копирование отменено."
    },
    "br_backup_rec_select_source_title": {
        "en": "Select AnyDesk Screen Recordings Folder",
        "ru": "Выберите папку с записями экрана AnyDesk"
    },
    "br_backup_rec_selected_path_invalid": {
        "en": "Selected folder does not exist: {path}",
        "ru": "Выбранная папка не существует: {path}"
    },
    "br_backup_rec_source_folder_info": {
        "en": "Source folder for backup: {path}",
        "ru": "Исходная папка для бэкапа: {path}"
    },
    "br_backup_rec_source_empty": {
        "en": "Source folder is empty. Archive creation is not required.",
        "ru": "Исходная папка пуста. Создание архива не требуется."
    },
    "br_backup_rec_source_access_error": {
        "en": "Error accessing source folder '{path}': {error}",
        "ru": "Ошибка доступа к исходной папке '{path}': {error}"
    },
    "br_backup_rec_archive_path_info": {
        "en": "Archive will be saved as: {path}",
        "ru": "Архив будет сохранен как: {path}"
    },
    "br_backup_rec_archive_exists_warn": {
        "en": "WARNING: Archive '{filename}' already exists in '{folder}' and will be overwritten!",
        "ru": "ВНИМАНИЕ: Архив '{filename}' уже существует в папке '{folder}' и будет перезаписан!"
    },
    "br_backup_rec_archive_overwrite_confirm": {
        "en": "Continue overwriting?",
        "ru": "Продолжить перезапись?"
    },
    "br_backup_rec_creating_archive": {
        "en": "Creating archive...",
        "ru": "Создание архива..."
    },
    "br_backup_rec_success": {
        "en": "Screen recordings backup successfully created: {path}",
        "ru": "Резервная копия записей экрана успешно создана: {path}"
    },
    "br_backup_rec_source_missing_during_zip": {
        "en": "Error: Could not find source folder '{path}' during archiving.",
        "ru": "Ошибка: Не удалось найти исходную папку '{path}' во время архивации."
    },
    "br_backup_rec_zip_perm_error": {
        "en": "Permission error reading source files or writing archive.",
        "ru": "Ошибка прав доступа при чтении исходных файлов или записи архива."
    },
    "br_restore_rec_title": {
        "en": "\n" + "-"*10 + " Restoring AnyDesk Screen Recordings from Backup " + "-"*10,
        "ru": "\n" + "-"*10 + " Восстановление записей экрана AnyDesk из резервной копии " + "-"*10
    },
    "br_restore_rec_default_archive_info": {
        "en": "Default backup archive path: {path}",
        "ru": "Стандартный путь к архиву бэкапа: {path}"
    },
    "br_restore_rec_ask_archive_source": {
        "en": "Use default archive path (d) or choose manually (c)? (d/c): ",
        "ru": "Использовать стандартный путь к архиву (d) или выбрать вручную (c)? (d/c): "
    },
    "br_restore_rec_default_archive_missing": {
        "en": "Archive not found at default path: {path}",
        "ru": "Архив не найден по стандартному пути: {path}"
    },
    "br_restore_rec_cancelled": {
        "en": "Restore cancelled.",
        "ru": "Восстановление отменено."
    },
    "br_restore_rec_select_archive_prompt": {
        "en": "Please select the ZIP archive with the recordings backup.",
        "ru": "Пожалуйста, выберите ZIP-архив с резервной копией записей."
    },
    "br_restore_rec_select_archive_title": {
        "en": "Select Archive (.zip)",
        "ru": "Выберите архив (.zip)"
    },
    "br_restore_rec_archive_filetypes": {
        "en": [("ZIP archives", "*.zip"), ("All files", "*.*")],
        "ru": [("ZIP архивы", "*.zip"), ("Все файлы", "*.*")]
    },
    "br_restore_rec_selected_archive_invalid": {
        "en": "Selected file not found: {path}",
        "ru": "Выбранный файл не найден: {path}"
    },
    "br_restore_rec_using_archive": {
        "en": "Using archive: {path}",
        "ru": "Используется архив: {path}"
    },
    "br_restore_rec_default_dest_info": {
        "en": "Default path for restoring recordings: {path}",
        "ru": "Стандартный путь для восстановления записей: {path}"
    },
    "br_restore_rec_ask_dest_path": {
        "en": "Restore to default folder (d) or choose manually (c)? (d/c): ",
        "ru": "Восстановить в стандартную папку (d) или выбрать вручную (c)? (d/c): "
    },
    "br_restore_rec_select_dest_title": {
        "en": "Select Folder to Restore Recordings",
        "ru": "Выберите папку для восстановления записей"
    },
    "br_restore_rec_dest_folder_info": {
        "en": "Recordings will be restored to: {path}",
        "ru": "Записи будут восстановлены в: {path}"
    },
    "br_restore_rec_dest_not_empty_warn": {
        "en": "WARNING: Destination folder '{path}' is not empty!",
        "ru": "ВНИМАНИЕ: Папка назначения '{path}' не пуста!"
    },
    "br_restore_rec_dest_overwrite_warn": {
        "en": "Existing files with the same names MAY BE OVERWRITTEN during extraction.",
        "ru": "Существующие файлы с одинаковыми именами МОГУТ БЫТЬ ПЕРЕЗАПИСАНЫ при распаковке."
    },
    "br_restore_rec_dest_overwrite_confirm": {
        "en": "Continue restoring with possible overwriting?",
        "ru": "Продолжить восстановление с возможной перезаписью?"
    },
    "br_restore_rec_dest_create_error": {
        "en": "Could not create/check destination folder '{path}': {error}",
        "ru": "Не удалось создать/проверить папку назначения '{path}': {error}"
    },
    "br_restore_rec_unpacking": {
        "en": "Unpacking archive...",
        "ru": "Распаковка архива..."
    },
    "br_restore_rec_success": {
        "en": "Screen recordings successfully restored to folder: {path}",
        "ru": "Записи экрана успешно восстановлены в папку: {path}"
    },
    "br_restore_rec_archive_missing_during_unpack": {
        "en": "Error: Could not find archive '{path}' during unpacking.",
        "ru": "Ошибка: Не удалось найти архив '{path}' во время распаковки."
    },
    "br_restore_rec_unpack_perm_error": {
        "en": "Permission error reading archive or writing to destination folder.",
        "ru": "Ошибка прав доступа при чтении архива или записи в папку назначения."
    },
    "br_restore_rec_archive_read_error": {
        "en": "Error reading archive: {error}. It might be corrupted or not a ZIP file.",
        "ru": "Ошибка чтения архива: {error}. Возможно, архив поврежден или не является ZIP-файлом."
    },

    # --- id_changer.py Specific ---
    "idc_attempting_delete": {
        "en": "Attempting to delete file: {path}",
        "ru": "Попытка удаления файла: {path}"
    },
    "idc_delete_success": {
        "en": "File '{filename}' successfully deleted.",
        "ru": "Файл '{filename}' успешно удален."
    },
    "idc_id_reset_info": {
        "en": "AnyDesk ID should be reset after restarting the AnyDesk service or rebooting.",
        "ru": "AnyDesk ID должен быть сброшен после перезапуска службы AnyDesk или перезагрузки."
    },
    "idc_delete_perm_error": {
        "en": "Error: Insufficient permissions to delete '{path}'.",
        "ru": "Ошибка: Недостаточно прав для удаления файла '{path}'."
    },
    "idc_run_as_admin_hint": {
        "en": "Please run the script as an administrator.",
        "ru": "Пожалуйста, запустите скрипт от имени администратора."
    },
    "idc_delete_os_error": {
        "en": "File system error deleting '{filename}':",
        "ru": "Ошибка файловой системы при удалении файла '{filename}':"
    },
    "idc_os_error_details": {
        "en": "  Message: {error} (Code: {errno})",
        "ru": "  Сообщение: {error} (Код: {errno})"
    },
    "idc_delete_unexpected_error": {
        "en": "Unexpected error deleting '{filename}': {error}",
        "ru": "Непредвиденная ошибка при удалении файла '{filename}': {error}"
    },
    "idc_file_already_missing": {
        "en": "File '{path}' does not exist. Deletion not required.",
        "ru": "Файл '{path}' не существует. Удаление не требуется."
    },

    # --- MK_ADeskUtils.py Specific ---
    "main_title_anydesk": {
        "en": "AnyDesk",
        "ru": "AnyDesk" # Usually not translated
    },
     "main_title_utils": {
        "en": "Utils",
        "ru": "Utils"
    },
    "main_author_info": {
        "en": "  Author: MKultra69 | GitHub: https://github.com/Project-MKDELTA/MK_ADeskUtils",
        "ru": "  Автор: MKultra69 | GitHub: https://github.com/Project-MKDELTA/MK_ADeskUtils"
    },
    "main_backup_folder_info": {
        "en": "  (Backup folder: {folder})",
        "ru": "  (Папка для бэкапа: {folder})"
    },
    "main_menu_title": {
        "en": "\n  MAIN MENU:",
        "ru": "\n  ГЛАВНОЕ МЕНЮ:"
    },
    "main_menu_option1_cleanup": {
        "en": "  1. Full Cleanup",
        "ru": "  1. Полная очистка"
    },
    "main_menu_option2_utils": {
        "en": "  2. Utilities & Quick Actions",
        "ru": "  2. Утилиты и быстрые действия"
    },
    "main_menu_option3_backup": {
        "en": "  3. Backup Management",
        "ru": "  3. Управление резервными копиями"
    },
    "main_menu_option4_exit": {
        "en": "  4. Exit",
        "ru": "  4. Выход"
    },
    "main_menu_enter_choice": {
        "en": "  Enter your choice (1-4): ",
        "ru": "  Введите ваш выбор (1-4): "
    },
    "main_invalid_choice": {
        "en": "Invalid choice in the main menu.",
        "ru": "Неверный выбор в главном меню."
    },
    "main_press_enter_to_return": {
        "en": "\nPress Enter to return to the main menu...",
        "ru": "\nНажмите Enter для возврата в главное меню..."
    },
    "submenu_cleanup_title": {
        "en": "\n  FULL CLEANUP MODES:",
        "ru": "\n  РЕЖИМЫ ПОЛНОЙ ОЧИСТКИ:"
    },
    "submenu_cleanup_option_a": {
        "en": "  a. Interactive mode (with confirmation for each step)",
        "ru": "  a. Интерактивный режим (с подтверждением каждого шага)"
    },
    "submenu_cleanup_option_b": {
        "en": "  b. Automatic mode (no confirmations, DANGEROUS!)",
        "ru": "  b. Автоматический режим (без подтверждений, ОПАСНО!)"
    },
    "submenu_cleanup_option_c": {
        "en": "  c. Return to main menu",
        "ru": "  c. Вернуться в главное меню"
    },
    "submenu_cleanup_enter_choice": {
        "en": "  Select mode (a, b, c): ",
        "ru": "  Выберите режим (a, b, c): "
    },
    "submenu_cleanup_invalid_choice": {
        "en": "Invalid choice in the cleanup menu.",
        "ru": "Неверный выбор в меню очистки."
    },
    "submenu_cleanup_auto_warning_title": {
        "en": "\nWARNING: Automatic mode will perform all steps without confirmation!",
        "ru": "\nВНИМАНИЕ: Автоматический режим выполнит все шаги без подтверждения!"
    },
    "submenu_cleanup_auto_warning_details": {
        "en": "This includes deleting AnyDesk data and attempting a silent install.",
        "ru": "Это включает удаление данных AnyDesk и попытку тихой установки."
    },
    "submenu_cleanup_auto_confirm": {
        "en": "Are you sure you want to continue?",
        "ru": "Вы уверены, что хотите продолжить?"
    },
    "submenu_cleanup_auto_cancelled": {
        "en": "Automatic cleanup cancelled.",
        "ru": "Автоматическая очистка отменена."
    },
    "submenu_return_to_main": {
        "en": "Returning to main menu...",
        "ru": "Возврат в главное меню..."
    },
    "submenu_utils_title": {
        "en": "\n  UTILITIES & QUICK ACTIONS MENU:",
        "ru": "\n  МЕНЮ УТИЛИТ И БЫСТРЫХ ДЕЙСТВИЙ:"
    },
    "submenu_utils_section_service": {
        "en": "  --- Service & Processes ---",
        "ru": "  --- Служба и процессы ---"
    },
    "submenu_utils_option_a_kill": {
        "en": "  a. Stop AnyDesk (process and service)",
        "ru": "  a. Остановить AnyDesk (процесс и службу)"
    },
    "submenu_utils_option_b_start_svc": {
        "en": "  b. Start AnyDesk service",
        "ru": "  b. Запустить службу AnyDesk"
    },
    "submenu_utils_option_c_stop_svc": {
        "en": "  c. Stop AnyDesk service",
        "ru": "  c. Остановить службу AnyDesk"
    },
    "submenu_utils_option_d_status_svc": {
        "en": "  d. Check service status (Current: {status})",
        "ru": "  d. Проверить статус службы (Сейчас: {status})"
    },
    "submenu_utils_section_app": {
        "en": "\n  --- Application & ID ---",
        "ru": "\n  --- Приложение и ID ---"
    },
    "submenu_utils_option_e_run_app": {
        "en": "  e. Start AnyDesk application",
        "ru": "  e. Запустить приложение AnyDesk"
    },
    "submenu_utils_option_f_change_id": {
        "en": "  f. Change AnyDesk ID (delete service.conf)",
        "ru": "  f. Сменить ID AnyDesk (удалить service.conf)"
    },
    "submenu_utils_section_windows": {
        "en": "\n  --- Windows Settings ---",
        "ru": "\n  --- Настройки Windows ---"
    },
    "submenu_utils_option_g_enable_autostart": {
        "en": "  g. Enable AnyDesk autostart (on user login)",
        "ru": "  g. Включить автозапуск AnyDesk (при входе пользователя)"
    },
    "submenu_utils_option_h_disable_autostart": {
        "en": "  h. Disable AnyDesk autostart",
        "ru": "  h. Отключить автозапуск AnyDesk"
    },
    "submenu_utils_option_i_status_autostart": {
        "en": "  i. Check autostart status (Current: {status})",
        "ru": "  i. Проверить статус автозапуска (Сейчас: {status})"
    },
    "submenu_utils_section_install": {
        "en": "\n  --- Installation & Info ---",
        "ru": "\n  --- Установка и информация ---"
    },
    "submenu_utils_option_j_download": {
        "en": "  j. Download latest AnyDesk version",
        "ru": "  j. Скачать последнюю версию AnyDesk"
    },
    "submenu_utils_option_k_show_path": {
        "en": "  k. Show AnyDesk installation path",
        "ru": "  k. Показать путь установки AnyDesk"
    },
    "submenu_utils_option_z_exit": {
        "en": "\n  z. Return to main menu",
        "ru": "\n  z. Вернуться в главное меню"
    },
    "submenu_utils_enter_choice": {
        "en": "  Enter your choice (a-k, z): ",
        "ru": "  Введите ваш выбор (a-k, z): "
    },
    "submenu_utils_invalid_choice": {
        "en": "Invalid choice in the utilities menu.",
        "ru": "Неверный выбор в меню утилит."
    },
    "submenu_utils_checking_svc_status": {
        "en": "  Checking service status...",
        "ru": "  Проверка статуса службы..."
    },
    "submenu_utils_current_svc_status": {
        "en": "  Current AnyDesk service status: {status}",
        "ru": "  Текущий статус службы AnyDesk: {status}"
    },
    "submenu_utils_checking_autostart_status": {
        "en": "  Checking autostart status...",
        "ru": "  Проверка статуса автозапуска..."
    },
    "submenu_utils_current_autostart_status": {
        "en": "  Autostart status in HKCU\\...\\Run: {status}",
        "ru": "  Статус автозапуска в HKCU\\...\\Run: {status}"
    },
    "submenu_utils_path_not_found": {
        "en": "  Installation path not determined.",
        "ru": "  Путь установки не определен."
    },
    "submenu_backup_title": {
        "en": "\n  BACKUP MANAGEMENT MENU:",
        "ru": "\n  МЕНЮ РЕЗЕРВНЫХ КОПИЙ:"
    },
    "submenu_backup_conf_path_info": {
        "en": "  (Config backup: {path})",
        "ru": "  (Бэкап конфига: {path})"
    },
    "submenu_backup_rec_path_info": {
        "en": "  (Recordings backup: {path})",
        "ru": "  (Бэкап записей: {path})"
    },
    "submenu_backup_section_conf": {
        "en": "\n  --- Configuration (user.conf) ---",
        "ru": "\n  --- Конфигурация (user.conf) ---"
    },
    "submenu_backup_option_a_backup_conf": {
        "en": "  a. Create/update user.conf backup",
        "ru": "  a. Создать/обновить бэкап user.conf"
    },
    "submenu_backup_option_b_restore_conf": {
        "en": "  b. Restore user.conf from backup",
        "ru": "  b. Восстановить user.conf из бэкапа"
    },
    "submenu_backup_section_rec": {
        "en": "\n  --- Screen Recordings (.anydesk) ---",
        "ru": "\n  --- Записи экрана (.anydesk) ---"
    },
    "submenu_backup_option_c_backup_rec": {
        "en": "  c. Create recordings backup (to .zip)",
        "ru": "  c. Создать бэкап записей экрана (в .zip)"
    },
    "submenu_backup_option_d_restore_rec": {
        "en": "  d. Restore recordings from backup (.zip)",
        "ru": "  d. Восстановить записи экрана из бэкапа (.zip)"
    },
    "submenu_backup_section_settings": {
        "en": "\n  --- Settings ---",
        "ru": "\n  --- Настройки ---"
    },
    "submenu_backup_option_e_change_folder": {
        "en": "  e. Change folder for all backups",
        "ru": "  e. Изменить папку для всех бэкапов"
    },
    "submenu_backup_option_f_exit": {
        "en": "\n  f. Return to main menu",
        "ru": "\n  f. Вернуться в главное меню"
    },
    "submenu_backup_enter_choice": {
        "en": "  Enter your choice (a-f): ",
        "ru": "  Введите ваш выбор (a-f): "
    },
    "submenu_backup_invalid_choice": {
        "en": "Invalid choice in the backup menu.",
        "ru": "Неверный выбор в меню бэкапа."
    },
    "find_path_searching": {
        "en": "Searching for AnyDesk installation...",
        "ru": "Поиск установки AnyDesk..."
    },
    "find_path_registry_failed": {
        "en": "Registry search yielded no results. Checking standard folders...",
        "ru": "Поиск в реестре не дал результатов. Проверка стандартных папок..."
    },
     "find_path_multiple_found": {
        "en": "Multiple possible AnyDesk installation paths detected:",
        "ru": "Обнаружено несколько возможных путей установки AnyDesk:"
    },
     "find_path_select_prompt": {
        "en": "Select the number of the correct path: ",
        "ru": "Выберите номер корректного пути: "
    },
    "find_path_invalid_number": {
        "en": "Invalid number.",
        "ru": "Неверный номер."
    },
    "find_path_enter_number": {
        "en": "Please enter a number.",
        "ru": "Пожалуйста, введите число."
    },
    "find_path_success": {
        "en": "Found AnyDesk installation path: {path}",
        "ru": "Найден путь установки AnyDesk: {path}"
    },
    "find_path_failed": {
        "en": "Could not find AnyDesk installation folder.",
        "ru": "Не удалось найти папку установки AnyDesk."
    },
    "kill_attempting_process": {
        "en": "\nAttempting to terminate AnyDesk process...",
        "ru": "\nПопытка завершения процесса AnyDesk..."
    },
    "kill_process_success": {
        "en": "  AnyDesk.exe process successfully terminated.",
        "ru": "  Процесс AnyDesk.exe успешно завершен."
    },
    "kill_process_not_found": {
        "en": "  AnyDesk.exe process not found (possibly already closed).",
        "ru": "  Процесс AnyDesk.exe не найден (возможно, уже закрыт)."
    },
    "kill_process_error": {
        "en": "  Taskkill command failed with error (code {code}).",
        "ru": "  Команда taskkill завершилась с ошибкой (код {code})."
    },
    "kill_process_perm_error": {
        "en": "    Possibly insufficient permissions.",
        "ru": "    Возможно, недостаточно прав."
    },
    "kill_taskkill_not_found": {
        "en": "Error: 'taskkill' command not found.",
        "ru": "Ошибка: Команда 'taskkill' не найдена."
    },
    "kill_attempting_service": {
        "en": "Attempting to stop AnyDesk service...",
        "ru": "Попытка остановки службы AnyDesk..."
    },
    "kill_service_stop_sent": {
        "en": "  Stop command successfully sent for service '{name}'.",
        "ru": "  Команда остановки службы '{name}' успешно отправлена."
    },
    "kill_service_not_found": {
        "en": "  Service '{name}' not found.",
        "ru": "  Служба '{name}' не найдена."
    },
    "kill_service_already_stopped": {
        "en": "  Service '{name}' is already stopped.",
        "ru": "  Служба '{name}' уже остановлена."
    },
    "kill_service_perm_error": {
        "en": "  Permission Error (5): Failed to stop service '{name}'.",
        "ru": "  Ошибка прав доступа (5): Не удалось остановить службу '{name}'."
    },
    "kill_service_stop_error": {
        "en": "  Failed to stop service '{name}'. SC error code: {code}.",
        "ru": "  Не удалось остановить службу '{name}'. Код ошибки sc: {code}."
    },
    "kill_sc_not_found": {
        "en": "Error: 'sc' command not found. Cannot manage services.",
        "ru": "Ошибка: Команда 'sc' не найдена. Невозможно управлять службами."
    },
    "kill_summary_failed": {
        "en": "Failed to terminate process or stop AnyDesk service.",
        "ru": "Не удалось завершить процесс или остановить службу AnyDesk."
    },
    "kill_summary_process_failed": {
        "en": "Service stopped (or not found/running), but failed to terminate AnyDesk.exe process.",
        "ru": "Служба остановлена (или не найдена/не запущена), но процесс AnyDesk.exe завершить не удалось."
    },
    "kill_summary_service_failed": {
        "en": "Process terminated (or not found), but failed to stop the AnyDesk service.",
        "ru": "Процесс завершен (или не найден), но службу AnyDesk остановить не удалось."
    },
    "remove_starting": {
        "en": "\nRemoving AnyDesk...",
        "ru": "\nУдаление AnyDesk..."
    },
    "remove_paths_to_check": {
        "en": "The following paths will be checked and deleted (if they exist):",
        "ru": "Будут проверены и удалены следующие пути (если существуют):"
    },
    "remove_confirm": {
        "en": "Continue deleting these paths?",
        "ru": "Продолжить удаление этих путей?"
    },
    "remove_cancelled": {
        "en": "Deletion cancelled by user.",
        "ru": "Удаление отменено пользователем."
    },
    "remove_process_start": {
        "en": "\n--- Starting deletion process ---",
        "ru": "\n--- Начало процесса удаления ---"
    },
    "remove_deleting_folder": {
        "en": "Deleting folder: {path}",
        "ru": "Удаление папки: {path}"
    },
    "remove_deleting_file": {
        "en": "Deleting file: {path}",
        "ru": "Удаление файла: {path}"
    },
    "remove_delete_success": {
        "en": "  Successfully deleted: {path}",
        "ru": "  Успешно удалено: {path}"
    },
    "remove_still_exists": {
        "en": "  ! Item still exists after deletion attempt: {path}",
        "ru": "  ! Объект все еще существует после попытки удаления: {path}"
    },
    "remove_perm_error": {
        "en": "  Permission error deleting: {path}.",
        "ru": "  Ошибка прав доступа при удалении: {path}."
    },
    "remove_os_error": {
        "en": "  File system error deleting {path}: {error} (Code: {errno})",
        "ru": "  Ошибка файловой системы при удалении {path}: {error} (Код: {errno})"
    },
    "remove_unexpected_error": {
        "en": "  Unexpected error deleting {path}: {error}",
        "ru": "  Непредвиденная ошибка при удалении {path}: {error}"
    },
    "remove_summary_complete": {
        "en": "--- Deletion complete ---",
        "ru": "--- Удаление завершено ---"
    },
    "remove_summary_deleted": {
        "en": "Successfully deleted items: {count}",
        "ru": "Успешно удалено объектов: {count}"
    },
    "remove_summary_failed": {
        "en": "Failed to delete items: {count}. Check the log file ({log_file}) and permissions.",
        "ru": "Не удалось удалить объектов: {count}. Проверьте лог-файл ({log_file}) и права доступа."
    },
    "remove_summary_nothing": {
        "en": "Nothing was deleted (paths not found or already removed).",
        "ru": "Ничего не было удалено (пути не найдены или уже были удалены)."
    },
    "download_starting": {
        "en": "\nDownloading the latest version of AnyDesk...",
        "ru": "\nСкачивание последней версии AnyDesk..."
    },
    "download_source": {
        "en": "Source: {url}",
        "ru": "Источник: {url}"
    },
    "download_destination": {
        "en": "Saving to: {path}",
        "ru": "Сохранение в: {path}"
    },
    "download_progress": {
        "en": "Download progress:",
        "ru": "Процесс скачивания:"
    },
    "download_error_size_mismatch": {
        "en": "\nError: Downloaded file size ({downloaded} bytes) does not match expected size ({expected} bytes)!",
        "ru": "\nОшибка: Размер скачанного файла ({downloaded} байт) не совпадает с ожидаемым ({expected} байт)!"
    },
    "download_error_empty_file": {
        "en": "\nError: Downloaded an empty file!",
        "ru": "\nОшибка: Скачан пустой файл!"
    },
    "download_success": {
        "en": "\nAnyDesk file successfully downloaded: {path}",
        "ru": "\nФайл AnyDesk успешно скачан: {path}"
    },
    "download_error_timeout": {
        "en": "\nError: Timeout occurred while downloading AnyDesk.",
        "ru": "\nОшибка: Истекло время ожидания при скачивании AnyDesk."
    },
    "download_error_network": {
        "en": "\nNetwork error downloading AnyDesk: {error}",
        "ru": "\nОшибка сети при скачивании AnyDesk: {error}"
    },
    "download_error_write": {
        "en": "\nError writing file during AnyDesk download: {error}",
        "ru": "\nОшибка записи файла при скачивании AnyDesk: {error}"
    },
    "install_starting": {
        "en": "\nInstalling AnyDesk...",
        "ru": "\nУстановка AnyDesk..."
    },
    "install_ask_download": {
        "en": "Do you want to download the latest version of AnyDesk?",
        "ru": "Хотите скачать последнюю версию AnyDesk?"
    },
    "install_use_downloaded": {
        "en": "Use downloaded file '{filename}' for installation?",
        "ru": "Использовать скачанный файл '{filename}' для установки?"
    },
    "install_downloaded_not_used": {
        "en": "Downloaded file will not be used.",
        "ru": "Скачанный файл не будет использован."
    },
    "install_download_failed": {
        "en": "Download failed.",
        "ru": "Скачивание не удалось."
    },
    "install_ask_select_manual": {
        "en": "Do you want to select the AnyDesk installer file (.exe) manually?",
        "ru": "Хотите выбрать файл установщика AnyDesk (.exe) вручную?"
    },
    "install_select_prompt": {
        "en": "Please select the AnyDesk installer executable.",
        "ru": "Пожалуйста, выберите исполняемый файл установщика AnyDesk."
    },
    "install_select_title": {
        "en": "Select AnyDesk Installer",
        "ru": "Выберите установщик AnyDesk"
    },
    "install_filetypes": {
        "en": [("Executable files", "*.exe"), ("All files", "*.*")],
        "ru": [("Исполняемые файлы", "*.exe"), ("Все файлы", "*.*")]
    },
    "install_cancelled": {
        "en": "AnyDesk installation cancelled (installer not found/selected).",
        "ru": "Установка AnyDesk отменена (установщик не найден/не выбран)."
    },
    "install_using_installer": {
        "en": "\nUsing installer: {path}",
        "ru": "\nИспользуется установщик: {path}"
    },
    "install_attempting_silent": {
        "en": "Attempting silent installation...",
        "ru": "Попытка тихой установки..."
    },
    "install_running_command": {
        "en": "Running command: {command}",
        "ru": "Запуск команды: {command}"
    },
    "install_silent_error_code": {
        "en": "Error: Silent installation finished with code {code}.",
        "ru": "Ошибка: Тихая установка завершилась с кодом {code}."
    },
    "install_silent_error_stderr": {
        "en": "  Installer message (stderr): {stderr}",
        "ru": "  Сообщение установщика (stderr): {stderr}"
    },
    "install_silent_timeout": {
        "en": "Error: Installer did not finish within 5 minutes.",
        "ru": "Ошибка: Установщик не завершился за 5 минут."
    },
    "install_interactive_prompt": {
        "en": "Launching installer... Please follow the on-screen instructions.",
        "ru": "Запуск установщика... Пожалуйста, следуйте инструкциям на экране."
    },
    "install_finished": {
        "en": "Installer finished.",
        "ru": "Установщик завершил работу."
    },
    "install_verify_success_found": {
        "en": "Installation seems successful (found {path}).",
        "ru": "Установка, похоже, прошла успешно (найден {path})."
    },
    "install_verify_failed_silent_ok": {
        "en": "Installer finished successfully (code 0), but AnyDesk.exe not found in standard folders.",
        "ru": "Установщик завершился успешно (код 0), но AnyDesk.exe не найден в стандартных папках."
    },
    "install_verify_failed_generic": {
        "en": "AnyDesk.exe not found in standard folders after installer finished.",
        "ru": "AnyDesk.exe не найден в стандартных папках после завершения установщика."
    },
    "install_error_installer_not_found": {
        "en": "Error: Installer file not found '{path}'",
        "ru": "Ошибка: Файл установщика не найден '{path}'"
    },
    "install_error_called_process": {
        "en": "Error during installation: Installer returned error code {code}.",
        "ru": "Ошибка во время установки: Установщик вернул код ошибки {code}."
    },
    "install_error_permission": {
        "en": "Permission error launching installer.",
        "ru": "Ошибка прав доступа при запуске установщика."
    },
    "run_starting": {
        "en": "\nLaunching AnyDesk...",
        "ru": "\nЗапуск AnyDesk..."
    },
    "run_using_path": {
        "en": "Launching from: {path}",
        "ru": "Запуск из: {path}"
    },
    "run_command_sent": {
        "en": "  Launch command sent.",
        "ru": "  Команда запуска отправлена."
    },
    "run_checking_status": {
        "en": "  Checking process status in 2 seconds...",
        "ru": "  Проверка статуса процесса через 2 секунды..."
    },
    "run_process_found": {
        "en": "  AnyDesk.exe process detected.",
        "ru": "  Процесс AnyDesk.exe обнаружен."
    },
    "run_process_not_found": {
        "en": "  AnyDesk.exe process NOT detected after launch attempt.",
        "ru": "  Процесс AnyDesk.exe НЕ обнаружен после попытки запуска."
    },
    "run_error_permission": {
        "en": "Permission error launching AnyDesk.",
        "ru": "Ошибка прав доступа при запуске AnyDesk."
    },
    "run_error_os": {
        "en": "System error launching AnyDesk: {error}",
        "ru": "Ошибка системы при запуске AnyDesk: {error}"
    },
    "run_error_not_found_final": {
        "en": "Ensure AnyDesk is installed.",
        "ru": "Убедитесь, что AnyDesk установлен."
    },
    "id_change_starting": {
        "en": "\nChanging AnyDesk ID...",
        "ru": "\nСмена ID AnyDesk..."
    },
    "id_change_prompt": {
        "en": "Do you want to attempt changing the AnyDesk ID (delete {filename})?\n(Requires stopping the AnyDesk service and administrator rights)",
        "ru": "Хотите попытаться сменить ID AnyDesk (удалить {filename})?\n(Требует остановки службы AnyDesk и прав администратора)"
    },
    "id_change_stopping_service": {
        "en": "Stopping AnyDesk before changing ID...",
        "ru": "Остановка AnyDesk перед сменой ID..."
    },
    "id_change_executing": {
        "en": "Executing ID change...",
        "ru": "Выполнение смены ID..."
    },
    "id_change_success": {
        "en": "ID change operation (deleting service.conf) completed.",
        "ru": "Операция смены ID (удаление service.conf) завершена."
    },
    "id_change_failed": {
        "en": "Failed to perform ID change. See messages above and log.",
        "ru": "Не удалось выполнить смену ID. Смотрите сообщения выше и лог."
    },
    "id_change_skipping": {
        "en": "Skipping ID change.",
        "ru": "Пропуск смены ID."
    },
    "autostart_checking": {
        "en": "Checking AnyDesk autostart status...",
        "ru": "Проверка статуса автозапуска AnyDesk..."
    },
    "autostart_status_enabled": {
        "en": "Enabled",
        "ru": "Включен"
    },
    "autostart_status_disabled": {
        "en": "Disabled",
        "ru": "Отключен"
    },
    "autostart_status_unknown": {
        "en": "Unknown/Error",
        "ru": "Неизвестно/Ошибка"
    },
    "autostart_status_error": {
        "en": "Error checking AnyDesk autostart status: {error}",
        "ru": "Ошибка при проверке статуса автозапуска AnyDesk: {error}"
    },
    "autostart_setting_action": {
        "en": "\n{action} AnyDesk autostart...",
        "ru": "\n{action} автозапуска AnyDesk..."
    },
    "autostart_action_enabling": {
        "en": "Enabling",
        "ru": "Включение"
    },
    "autostart_action_disabling": {
        "en": "Disabling",
        "ru": "Отключение"
    },
    "autostart_path_not_found": {
        "en": "Cannot manage autostart (AnyDesk installation path not found).",
        "ru": "Невозможно управлять автозапуском (путь установки AnyDesk не найден)."
    },
    "autostart_exe_not_found": {
        "en": "AnyDesk.exe not found at: {path}.",
        "ru": "Файл AnyDesk.exe не найден по пути: {path}."
    },
    "autostart_cannot_manage": {
        "en": "Cannot manage autostart.",
        "ru": "Невозможно управлять автозапуском."
    },
    "autostart_enabled_success": {
        "en": "AnyDesk autostart enabled.",
        "ru": "Автозапуск AnyDesk включен."
    },
    "autostart_registry_info_added": {
        "en": "  (Entry '{name}' added/updated in HKCU\\...\\Run)",
        "ru": "  (Запись '{name}' добавлена/обновлена в HKCU\\...\\Run)"
    },
    "autostart_disabled_success": {
        "en": "AnyDesk autostart disabled.",
        "ru": "Автозапуск AnyDesk отключен."
    },
    "autostart_registry_info_removed": {
        "en": "  (Entry '{name}' removed from HKCU\\...\\Run)",
        "ru": "  (Запись '{name}' удалена из HKCU\\...\\Run)"
    },
    "autostart_already_disabled": {
        "en": "AnyDesk autostart was already disabled (entry not found).",
        "ru": "Автозапуск AnyDesk уже был отключен (запись не найдена)."
    },
    "autostart_registry_perm_error": {
        "en": "Permission error modifying autostart registry (HKCU).",
        "ru": "Ошибка прав доступа при изменении реестра автозапуска (HKCU)."
    },
    "autostart_registry_error": {
        "en": "Error accessing autostart registry: {error}",
        "ru": "Ошибка при доступе к реестру автозапуска: {error}"
    },
    "service_control_action": {
        "en": "\nPerforming '{action}' action for AnyDesk service...",
        "ru": "\nВыполнение действия '{action}' для службы AnyDesk..."
    },
    "service_invalid_action": {
        "en": "Invalid action for service.",
        "ru": "Недопустимое действие для службы."
    },
    "service_status_running": {
        "en": "Running",
        "ru": "Запущена"
    },
    "service_status_stopped": {
        "en": "Stopped",
        "ru": "Остановлена"
    },
    "service_status_not_found": {
        "en": "Not Found",
        "ru": "Не найдена"
    },
    "service_status_access_denied": {
        "en": "Access Denied",
        "ru": "Отказано в доступе"
    },
    "service_status_start_pending": {
        "en": "Starting",
        "ru": "Запускается"
    },
    "service_status_stop_pending": {
        "en": "Stopping",
        "ru": "Останавливается"
    },
    "service_status_already_running": {
        "en": "Already Running", # From control_service success
        "ru": "Уже запущена"
    },
     "service_status_already_stopped": {
        "en": "Already Stopped", # From control_service success
        "ru": "Уже остановлена"
    },
    "service_status_unknown": {
        "en": "Unknown State",
        "ru": "Неизвестное состояние"
    },
    "service_status_query_failed": {
        "en": "Query Failed",
        "ru": "Ошибка запроса"
    },
    "service_status_start_failed": {
        "en": "Start Failed",
        "ru": "Ошибка запуска"
    },
    "service_status_stop_failed": {
        "en": "Stop Failed",
        "ru": "Ошибка остановки"
    },
    "service_status_sc_not_found": {
        "en": "SC Not Found",
        "ru": "SC не найден"
    },
    "service_status_exception": {
        "en": "Exception",
        "ru": "Исключение"
    },
    "service_control_perm_error": {
        "en": "  Permission Error (5) for service '{name}'.",
        "ru": "  Ошибка прав доступа (5) для службы '{name}'."
    },
    "service_control_start_sent": {
        "en": "  Start command successfully sent for service '{name}'.",
        "ru": "  Команда запуска службы '{name}' успешно отправлена."
    },
    "service_control_checking_status": {
        "en": "  Checking service status '{name}' in 3 seconds...",
        "ru": "  Проверка статуса службы '{name}' через 3 секунды..."
    },
    "service_control_start_confirmed": {
        "en": "  Service '{name}' confirmed as running.",
        "ru": "  Служба '{name}' подтверждена как запущенная."
    },
    "service_control_start_pending_final": {
        "en": "  Service '{name}' is still in START_PENDING state.",
        "ru": "  Служба '{name}' все еще в состоянии запуска (START_PENDING)."
    },
    "service_control_start_status_after": {
        "en": "  Service '{name}' status after start attempt: {status}. May need more time or there was an issue.",
        "ru": "  Статус службы '{name}' после попытки запуска: {status}. Возможно, требуется больше времени или возникла проблема."
    },
    "service_control_start_error": {
        "en": "  Failed to start service '{name}'. SC error code: {code}.",
        "ru": "  Не удалось запустить службу '{name}'. Код ошибки sc: {code}."
    },
    "service_control_stop_sent": {
        "en": "  Stop command successfully sent for service '{name}'.",
        "ru": "  Команда остановки службы '{name}' успешно отправлена."
    },
    "service_control_stop_confirmed": {
        "en": "  Service '{name}' confirmed as stopped.",
        "ru": "  Служба '{name}' подтверждена как остановленная."
    },
    "service_control_stop_pending_final": {
        "en": "  Service '{name}' is still in STOP_PENDING state.",
        "ru": "  Служба '{name}' все еще в состоянии остановки (STOP_PENDING)."
    },
    "service_control_stop_status_after": {
        "en": "  Service '{name}' status after stop attempt: {status}.",
        "ru": "  Статус службы '{name}' после попытки остановки: {status}."
    },
    "service_control_stop_error": {
        "en": "  Failed to stop service '{name}'. SC error code: {code}.",
        "ru": "  Не удалось остановить службу '{name}'. Код ошибки sc: {code}."
    },
    "cleanup_main_start_mode": {
        "en": "\n" + "="*15 + " STARTING {mode} CLEANUP " + "="*15,
        "ru": "\n" + "="*15 + " НАЧАЛО {mode} ОЧИСТКИ " + "="*15
    },
    "cleanup_mode_automatic": {
        "en": "AUTOMATIC",
        "ru": "АВТОМАТИЧЕСКОЙ"
    },
     "cleanup_mode_interactive": {
        "en": "INTERACTIVE",
        "ru": "ИНТЕРАКТИВНОЙ"
    },
     "cleanup_intro_interactive": {
        "en": "You will be prompted for cleanup steps. You can agree (y) or skip (n).",
        "ru": "Вам будут предложены шаги очистки. Вы можете согласиться (y) или пропустить (n)."
    },
     "cleanup_step_confirm_auto": {
        "en": "{prompt} (Automatically: Yes)",
        "ru": "{prompt} (Автоматически: Да)"
    },
    "cleanup_step1_prompt": {
        "en": "1. Stop AnyDesk processes and service?",
        "ru": "1. Остановить процессы и службу AnyDesk?"
    },
    "cleanup_step1_skip": {
        "en": "Skipping AnyDesk stop.",
        "ru": "Пропуск остановки AnyDesk."
    },
    "cleanup_step2_prompt": {
        "en": "2. Create user.conf backup?",
        "ru": "2. Создать резервную копию user.conf?"
    },
    "cleanup_step2_skip": {
        "en": "Skipping user.conf backup creation.",
        "ru": "Пропуск создания резервной копии user.conf."
    },
     "cleanup_step3_prompt": {
        "en": "3. Remove AnyDesk files and folders (including data)?",
        "ru": "3. Удалить файлы и папки AnyDesk (включая данные)?"
    },
    "cleanup_step3_skip": {
        "en": "Skipping file removal.",
        "ru": "Пропуск удаления файлов."
    },
     "cleanup_step4_prompt": {
        "en": "4. Install a new version of AnyDesk?",
        "ru": "4. Установить новую версию AnyDesk?"
    },
    "cleanup_step4_auto_download_fail": {
        "en": "Automatic mode: Could not download AnyDesk, installation skipped.",
        "ru": "Автоматический режим: Не удалось скачать AnyDesk, установка пропущена."
    },
    "cleanup_step4_install_failed": {
        "en": "AnyDesk installation failed or was cancelled.",
        "ru": "Установка AnyDesk не удалась или была отменена."
    },
    "cleanup_step4_skip": {
        "en": "Skipping AnyDesk installation.",
        "ru": "Пропуск установки AnyDesk."
    },
    "cleanup_step5_prompt": {
        "en": "5. Restore user.conf from backup?",
        "ru": "5. Восстановить user.conf из резервной копии?"
    },
    "cleanup_step5_skip": {
        "en": "Skipping user.conf restore.",
        "ru": "Пропуск восстановления user.conf."
    },
    "cleanup_step6_prompt": {
        "en": "6. Attempt to change AnyDesk ID (delete service.conf)?",
        "ru": "6. Попытаться сменить ID AnyDesk (удалить service.conf)?"
    },
    "cleanup_step7_prompt": {
        "en": "7. Start AnyDesk now?",
        "ru": "7. Запустить AnyDesk сейчас?"
    },
    "cleanup_step7_skip": {
        "en": "Skipping AnyDesk launch.",
        "ru": "Пропуск запуска AnyDesk."
    },
    "cleanup_step7_skip_no_install": {
        "en": "7. AnyDesk launch skipped (installation was not performed or failed).",
        "ru": "7. Запуск AnyDesk пропущен (установка не выполнялась или не удалась)."
    },
     "cleanup_main_end_mode": {
        "en": "\n" + "="*15 + " {mode} CLEANUP COMPLETED " + "="*15,
        "ru": "\n" + "="*15 + " {mode} ОЧИСТКА ЗАВЕРШЕНА " + "="*15
    },
     "cleanup_finished": {
        "en": "Done!",
        "ru": "Готово!"
    },

    # --- FAQ ---
    "faq_title": {
        "en": "--- Frequently Asked Questions (FAQ) ---",
        "ru": "--- Часто Задаваемые Вопросы (FAQ) ---"
    },
    "faq_q_origin": {
        "en": "Q: What is this script?",
        "ru": "В: Что это за скрипт?"
    },
    "faq_a_origin": {
        "en": "A: This script is a set of utilities for AnyDesk. It originally started as a simple .bat file mainly intended to reset the AnyDesk license by deleting the configuration file (`service.conf`). Over time, I started developing it further, adding features for backup/restore of settings (`user.conf`) and recordings, service control, autostart management, and other helpful actions in an interactive menu.",
        "ru": "О: Этот скрипт - набор утилит для AnyDesk. Изначально он был простым .bat файлом, предназначенным в основном для сброса лицензии AnyDesk путем удаления файла конфигурации (`service.conf`). Со временем я начал его развивать, включив функции резервного копирования/восстановления настроек (`user.conf`) и записей, управления службой, автозапуском и другие полезные действия в интерактивном меню."
    },
    "faq_q_language": {
        "en": "Q: How do I choose the language?",
        "ru": "В: Как выбрать язык?"
    },
    "faq_a_language": {
        "en": "A: The script asks you to select 'en' for English or 'ru' for Russian right at the start.",
        "ru": "О: Скрипт запросит у вас выбор языка ('en' для английского или 'ru' для русского) сразу при запуске."
    },
    "faq_q_admin": {
        "en": "Q: Why does the script need administrator rights?",
        "ru": "В: Зачем скрипту права администратора?"
    },
    "faq_a_admin": {
        "en": "A: Administrator rights are required for actions like stopping/starting the AnyDesk service and deleting files in AnyDesk directories (like `service.conf` in `%PROGRAMDATA%`).",
        "ru": "О: Права администратора необходимы для таких действий, как остановка/запуск службы AnyDesk, удаление файлов в директориях AnyDesk (например, `service.conf` в `%PROGRAMDATA%`)."
    },
    "faq_q_cleanup_what": {
        "en": "Q: What does 'Full Cleanup' do?",
        "ru": "В: Что делает 'Полная очистка'?"
    },
    "faq_a_cleanup_what": {
        "en": "A: It's a sequence of steps designed to completely remove AnyDesk and optionally reinstall it. The steps include: stopping AnyDesk and its service, backing up settings, removing program files and folders, optionally installing a fresh copy directly from the official website, optionally restoring settings, and optionally resetting the ID.", # Updated to match RU meaning
        "ru": "О: Это последовательность шагов, предназначенная для полного удаления AnyDesk и, по желанию, его переустановки. Шаги включают: остановку AnyDesk и его службы, резервное копирование настроек, удаление программных файлов и папок, опциональную установку новой копии напрямую с официального сайта, опциональное восстановление настроек и опциональный сброс ID."
    },
    "faq_q_cleanup_modes": {
        "en": "Q: What's the difference between Interactive and Automatic cleanup?",
        "ru": "В: В чем разница между Интерактивным и Автоматическим режимами очистки?"
    },
    "faq_a_cleanup_modes": {
        "en": "A: Interactive mode asks for your confirmation (y/n) before each major step (stopping, backing up, deleting, installing, restoring, ID change). Automatic mode performs ALL steps without asking - USE WITH EXTREME CAUTION, as it will delete files and install silently if possible!",
        "ru": "О: Интерактивный режим запрашивает ваше подтверждение (y/n) перед каждым важным шагом (остановка, бэкап, удаление, установка, восстановление, смена ID). Автоматический режим выполняет ВСЕ шаги без запроса - ИСПОЛЬЗУЙТЕ С ОСОБОЙ ОСТОРОЖНОСТЬЮ, так как он удалит файлы и попытается выполнить тихую установку, если это возможно!"
    },
    "faq_q_cleanup_id_change": {
        "en": "Q: Will 'Full Cleanup' *always* change my AnyDesk ID?",
        "ru": "В: 'Полная очистка' *всегда* меняет мой ID AnyDesk?"
    },
    "faq_a_cleanup_id_change": {
        "en": "A: No. Changing the ID (by deleting `service.conf`) is an *optional* step within the cleanup process. In Interactive mode, you will be asked whether to change the ID. In Automatic mode, it will attempt the ID change.",
        "ru": "О: Нет. Смена ID (путем удаления `service.conf`) - это *опциональный* шаг в процессе очистки. В Интерактивном режиме вас спросят, сменить ли ID. В Автоматическом режиме будет предпринята попытка смены ID."
    },
    "faq_q_utils_id_change": {
        "en": "Q: How does 'Change AnyDesk ID' in the Utilities menu work?",
        "ru": "В: Как работает 'Сменить ID AnyDesk' в меню Утилит?"
    },
    "faq_a_utils_id_change": {
        "en": "A: This option specifically targets the `service.conf` file located in `%PROGRAMDATA%\\AnyDesk`. Deleting this file while the AnyDesk service is stopped usually forces AnyDesk to generate a new ID the next time the service starts. It requires administrator rights.",
        "ru": "О: Эта опция нацелена конкретно на файл `service.conf`, расположенный в `%PROGRAMDATA%\\AnyDesk`. Удаление этого файла при остановленной службе AnyDesk обычно заставляет AnyDesk сгенерировать новый ID при следующем запуске службы. Требует прав администратора."
    },
    "faq_q_utils_autostart": {
        "en": "Q: How does the autostart management work?",
        "ru": "В: Как работает управление автозапуском?"
    },
    "faq_a_utils_autostart": {
        "en": "A: It adds or removes an entry for AnyDesk in the current user's registry key `HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`. This controls whether AnyDesk starts automatically when *you* log into Windows. It does not require administrator rights as it modifies the current user's settings.",
        "ru": "О: Оно добавляет или удаляет запись для AnyDesk в ключе реестра текущего пользователя `HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`. Это контролирует, будет ли AnyDesk запускаться автоматически при *вашем* входе в Windows. Не требует прав администратора, так как изменяет настройки текущего пользователя."
    },
    "faq_q_backup_what": {
        "en": "Q: What exactly does the script back up?",
        "ru": "В: Что именно резервирует скрипт?"
    },
    "faq_a_backup_what": {
        "en": "A: It can back up two main things:\n1. Your AnyDesk settings and address book: The `user.conf` file from `%APPDATA%\\AnyDesk` is copied as `user.conf.backup`.\n2. Your screen recordings: All files from the AnyDesk recordings folder (usually `Videos\\AnyDesk\\screen recordings`) are archived into a single `.zip` file.",
        "ru": "О: Он может резервировать две основные вещи:\n1. Ваши настройки и адресную книгу AnyDesk: Файл `user.conf` из `%APPDATA%\\AnyDesk` копируется как `user.conf.backup`.\n2. Ваши записи экрана: Все файлы из папки записей AnyDesk (обычно `Videos\\AnyDesk\\screen recordings`) архивируются в один `.zip` файл."
    },
    "faq_q_backup_where": {
        "en": "Q: Where are backups saved?",
        "ru": "В: Куда сохраняются резервные копии?"
    },
    "faq_a_backup_where": {
        "en": "A: By default, backups (`user.conf.backup` and the recordings `.zip`) are saved to your Desktop (`~/Desktop`). You can change this location using option 5 in the Backup Management menu.",
        "ru": "О: По умолчанию резервные копии (`user.conf.backup` и `.zip` с записями) сохраняются на ваш Рабочий стол (`~/Desktop`). Вы можете изменить это местоположение, используя опцию 5 в меню Управления резервными копиями."
    },
    "faq_q_backup_recordings": {
        "en": "Q: Why are recordings backed up to a ZIP file?",
        "ru": "В: Почему записи резервируются в ZIP-архив?"
    },
    "faq_a_backup_recordings": {
        "en": "A: There can be many recording files. Compressing them into a single ZIP archive makes the backup easier to manage, move, and store compared to potentially hundreds of individual `.anydesk` files.",
        "ru": "О: Файлов записей может быть много. Сжатие их в один ZIP-архив упрощает управление, перемещение и хранение резервной копии по сравнению с потенциально сотнями отдельных `.anydesk` файлов."
    },
    "faq_q_logging": {
        "en": "Q: Is there a log file?",
        "ru": "В: Есть ли лог-файл?"
    },
    "faq_a_logging": {
        "en": "A: Yes, every time you run the script, it creates a detailed log file in the same directory where the script is located. The filename includes the date and time, like `anydesk_utils_YYYY-MM-DD_HH-MM-SS.log`. This file can be helpful for troubleshooting.",
        "ru": "О: Да, каждый раз при запуске скрипт создает подробный лог-файл в той же папке, где находится сам скрипт. Имя файла включает дату и время, например: `anydesk_utils_ГГГГ-ММ-ДД_ЧЧ-ММ-СС.log`. Этот файл может быть полезен для диагностики проблем."
    },
    "faq_q_risks": {
        "en": "Q: Are there any risks using this script?",
        "ru": "В: Есть ли риски при использовании этого скрипта?"
    },
    "faq_a_risks": {
        "en": "A: More likely no than yes; the script backs things up and doesn't do anything critical.",
        "ru": "О: Скорее нет, чем да, скрипт все бэкапит и ничего критичного не делает."
    },
}

# --- Global Language Variable ---
# Will be set after user selection
CURRENT_LANGUAGE = "en" # Default to English

# --- Translation Function ---
def set_language(lang_code):
    """Sets the global language."""
    global CURRENT_LANGUAGE
    if lang_code in ['en', 'ru']:
        CURRENT_LANGUAGE = lang_code
        return True
    return False

def _(key, **kwargs):
    """
    Gets the translated string for a given key and formats it.
    Uses CURRENT_LANGUAGE global variable.
    """
    lang_dict = MESSAGES.get(key, {})
    # Fallback to English if current language or key is missing, then to key itself
    message_template = lang_dict.get(CURRENT_LANGUAGE, lang_dict.get("en", key))

    # Special case for file dialog types which are lists of tuples
    if isinstance(message_template, list) and key.endswith("filetypes"):
        return message_template # Return the list directly

    # For regular strings, perform formatting if needed
    try:
        # Use str() to handle potential non-string types before format
        return str(message_template).format(**kwargs)
    except KeyError as e:
        # Handle cases where a placeholder in the string doesn't have a matching kwarg
        print(f"Translation formatting error: Missing key {e} for message key '{key}' in language '{CURRENT_LANGUAGE}'", file=sys.stderr)
        # Return the template with placeholders visible for debugging
        return str(message_template)
    except Exception as e:
        print(f"Unexpected translation formatting error for key '{key}': {e}", file=sys.stderr)
        return str(message_template) # Return raw template on other errors
