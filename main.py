class Singleton(type):
    _intances = {}
    
    def __call__(cls,*args,**kwargs):
        if cls not in cls._intances:
            cls._intances[cls] = super(Singleton,cls).__call__(*args,**kwargs)    
        return cls._intances[cls]

from ratelimit import limits,sleep_and_retry
from datetime import timedelta
Request_interval = 1 #Интервал между запросами, в секундах



class Currency(metaclass = Singleton):
    import math
    def __init__(self, currency_id = 'R01010',json_currency_url = "https://www.cbr-xml-daily.ru/daily_json.js", float_digits = 4):
        """
        Аргументы:
            currency_id (str): ID валюты согласно ЦБ. Значение по умолчанию: 'R01010'.
            
            json_currency_url (str): Ссылка на API курса валют ЦБ в формате JSON. Значение по умолчанию: "https://www.cbr-xml-daily.ru/daily_json.js".
            
            float_digits (int): Количество знаков после запятой у валюты. Значение по умолчанию: 4.
        
        """
        #Параметры
        
        import requests
        self._json_currency_url = None
        if requests.get(json_currency_url).status_code == 200:
            self._json_currency_url = json_currency_url
        else:
            raise ConnectionError('Нет соединения с API!')
        
        
        self._currency_id = currency_id
        self._float_digits = float_digits #Количество знаков после запятой у валюты
        self._result = None #Read-only. Словарь, отоброжающий код, наимнование и курс валюты. Равен None, если валюта не найдена
        
        #Внутренние переменные
        self.__Cur_Value = None # Курс валюты из API ЦБ
        self.__Cur_Value_whole = None #Целая часть курса валюты
        self.__Cur_Value_frac = None #Дробная часть курса валюты 
        self.__Cur_CharCode = None #Символьный код валюты
        self.__Cur_Nominal = None #Номинал валюты. Равен None, если 1
        self.__Cur_Name = None #Наименование валюты
    
        self.__Error_Dict = None #Словарь, который формируется, если валюта не найдена
        self.__max_float_digits = 4 #Максимальное количество
        
        
        self.__get_currency_from_API()
        
    @property
    def json_currency_url(self):
        return self._json_currency_url
    
    @json_currency_url.setter
    def json_currency_url(self,new_url):
        import requests
        if requests.get(new_url).status_code == 200:
            self._json_currency_url = new_url
        else:
            raise ConnectionError('Нет соединения с API!')
    
    
        
    @property
    def currency_id(self):
        return self.currency_id
    
    @currency_id.setter
    def currency_id(self, ID:str):
        if not isinstance(ID,str):
            raise TypeError("Неверное тип ID. Ожидаемое значение: строка!")
        self._currency_id = ID
        self.__get_currency_from_API()
        
    @property
    def result(self):
        if self._result is None:
            return self.__Error_Dict
        return self._result      
    
    @result.setter
    def result(self):
        print('Попытка происвоить значение атрибуту read-only')
    
    @property
    def float_digits(self):
        return self._float_digits
    
    @float_digits.setter
    def float_digits(self,num :int):
        print('Вызван setter')
        
        # Проверка исключений
        if not isinstance(num,int):
            raise TypeError('Неверный тип данных для количества знаков. Ожидаемое значение: целое число!')
        if num > self.__max_float_digits or num < 0:
            raise ValueError(f'Количество знаков после запятой не можеть быть больше {self.__max_float_digits} или меньше 0!')
        self._float_digits = num
        
        from math import modf
        self.__Cur_Value_frac = round(modf(self.__Cur_Value)[0]*10**self._float_digits)
    
    
    @sleep_and_retry
    @limits(calls = 1, period=timedelta(seconds= Request_interval).total_seconds())
    def visualize_currencies(self,currencies_id_list):
        ''' Визуализация курса валют по списку ID валют'''
        if len(currencies_id_list) == 0:
            print('Список ID валют пустой!')
            return
        
        # Получении информации о валютах
        import requests
        response = requests.get(self._json_currency_url)
        response.raise_for_status()
        
        valutes_lst = list(response.json()['Valute'].values())
        
                
        Currency_charcodes = []
        Currency_values = []
        for valute in valutes_lst:
            if valute['ID'] in currencies_id_list:
                Currency_charcodes.append(valute['CharCode'])
                Currency_values.append(valute['Value'])
        
        #Отрисовка
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()

        #Задаём случайный цвет для валют
        import random
        all_colors = list(plt.cm.colors.cnames.keys())
        random.seed(123)
        c = random.choices(all_colors,k = len(currencies_id_list))
        
        ax.bar(Currency_charcodes,Currency_values, color = c)
        ax.set_ylabel('Валюты')
        ax.set_title('Курс валют')
        plt.savefig('currencies')

    def __write_currency_to_class(self,valute):
        '''Запись параметров валюты по ее dict в json'''
        from math import modf
        self.__Cur_Name = valute['Name']
        self.__Cur_Value = float(valute['Value'])
        self.__Cur_CharCode = valute['CharCode']
        self.__Cur_Nominal =  valute['Nominal'] if  valute['Nominal'] != 1 else None
        
        self.__Cur_Value_frac,self.__Cur_Value_whole = modf(self.__Cur_Value)
        self.__Cur_Value_frac = round(self.__Cur_Value_frac*10**self._float_digits)
        self.__Cur_Value_whole = int(self.__Cur_Value_whole)

        self._result = {self.__Cur_CharCode: (self.__Cur_Name, str((self.__Cur_Value_whole,self.__Cur_Value_frac)))}
    
    @sleep_and_retry
    @limits(calls = 1, period=timedelta(seconds= Request_interval).total_seconds())
    def __get_currency_from_API(self):
        ''' Получает с API ЦБ валюту и записываем ёё параметры и словарь в атрибуты класса'''        
        import requests
        
        
        response = requests.get(self._json_currency_url)
        response.raise_for_status()
        
        valutes_lst = list(response.json()['Valute'].values())
        found_currency = False
        
        self._result = None
        
        # Поиск валюты в списке валют
        for valute in valutes_lst:
            if valute['ID'] == self._currency_id:
                found_currency = True
                self.__write_currency_to_class(valute)
        
        if not found_currency:
            err_dict = dict()
            err_dict[self._currency_id] = None
            self.__Error_Dict = err_dict
        
        
        
if __name__ == '__main__':
    gc = Currency()
    # print(gc._result)

    gc.currency_id = 'R01035'
    print(gc._result)

    id_list = ['R01010','R01035','R01240','R01335']
    gc.visualize_currencies(id_list)

