\"\"\"
Пример Python файла для проверки pylint
\"\"\"

def calculate_sum(a, b):
    \"\"\"Сложение двух чисел\"\"\"
    return a + b

def calculate_product(a, b):
    \"\"\"Умножение двух чисел\"\"\"
    return a * b

def main():
    \"\"\"Основная функция\"\"\"
    result_sum = calculate_sum(5, 3)
    result_product = calculate_product(5, 3)
    print(f\"5 + 3 = {result_sum}\")
    print(f\"5 * 3 = {result_product}\")

if __name__ == \"__main__\":
    main()
