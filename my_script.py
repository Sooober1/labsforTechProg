#!/usr/bin/env python3
"""
Лабораторная работа №1
Скрипт определяет текущую ОС (Windows / macOS), собирает набор параметров
о системе и сохраняет результат в JSON-файл.

Запуск:
    python my_script.py

Важное ограничение задания: данные собираются БЕЗ вызова системных
утилит (нельзя дергать systeminfo, sw_vers, uname, vm_stat, ipconfig и т.п.
через subprocess). Поэтому все данные получены либо через функции
стандартной библиотеки Python (platform, os, sys, socket, getpass, uuid,
shutil, locale), либо через прямые системные вызовы операционной системы
через ctypes (GlobalMemoryStatusEx в Windows, sysctlbyname в macOS) —
это тоже стандартный модуль Python, подпроцессов не создаётся.

Внешние (не входящие в стандартную библиотеку) модули не используются:
всех нужных параметров достаточно, чтобы собрать их средствами stdlib,
поэтому обоснования для стороннего модуля (например, psutil) не требуется.
"""

import ctypes
import getpass
import json
import locale
import os
import platform
import shutil
import socket
import sys
import uuid
from datetime import datetime, timezone


def get_total_memory_bytes():
    """Физический объём ОЗУ в байтах. Получаем напрямую через системные
    вызовы ОС (без утилит типа vm_stat/systeminfo)."""
    system = platform.system()

    if system == "Windows":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        return int(stat.ullTotalPhys)

    if system == "Darwin":
        libc = ctypes.CDLL("libSystem.dylib")
        size = ctypes.c_uint64(0)
        size_len = ctypes.c_size_t(ctypes.sizeof(size))
        result = libc.sysctlbyname(
            b"hw.memsize",
            ctypes.byref(size),
            ctypes.byref(size_len),
            None,
            0,
        )
        if result == 0:
            return int(size.value)
        return None

    return None


def get_ip_address(hostname):
    try:
        return socket.gethostbyname(hostname)
    except OSError:
        return None


def get_mac_address():
    node = uuid.getnode()
    return ":".join(f"{(node >> ele) & 0xff:02x}" for ele in range(40, -1, -8))


def get_locale_name():
    try:
        return locale.getlocale()[0]
    except Exception:
        return None


def collect_system_info():
    hostname = socket.gethostname()
    home_dir = os.path.expanduser("~")
    disk_total, _disk_used, disk_free = shutil.disk_usage(home_dir)
    path_entries = os.environ.get("PATH", "").split(os.pathsep)

    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "os": {
            "system": platform.system(),          # 'Windows' / 'Darwin'
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "architecture": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "hardware": {
            "cpu_count_logical": os.cpu_count(),
            "total_memory_bytes": get_total_memory_bytes(),
            "disk_total_bytes": disk_total,
            "disk_free_bytes": disk_free,
        },
        "network": {
            "hostname": hostname,
            "ip_address": get_ip_address(hostname),
            "mac_address": get_mac_address(),
        },
        "user": {
            "username": getpass.getuser(),
            "home_directory": home_dir,
            "current_working_directory": os.getcwd(),
        },
        "environment": {
            "path_entries_count": len([p for p in path_entries if p]),
            "locale": get_locale_name(),
        },
    }


def main():
    info = collect_system_info()

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_info.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"Обнаружена ОС: {info['os']['system']}")
    print(f"Результат сохранён в: {output_path}")


if __name__ == "__main__":
    main()
