"""
Программа рассылает сообщения 
в чаты, каналы, группы по списку
версия от 19 октября 2022 года

"""

#import configparser
import asyncio
import datetime
import os
import os.path
import sys
from telethon import events, TelegramClient

contacts = dict()
postingList = dict()
badIds = list()
repeating = list()
sendErrors = list()


# инициализация клиента 

#config = configparser.ConfigParser()
#config.read('mailing.ini')

#api_id = config['api_data']['api_id']
#api_hash = config['api_data']['api_hash']

try:
    api_id = os.environ['api_id']
    api_hash = os.environ['api_hash']
except KeyError:
    print('api_id не найден. Ожидается ввод значения.')
    api_id = input().strip()
    print('api_hash не найден. Ожидается ввод значения.')
    api_hash = input().strip()

try:
    client = TelegramClient('posting', api_id, api_hash)
    client.start()
    client.parse_mode = 'html'
except Exception as err:
    print('Не удается подключится с указанными данными.')
    print(err)
    print('Выполнение программы прервано.')
    sys.exit()


async def main():
    # создание файла contacts.ml
    print('1) Проверка наличия файла "contacts.ml"')
    if not os.path.exists('contacts.ml'):
        async for dialog in client.iter_dialogs():
            contacts[int(dialog.id)] = dialog.name
        contactsKey = list(contacts.keys())
        sortMethod = lambda x: 0 if x==0 else -1 if x<0 else 1
        contactsKey.sort(key=sortMethod)
        try:
           contactsFile = open("contacts.ml", "w+", encoding="utf-8")
        except:
            pass
        else:
            for userId in contactsKey:
                str = '{:<20}'.format(userId) + contacts[userId] + ' \n'
                contactsFile.write(str)
        finally:
            contactsFile.close()

        print('Контакты скачены в файл "contacts.ml".')
    else:
        print('Файл обнаружен - ОК')

    # считывание файла list.ml
    print('\n2) Считывание списка рассылки.')
    try:
        mailingFile = open("list.ml", "r", encoding="utf-8")
    except FileNotFoundError:
        mailingFile = open("list.ml", "w+", encoding="utf-8")

        print('Заполните файл "list.ml" на основании данных из '
            'файла "contacts.ml" и запустите программу заново!')
        return
    except Exception:
            print('Exception \n', error)
            return
    else:
        for i, idStr in enumerate(mailingFile):
            userData = idStr.split()
            if len(userData)>0:
                userStrId = userData[0].strip()
                infoStr = idStr.strip() + f' (строка  № {i})'
                try:
                    userId = int(userStrId)
                except ValueError:
                    badIds.append(infoStr)
                except Exception:
                    print('Exception \n', error)
                else:
                    #print(userId)
                    if userId  in postingList:
                        repeating.append(infoStr)
                    else:
                        postingList[userId] = infoStr
    finally:
        mailingFile.close()

    # если список рассылки пустой
    if not len(postingList):
        print('Список рассылки пустой. Заполните  файл "list.ml", '
            'данными взяв их из файла "contacts.ml" и запустите '
            'программу заново!')
        return

    if len(badIds):
        print('Обнаружены строки с нечитаемым id:')
        for userStr in badIds:
            print(userStr)
        print('В эти чаты (каналы, группы) сообщение не может быть '
                'отправлено. Хотите продолжить отправку? (yes/no)')
        while True:
            next = input()
            if next in ['yes']:
                break
            elif next in ['no', 'stop', 'exit', 'quit']:
                print('Исправьте некорректные id  и запустите '
                        'программу снова.')
                return
            else:
                print('Некорректный ввод. Введите "yes" если хотите перейти '
                    'к рассылке и "no" если хотите прервать программу.')

    if len(repeating):
        print('Обнаружены повторяющиеся строки:')
        for userStr in repeating:
            print(userStr)
        print('Эти строки проигнорированы. Рекомендуеся их удалить.'
                'Хотите продолжить отправку? (yes/no)')
        while True:
            next = input()
            if next in ['yes']:
                break
            elif next in ['no', 'stop', 'exit', 'quit']:
                print('Удалите повторяющиеся строки '
                        'и запустите программу снова.')
                return
            else:
                print('Некорректный ввод. Введите "yes" если хотите перейти '
                    'к рассылке и "no" если хотите прервать программу.')
    
    print('Итог:')
    print(f'Считаны id получателей - {len(postingList)}')
    print(f'Обнаружено некорректных id - {len(badIds)}')
    print(f'Обнаружено повторяющихся строк - {len(repeating)}')

    # считывание сообщения
    print('\n3) Считывание сообщения.')
    b = True
    while b:
        try:
            messageFile = open("message.ml", "r", encoding="utf-8")
        except FileNotFoundError:
            messageFile = open("message.ml", "w+", encoding="utf-8")
            print('Создан файл "message.ml". Сообщение должно '
                'находится в этом файле . Введите сообщение и запустите'
                'программу заново!')
            return
        except Exception:
                print('Exception \n', error)
        else:
            message = messageFile.read()
        finally:
            messageFile.close()

        # удаление переносов строк и лишних пробелов
        message = message.replace('\n', '')
        message = message.replace(chr(10), '')
        message = message.strip()
        while "  " in message:
            message = message.replace("  ", " ")

        if not len(message):
            print('Вы пытаетесь отправить пустое сообщение. Сообщение должно '
                'находится в файле "message.ml". Введите сообщение и запустите'
                'программу заново!')
            return

        print('Из файла "message.ml" cчитано следующее сообщение:')
        print(message)
        
        # тестовая рассылка
        print('\n4)Тестовая отправка сообщения оператору')
        me = await client.get_me()
        try:
            await client.send_message(me, message)
        except Exception as error:
            print(error)
        else:
            print('Повторить тестовую отправку сообщения ?(yes/no)')
            while b:
                next = input()
                if next in ['yes']:
                    break
                elif next in ['no', 'stop', 'exit', 'quit']:
                    b = False
                else:
                    print('Некорректный ввод. Необходимо ввести "yes" ',
                        'если хотите продолжить и "no" если хотите выйти.')

    # рассылка
    print('\nХотите разосталть сообщение? (yes/no)')
    while True:
        next = input()
        if next in ['yes']:
            break
        elif next in ['no', 'stop', 'exit', 'quit']:
            print("Отправка сообщения прервана пользователем.")
            return
        else:
            print('Некорректный ввод. Необходимо ввести "yes" ',
                'если хотите продолжить и "no" если хотите выйти.')

    goodSending = 0
    start = datetime.datetime.now()
    b = True
    for userId in postingList:
        try:
            await client.send_message(userId, message)
        except Exception as error:
            if b:
                print('\nОтправка сообщения некоторым получателям не удалась:')
                b = False
            sendErrors.append({
                'id': userId,
                'idStr': postingList[userId],
                'error': error
            })
            print('\n', postingList[userId])
            print(error)
        else:
            goodSending += 1
    end = datetime.datetime.now()
    delta = end - start

    print(f'\nРассылка завершена за '
            f'{delta.seconds}.{delta.microseconds} секунд')
    print(f'Количество получивших - {goodSending}')
    print(f'Количество ошибок - {len(sendErrors)}')
    print(f'Обнаружено повторяющихся строк - {len(repeating)}')

    #формирование файла отчета
    resultFile = open("result.ml", "w+", encoding="utf-8")
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    resultFile.write(f'Рассылка стартовала {now} \n')
    resultFile.write(f'Текст сообщения: \n')
    resultFile.write(message + '\n')
    resultFile.write(f'Рассылка завершена за '
                    '{delta.seconds}.{delta.microseconds} секунд \n')
    resultFile.write(f'Количество получивших - {goodSending} \n')
    resultFile.write(f'Количество непрочитанных id - {len(badIds)} \n')
    for badId in badIds:
        resultFile.write(f'{badId} \n')
    resultFile.write(f'Количество ошибок - {len(sendErrors)} \n')
    for error in sendErrors:
        errorUser = error['idStr']
        err = error['error']
        resultFile.write(f'{errorUser} \n')
        resultFile.write(f'{err} \n')
    resultFile.close()
    print('Сформирован отчет - "result.ml"')
    print('Для отправки нового сообщения измените его текст '
        'в файле "message.ps" и заново запустите приложение.')


print('\n***telegram mailing tool (v1.0.0 from 16.10.22) is running***')

with client:
    client.loop.run_until_complete(main())

#loop = asyncio.new_event_loop()
#asyncio.set_event_loop(loop)
#loop2 = asyncio.get_event_loop()

#loop2.create_task(main())
#try:
#    loop2.run_until_complete(asyncio.sleep(3))
#except KeyboardInterrupt as error:
    #logger.error(error)
#    loop2.run_until_complete(asyncio.sleep(3))