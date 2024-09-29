import argparse
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def copy_file(file_path: Path, src_dir: Path, dest_dir: Path):
    """
    Копіює файл до цільової директорії, сортує його за розширенням.
    
    Args:
        file_path (Path): Шлях до файлу, який потрібно скопіювати.
        src_dir (Path): Джерельна директорія.
        dest_dir (Path): Цільова директорія.
    """
    try:
        # Отримуємо розширення файлу, без точки, у нижньому регістрі
        ext = file_path.suffix.lower().strip('.')
        if not ext:
            ext = 'no_extension'
        
        # Визначаємо цільову піддиректорію
        target_subdir = dest_dir / ext
        target_subdir.mkdir(parents=True, exist_ok=True)
        
        # Визначаємо цільовий шлях файлу
        target_file = target_subdir / file_path.name
        
        # Копіюємо файл
        shutil.copy2(file_path, target_file)
        logging.info(f"Скопійовано: {file_path} -> {target_file}")
        
    except Exception as e:
        logging.error(f"Помилка при копіюванні {file_path}: {e}")

def traverse_and_copy(src_dir: Path, dest_dir: Path, executor: ThreadPoolExecutor):
    """
    Рекурсивно обходить директорію та копіює файли за допомогою пулу потоків.
    
    Args:
        src_dir (Path): Джерельна директорія.
        dest_dir (Path): Цільова директорія.
        executor (ThreadPoolExecutor): Пул потоків для виконання копіювання файлів.
    """
    futures = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            file_path = Path(root) / file
            future = executor.submit(copy_file, file_path, src_dir, dest_dir)
            futures.append(future)
    
    # Очікуємо завершення всіх задач
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            logging.error(f"Помилка в потоці: {e}")

def main():
    # Налаштовуємо парсер аргументів
    parser = argparse.ArgumentParser(description="Сортування та копіювання файлів за розширеннями з використанням багатопотоковості.")
    parser.add_argument('src_dir', type=Path, help="Шлях до директорії з файлами для обробки.")
    parser.add_argument('dest_dir', type=Path, nargs='?', default=Path('dist'), help="Шлях до цільової директорії (за замовчуванням: dist).")
    
    args = parser.parse_args()
    src_dir = args.src_dir
    dest_dir = args.dest_dir
    
    # Перевіряємо, чи існує джерельна директорія
    if not src_dir.is_dir():
        logging.error(f"Джерельна директорія '{src_dir}' не існує або не є директорією.")
        return
    
    # Створюємо цільову директорію, якщо її немає
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Визначаємо кількість потоків (наприклад, 8)
    max_workers = min(32, os.cpu_count() + 4)
    logging.info(f"Запуск копіювання з {max_workers} потоками.")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        traverse_and_copy(src_dir, dest_dir, executor)
    
    logging.info("Копіювання завершено.")

if __name__ == "__main__":
    main()