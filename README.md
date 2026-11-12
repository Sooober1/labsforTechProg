# Лабораторная работа №1 — сбор параметров ОС

Скрипт `my_script.py` определяет операционную систему, в которой он
запущен (Windows или macOS), собирает набор параметров этой ОС и
сохраняет результат в файл `system_info.json`.

## Запуск

```bash
python my_script.py
```

Поддерживаемые ОС: **Windows** и **macOS**. Скрипт автоматически определяет
текущую ОС через `platform.system()` и дальше собирает данные одинаковым
способом на обеих платформах; часть параметров (объём физической памяти)
получена по-разному для каждой ОС, так как у них разные системные API.

Python 3.8+, сторонних зависимостей не требуется.

## Как собираются данные

По условию задания **нельзя** дергать стандартные утилиты ОС (например
`systeminfo`, `sw_vers`, `uname`, `vm_stat`, `ipconfig` и т.п. через
`subprocess`). Поэтому весь сбор данных идёт только через:

- стандартные модули Python: `platform`, `os`, `sys`, `socket`, `getpass`,
  `uuid`, `shutil`, `locale`, `datetime`, `json`;
- модуль `ctypes` (тоже стандартная библиотека) — чтобы напрямую вызвать
  системную функцию ОС и получить объём физической памяти:
  `GlobalMemoryStatusEx` в Windows и `sysctlbyname("hw.memsize")`
  в macOS. Это прямой вызов системной библиотеки (`kernel32.dll` /
  `libSystem.dylib`), а не запуск консольной утилиты.

### Почему без внешних модулей

Для выбранного набора параметров стандартной библиотеки Python оказалось
достаточно (в том числе для объёма ОЗУ — через `ctypes`), поэтому сторонние
пакеты (например, `psutil`) не использовались — в них не было необходимости,
а задание требует обоснования только при использовании внешних модулей.

## Собираемые параметры

Результат сохраняется в `system_info.json` со следующей структурой:

- **`collected_at`** — дата и время сбора данных (UTC, ISO 8601)
- **`os`** — параметры операционной системы:
  - `system` — название ОС (`Windows` / `Darwin`)
  - `release` — версия релиза ядра/ОС
  - `version` — подробная строка версии
  - `platform` — полная строка платформы
  - `architecture` — архитектура процессора (`x86_64`, `arm64` и т.п.)
- **`python`** — параметры интерпретатора Python:
  - `version` — версия Python
  - `implementation` — реализация (`CPython` и т.п.)
  - `executable` — путь к исполняемому файлу интерпретатора
- **`hardware`** — параметры оборудования:
  - `cpu_count_logical` — количество логических ядер CPU
  - `total_memory_bytes` — объём физической памяти (байт)
  - `disk_total_bytes` — общий объём диска домашнего раздела (байт)
  - `disk_free_bytes` — свободное место на диске (байт)
- **`network`** — сетевые параметры:
  - `hostname` — имя хоста
  - `ip_address` — IP-адрес хоста
  - `mac_address` — MAC-адрес сетевого интерфейса
- **`user`** — параметры пользователя:
  - `username` — имя текущего пользователя
  - `home_directory` — домашняя директория
  - `current_working_directory` — рабочая директория запуска скрипта
- **`environment`** — параметры окружения:
  - `path_entries_count` — количество записей в переменной `PATH`
  - `locale` — текущая локаль системы

## Пример результата

```json
{
  "collected_at": "2026-10-01T17:29:20.666789+00:00",
  "os": {
    "system": "Darwin",
    "release": "25.5.0",
    "version": "Darwin Kernel Version 25.5.0 ...",
    "platform": "macOS-26.5.2-arm64-arm-64bit",
    "architecture": "arm64"
  },
  "python": {
    "version": "3.9.6",
    "implementation": "CPython",
    "executable": "/Library/Developer/CommandLineTools/usr/bin/python3"
  },
  "hardware": {
    "cpu_count_logical": 10,
    "total_memory_bytes": 17179869184,
    "disk_total_bytes": 494384795648,
    "disk_free_bytes": 176512335872
  },
  "network": {
    "hostname": "MacBook-Air.local",
    "ip_address": "127.0.0.1",
    "mac_address": "1e:5d:84:4d:d4:1c"
  },
  "user": {
    "username": "user",
    "home_directory": "/Users/user",
    "current_working_directory": "/Users/user/lab1"
  },
  "environment": {
    "path_entries_count": 19,
    "locale": "en_US"
  }
}
```
