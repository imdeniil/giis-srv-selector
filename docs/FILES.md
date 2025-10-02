# Файловая структура проекта

```
giis-srv-selector/
├── .venv/                      # Виртуальное окружение Python
├── build/                      # Временные файлы сборки PyInstaller
├── dist/                       # Скомпилированные исполняемые файлы
│   └── GIIS_ServerSelector.exe # Готовая программа
├── docs/                       # Документация проекта
│   ├── CHANGELOG.md           # История изменений
│   ├── CLASSES.md             # Структура классов
│   ├── FILES.md               # Этот файл
│   ├── TECH.md                # Технический стек
│   └── TRANSIT.md             # Контекст разработки
├── giis_srv_selector.py       # Основной Python скрипт
├── script.bat                 # Оригинальный bat-скрипт
├── build.bat                  # Скрипт для сборки exe
├── CLAUDE.md                  # Инструкции для Claude
├── pyproject.toml             # Конфигурация проекта uv
├── uv.lock                    # Файл блокировки зависимостей
├── GIIS_ServerSelector.spec   # Спецификация PyInstaller
└── README.md                  # Описание проекта
```

## Системные файлы

Программа создает следующие файлы в системной директории `%APPDATA%\GIIS_ServerSelector\`:

- `settings.json` - Сохраненные настройки (путь к конфигу)
- `stunnel_manager_YYYY-MM-DD_HH-MM-SS.log` - Файлы логов операций
