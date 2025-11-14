"""
Пример тестов для проверки workflow
"""

def test_addition():
    """Тест сложения"""
    assert 1 + 1 == 2
    print("✅ Addition test passed")

def test_multiplication():
    """Тест умножения"""
    assert 2 * 3 == 6
    print("✅ Multiplication test passed")

if __name__ == "__main__":
    test_addition()
    test_multiplication()
    print("🎉 All tests passed!")