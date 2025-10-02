# Changelog

Все важные изменения в проекте будут документироваться в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-02

### Added
- Инициализация проекта с использованием uv
- GUI приложение на базе tkinter
- Класс `StunnelManager` для управления конфигурацией и службой
- Класс `StunnelGUI` для графического интерфейса
- Выбор файла конфигурации stunnel через диалог
- Сохранение пути к конфигу в `%APPDATA%\GIIS_ServerSelector\settings.json`
- Отображение текущего подключенного сервера
- Выбор сервера из предустановленного списка (3 сервера)
- Автоматический перезапуск службы Stunnel при смене сервера
- Логирование всех операций в `%APPDATA%\GIIS_ServerSelector\`
- Кнопка "Открыть лог" для просмотра текущего лога
- Кнопка "Открыть папку логов" для доступа к директории логов
- Проверка прав администратора при запуске
- Автоматический перезапуск с правами администратора
- Резервное копирование конфига перед изменениями
- Восстановление из резервной копии при ошибках
- Скрипт `build.bat` для компиляции приложения
- Компиляция в exe через PyInstaller с флагом `--uac-admin`
- Документация: FILES.md, CLASSES.md, TECH.md, TRANSIT.md, CHANGELOG.md

### Changed
- Портирован функционал из `script.bat` в Python GUI приложение

### Technical Details
- Python 3.13+
- Зависимости: только стандартная библиотека (tkinter, pathlib, json, subprocess, ctypes)
- Инструменты сборки: PyInstaller 6.16.0
- Целевая платформа: Windows 10/11

[Unreleased]: https://github.com/imdeniil/giis-srv-selector/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/imdeniil/giis-srv-selector/releases/tag/v0.1.0
