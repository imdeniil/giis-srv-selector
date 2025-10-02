"""
GIIS Server Selector - GUI утилита для управления stunnel конфигурацией
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import json
import subprocess
import ctypes
import shutil
from datetime import datetime
from pathlib import Path


class StunnelManager:
    """Менеджер для работы с stunnel конфигурацией и службой"""

    # Доступные серверы (из script.bat)
    SERVERS = {
        "195.209.130.9": "промышленный контур",
        "195.209.130.45": "тестовый контур (промышленный)",
        "195.209.130.19": "тестовый контур (новый функционал)"
    }

    SERVICE_NAME = "Stunnel"

    def __init__(self):
        self.config_dir = self._get_app_data_dir()
        self.config_file_path = self._load_config_path()
        self.log_file = self._create_log_file()

    def _get_app_data_dir(self):
        """Получить путь к директории приложения в AppData"""
        appdata = os.getenv('APPDATA')
        app_dir = Path(appdata) / "GIIS_ServerSelector"
        app_dir.mkdir(exist_ok=True)
        return app_dir

    def _load_config_path(self):
        """Загрузить сохраненный путь к конфигурационному файлу"""
        settings_file = self.config_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('config_path', '')
            except Exception as e:
                self.log(f"Ошибка загрузки настроек: {e}")
        return ''

    def save_config_path(self, path):
        """Сохранить путь к конфигурационному файлу"""
        settings_file = self.config_dir / "settings.json"
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump({'config_path': path}, f, ensure_ascii=False, indent=2)
            self.config_file_path = path
            self.log(f"Путь к конфигу сохранен: {path}")
        except Exception as e:
            self.log(f"Ошибка сохранения пути: {e}")
            raise

    def _create_log_file(self):
        """Создать файл лога с временной меткой"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = self.config_dir / f"stunnel_manager_{timestamp}.log"
        self.log(f"Файл лога создан: {log_file}", to_file=False)
        return log_file

    def log(self, message, to_file=True):
        """Записать сообщение в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        if to_file and hasattr(self, 'log_file'):
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_message + '\n')
            except Exception as e:
                print(f"Ошибка записи в лог: {e}")

        print(log_message)

    def get_current_server(self):
        """Получить текущий IP сервера из конфига"""
        if not self.config_file_path or not os.path.exists(self.config_file_path):
            return None

        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('connect='):
                        # Извлекаем IP (до двоеточия)
                        ip_port = line.split('=', 1)[1].strip()
                        ip = ip_port.split(':')[0].strip()
                        self.log(f"Текущий сервер: {ip}")
                        return ip
            self.log("Строка connect= не найдена в конфиге")
            return None
        except Exception as e:
            self.log(f"Ошибка чтения конфига: {e}")
            return None

    def stop_service(self):
        """Остановить службу Stunnel"""
        self.log(f"Остановка службы {self.SERVICE_NAME}...")

        # Попытка остановить службу
        result = subprocess.run(
            ['net', 'stop', self.SERVICE_NAME],
            capture_output=True,
            text=True,
            encoding='cp866'
        )

        if result.returncode != 0:
            self.log(f"Не удалось остановить службу (net stop). Пытаемся завершить процесс...")
            # Принудительное завершение процесса
            result = subprocess.run(
                ['taskkill', '/f', '/im', 'stunnel.exe'],
                capture_output=True,
                text=True,
                encoding='cp866'
            )

            if result.returncode != 0:
                self.log(f"ОШИБКА: Не удалось остановить службу!")
                return False

            self.log("Процесс завершен принудительно")
        else:
            self.log("Служба остановлена успешно")

        return True

    def start_service(self):
        """Запустить службу Stunnel"""
        self.log(f"Запуск службы {self.SERVICE_NAME}...")

        result = subprocess.run(
            ['net', 'start', self.SERVICE_NAME],
            capture_output=True,
            text=True,
            encoding='cp866'
        )

        if result.returncode != 0:
            self.log(f"ОШИБКА: Не удалось запустить службу!")
            self.log(f"Вывод: {result.stderr}")
            return False

        self.log("Служба запущена успешно")
        return True

    def change_server(self, new_ip):
        """Изменить IP сервера в конфиге"""
        if not self.config_file_path or not os.path.exists(self.config_file_path):
            raise Exception("Файл конфигурации не указан или не существует!")

        current_ip = self.get_current_server()

        if current_ip == new_ip:
            self.log(f"Сервер {new_ip} уже установлен")
            return True

        self.log("="*50)
        self.log("Изменение сервера")
        self.log(f"Старый сервер: {current_ip or 'не определен'}")
        self.log(f"Новый сервер: {new_ip} ({self.SERVERS.get(new_ip, 'неизвестный')})")
        self.log("="*50)

        # Остановка службы
        if not self.stop_service():
            raise Exception("Не удалось остановить службу!")

        # Резервное копирование
        self.log("Создание резервной копии...")
        backup_path = self.config_file_path + ".backup"
        try:
            shutil.copy2(self.config_file_path, backup_path)
            self.log(f"Резервная копия создана: {backup_path}")
        except Exception as e:
            self.log(f"ОШИБКА: Не удалось создать резервную копию: {e}")
            self.start_service()  # Попытка запустить службу обратно
            raise

        # Изменение конфига
        self.log("Изменение конфигурации...")
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            replaced = False
            new_lines = []

            for line in lines:
                if line.strip().startswith('connect='):
                    new_lines.append(f'connect={new_ip}:443\n')
                    replaced = True
                    self.log(f"Строка connect заменена на: connect={new_ip}:443")
                else:
                    new_lines.append(line)

            # Если строка connect= не найдена, добавляем
            if not replaced:
                new_lines.append(f'\nconnect={new_ip}:443\n')
                self.log(f"Строка connect добавлена: connect={new_ip}:443")

            # Записываем изменения
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            self.log("Конфигурация обновлена успешно")

        except Exception as e:
            self.log(f"ОШИБКА: Не удалось изменить конфиг: {e}")
            # Восстановление из резервной копии
            self.log("Восстановление из резервной копии...")
            shutil.copy2(backup_path, self.config_file_path)
            self.start_service()
            raise

        # Запуск службы
        if not self.start_service():
            raise Exception("Не удалось запустить службу! Проверьте конфигурацию.")

        self.log("="*50)
        self.log("УСПЕШНО: Сервер изменен!")
        self.log(f"Новый сервер: {new_ip} ({self.SERVERS.get(new_ip, 'неизвестный')})")
        self.log(f"Резервная копия: {backup_path}")
        self.log("="*50)

        return True


class StunnelGUI:
    """GUI приложение для управления Stunnel"""

    def __init__(self, root):
        self.root = root
        self.root.title("GIIS Server Selector")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        self.manager = StunnelManager()

        self._create_widgets()
        self._update_current_server()

    def _create_widgets(self):
        """Создать элементы интерфейса"""
        # Заголовок
        title_label = ttk.Label(
            self.root,
            text="GIIS Server Selector",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=10)

        # Фрейм для выбора конфига
        config_frame = ttk.LabelFrame(self.root, text="Файл конфигурации", padding=10)
        config_frame.pack(fill='x', padx=20, pady=5)

        self.config_path_var = tk.StringVar(value=self.manager.config_file_path)
        config_entry = ttk.Entry(config_frame, textvariable=self.config_path_var, state='readonly')
        config_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        browse_btn = ttk.Button(config_frame, text="Обзор...", command=self._browse_config)
        browse_btn.pack(side='left')

        # Фрейм текущего сервера
        current_frame = ttk.LabelFrame(self.root, text="Текущий сервер", padding=10)
        current_frame.pack(fill='x', padx=20, pady=5)

        self.current_server_var = tk.StringVar(value="Не определен")
        current_label = ttk.Label(
            current_frame,
            textvariable=self.current_server_var,
            font=('Arial', 11, 'bold'),
            foreground='blue'
        )
        current_label.pack()

        # Фрейм выбора сервера
        select_frame = ttk.LabelFrame(self.root, text="Выбор сервера", padding=10)
        select_frame.pack(fill='both', expand=True, padx=20, pady=5)

        ttk.Label(select_frame, text="Доступные серверы:").pack(anchor='w', pady=(0, 5))

        self.server_var = tk.StringVar()
        for ip, description in StunnelManager.SERVERS.items():
            ttk.Radiobutton(
                select_frame,
                text=f"{ip} - {description}",
                variable=self.server_var,
                value=ip
            ).pack(anchor='w', pady=2)

        # Фрейм кнопок управления
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill='x', padx=20, pady=5)

        change_btn = ttk.Button(
            control_frame,
            text="Применить изменения",
            command=self._change_server,
            style='Accent.TButton'
        )
        change_btn.pack(side='left', padx=5)

        refresh_btn = ttk.Button(
            control_frame,
            text="Обновить",
            command=self._update_current_server
        )
        refresh_btn.pack(side='left', padx=5)

        # Фрейм дополнительных кнопок
        extra_frame = ttk.Frame(self.root, padding=10)
        extra_frame.pack(fill='x', padx=20, pady=5)

        log_btn = ttk.Button(
            extra_frame,
            text="Открыть лог",
            command=self._open_log
        )
        log_btn.pack(side='left', padx=5)

        log_folder_btn = ttk.Button(
            extra_frame,
            text="Открыть папку логов",
            command=self._open_log_folder
        )
        log_folder_btn.pack(side='left', padx=5)

    def _browse_config(self):
        """Открыть диалог выбора файла конфигурации"""
        initial_dir = os.path.dirname(self.manager.config_file_path) if self.manager.config_file_path else "C:\\"

        filename = filedialog.askopenfilename(
            title="Выберите файл конфигурации stunnel",
            initialdir=initial_dir,
            filetypes=[
                ("Конфигурация", "*.conf"),
                ("Все файлы", "*.*")
            ]
        )

        if filename:
            try:
                self.manager.save_config_path(filename)
                self.config_path_var.set(filename)
                self._update_current_server()
                messagebox.showinfo("Успешно", f"Путь к конфигу сохранен:\n{filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить путь:\n{e}")

    def _update_current_server(self):
        """Обновить информацию о текущем сервере"""
        current_ip = self.manager.get_current_server()
        if current_ip:
            description = StunnelManager.SERVERS.get(current_ip, "неизвестный сервер")
            self.current_server_var.set(f"{current_ip} ({description})")
            # Установить радиокнопку
            if current_ip in StunnelManager.SERVERS:
                self.server_var.set(current_ip)
        else:
            self.current_server_var.set("Не определен")

    def _change_server(self):
        """Изменить сервер"""
        new_ip = self.server_var.get()

        if not new_ip:
            messagebox.showwarning("Предупреждение", "Выберите сервер из списка!")
            return

        if not self.manager.config_file_path or not os.path.exists(self.manager.config_file_path):
            messagebox.showerror("Ошибка", "Файл конфигурации не указан или не существует!\nВыберите файл через кнопку 'Обзор'.")
            return

        # Подтверждение
        current_ip = self.manager.get_current_server()

        if current_ip == new_ip:
            messagebox.showinfo("Информация", f"Сервер {new_ip} уже установлен!")
            return

        description = StunnelManager.SERVERS.get(new_ip, "неизвестный")
        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Изменить сервер на:\n{new_ip} ({description})?\n\nСлужба Stunnel будет перезапущена."
        )

        if not confirm:
            return

        # Выполнить изменение
        try:
            self.manager.change_server(new_ip)
            self._update_current_server()
            messagebox.showinfo(
                "Успешно",
                f"Сервер успешно изменен на:\n{new_ip} ({description})\n\nСлужба перезапущена."
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось изменить сервер:\n\n{e}\n\nПроверьте лог для деталей.")

    def _open_log(self):
        """Открыть текущий файл лога"""
        if self.manager.log_file.exists():
            os.startfile(self.manager.log_file)
        else:
            messagebox.showwarning("Предупреждение", "Файл лога не найден!")

    def _open_log_folder(self):
        """Открыть папку с логами"""
        os.startfile(self.manager.config_dir)


def is_admin():
    """Проверить, запущена ли программа с правами администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Перезапустить программу с правами администратора"""
    try:
        if sys.argv[0].endswith('.py'):
            # Запуск из Python
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                ' '.join([f'"{arg}"' for arg in sys.argv]),
                None,
                1
            )
        else:
            # Запуск из exe
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                ' '.join([f'"{arg}"' for arg in sys.argv[1:]]),
                None,
                1
            )
    except Exception as e:
        print(f"Ошибка запуска с правами администратора: {e}")
        return False
    return True


def main():
    """Главная функция"""
    # Проверка прав администратора
    if not is_admin():
        messagebox.showerror(
            "Требуются права администратора",
            "Для работы с службой Stunnel требуются права администратора.\n\n"
            "Программа будет перезапущена с повышенными правами."
        )
        if run_as_admin():
            sys.exit(0)
        else:
            messagebox.showerror("Ошибка", "Не удалось получить права администратора!")
            sys.exit(1)

    # Создание и запуск GUI
    root = tk.Tk()
    app = StunnelGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
