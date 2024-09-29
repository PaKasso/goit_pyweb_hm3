import time
import concurrent.futures
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_factors(n):
    factors = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    return sorted(factors)

def factorize(*numbers):
    logging.info("Початок синхронного виконання")
    
    # Синхронне виконання
    start_time = time.time()
    sync_results = [get_factors(num) for num in numbers]
    sync_time = time.time() - start_time
    logging.info(f"Синхронне виконання завершено за {sync_time:.4f} секунд")
    
    logging.info("Початок паралельного виконання")
    
    # Паралельне виконання
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        parallel_results = list(executor.map(get_factors, numbers))
    parallel_time = time.time() - start_time
    logging.info(f"Паралельне виконання завершено за {parallel_time:.4f} секунд")

    return sync_results, parallel_results

# Тестування функції
if __name__ == "__main__":
    a, b = factorize(128, 255, 99999, 10651060)

    # Перевірка результатів
    assert a[0] == [1, 2, 4, 8, 16, 32, 64, 128]
    assert a[1] == [1, 3, 5, 15, 17, 51, 85, 255]
    assert a[2] == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert a[3] == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

    # Перевірка для паралельного виконання
    assert b[0] == a[0]
    assert b[1] == a[1]
    assert b[2] == a[2]
    assert b[3] == a[3]