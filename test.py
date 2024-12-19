from main import Currency

cur = Currency()

def test_valute_name(valute_id_list,valute_name_list):
    
    for k in range (len(valute_id_list)):
        cur.currency_id = valute_id_list[k]
        currency_name = list(cur.result.values())[0][0]
        assert ( currency_name== valute_name_list[k]), f'Ошибка в тесте ID-Name. {currency_name} != {valute_name_list[k]}'
    print('Тест ID-Name пройден')


valute_name_list = ['Австралийский доллар','Фунт стерлингов Соединенного королевства','Доллар США','Казахстанских тенге']
valute_id_list = ['R01010','R01035','R01235','R01335']
test_valute_name(valute_id_list,valute_name_list)



def test_unreal_id(id):
    cur.currency_id = id
    
    assert cur.result == {id:None}, f'Ошибка в тесте Unreal ID. Ожидаемое значение: {id:None}, получили {cur.result}'
    print('Тест Uneral Id пройден')

test_unreal_id('1111')