import pytest
from main import Currency  # Замените `your_module` на имя вашего модуля
from unittest.mock import patch, Mock

# Фикстура для создания экземпляра класса Currency
@pytest.fixture
def currency_instance():
    return Currency()

# Тест на синглтон
def test_singleton():
    instance1 = Currency()
    instance2 = Currency()
    assert instance1 is instance2, "Экземпляры класса Currency не являются синглтонами"

# Тест на инициализацию класса
def test_initialization(currency_instance):
    assert currency_instance._json_currency_url == "https://www.cbr-xml-daily.ru/daily_json.js", "Некорректный URL API"
    assert currency_instance._currency_id == "R01010", "Некорректный ID валюты по умолчанию"
    assert currency_instance._float_digits == 4, "Некорректное количество знаков после запятой"

# Тест на изменение currency_id
def test_currency_id_setter(currency_instance):
    currency_instance.currency_id = "R01035"
    assert currency_instance._currency_id == "R01035", "Некорректное изменение ID валюты"

# Тест на обработку неверного типа для currency_id
def test_currency_id_setter_type_error(currency_instance):
    with pytest.raises(TypeError):
        currency_instance.currency_id = 123  # Передаем число вместо строки

# Тест на изменение float_digits
def test_float_digits_setter(currency_instance):
    currency_instance.float_digits = 2
    assert currency_instance._float_digits == 2, "Некорректное изменение количества знаков после запятой"

# Тест на обработку неверного значения для float_digits
def test_float_digits_setter_value_error(currency_instance):
    with pytest.raises(ValueError):
        currency_instance.float_digits = 5  # Передаем значение больше допустимого



# Тест на визуализацию валют (мокинг)
@patch('matplotlib.pyplot.savefig')
@patch('requests.get')
def test_visualize_currencies(mock_get, mock_savefig, currency_instance):
    # Мок ответа от API
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Valute": {
            "R01010": {"ID": "R01010", "CharCode": "AUD", "Name": "Австралийский доллар", "Value": 55.1234, "Nominal": 1},
            "R01035": {"ID": "R01035", "CharCode": "GBP", "Name": "Фунт стерлингов", "Value": 100.5678, "Nominal": 1}
        }
    }
    mock_get.return_value = mock_response

    # Вызов метода визуализации
    currency_instance.visualize_currencies(["R01010", "R01035"])
    mock_savefig.assert_called_once_with('currencies')  # Проверка, что график сохранен

# Тест на обработку пустого списка валют
def test_visualize_currencies_empty_list(currency_instance):
    with patch('builtins.print') as mock_print:
        currency_instance.visualize_currencies([])
        mock_print.assert_called_once_with("Список ID валют пустой!")
