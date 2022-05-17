import pyodbc
from bot_create import config_value

""" Декоратор для открытия и закрытия подключения к БД """
def dec_connect(sql_func):
     def wrapper(*args, **kwargs):
        connconfig = f"DRIVER={config_value['SQL']['driver']};SERVER={config_value['SQL']['server']};DATABASE={config_value['SQL']['database']};UID={config_value['SQL']['uid']};PWD={config_value['SQL']['pwd']}"
        connection = pyodbc.connect(connconfig)
        cursor = connection.cursor()
        res = sql_func(cursor, *args, **kwargs)
        cursor.close()
        connection.close()
        return res
     return wrapper

""" Запрос в БД проверка на зарегистрированность """
@dec_connect
def sql_check_user_(cursor, user_id):
    requestString = f""" SELECT user_id FROM users WHERE  (user_id = {user_id}) """
    cursor.execute(requestString)
    result =  cursor.fetchone()
    if result == None:
        return False
    else:
        return True

""" Запрос в БД получение городов """
@dec_connect
def sql_get_city(cursor):
    requestString = f""" SELECT DISTINCT city FROM division """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        result.append(str(i).strip(strip))
    return result

""" Запрос в БД получение подразделения """
@dec_connect
def sql_get_division(cursor, user_id):
    requestString = f""" SELECT division
                    FROM     division
                    WHERE  (city = 
                            (SELECT city
                            FROM users
                            WHERE user_id = {user_id})) """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        result.append(str(i).strip(strip))
    return result

""" Запрос в БД получение подразделения """
@dec_connect
def sql_get_cashbox(cursor, division):
    requestString = f""" SELECT name FROM cashbox WHERE (division='{division}') """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        result.append(str(i).strip(strip))
    return result

""" Запрос в БД на создание пользователя """
@dec_connect
def sql_create_user(cursor, user_id, name, tel, city):
    requestString = f""" INSERT INTO users (user_id, name, tel, city, privilege) VALUES 
({user_id}, '{name}', 8{tel}, '{city}', 1) """
    cursor.execute(requestString)
    cursor.commit()

""" Запрос в БД на получение данных о пользователе """
@dec_connect
def sql_get_user(cursor, user_id):
    requestString = f""" SELECT name, tel FROM users WHERE  (user_id = {user_id}) """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        for j in i:
            result.append(str(j).strip(strip))
    return result