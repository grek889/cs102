import datetime
import requests
from bs4 import BeautifulSoup
import telebot
from config import DOMAIN


bot = telebot.TeleBot('809458576:AAGWdbBqryUxEqAFra7r64s4W3DlY005uzk')
telebot.apihelper.proxy = {'https': 'https://141.125.82.106:80'}
weekdays = [
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
    'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY',
    'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье',
    'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье',
    'ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА', 'ВОСКРЕСЕНЬЕ']
msg_wrong_group = 'Такой группы не обнаружено'
msg_no_lessons = 'Отдыхайте'
msg_wrong_message = 'Ошибка в написании команды\n/help - список команд'
cache = dict()
parity = [
    'even', 'odd',
    'e', 'o',
    'четная', 'нечетная',
    'чётная', 'нечётная',
    'чет', 'нечет',
    'чёт', 'нечёт',
    'ч', 'н']


def get_page(group, week=''):
    group = group.capitalize()
    if week is int or str(week).isdigit():
        week = int(week)
        if not (0 <= week <= 2):
            week = 0
    elif week in parity:
        week = parity.index(week) % 2 + 1
    else:
        week = 0

    if f'{group}_{week}' in cache.keys():
        web_page = cache[f'{group}_{week}']
    else:
        if week:
            w = str(week) + '/'
        else:
            w = ''
        url = '{domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
            domain=DOMAIN,
            week=w,
            group=group)
        response = requests.get(url)
        web_page = response.text
    if 'Расписание не найдено' in web_page:
        return None
    else:
        cache[f'{group}_{week}'] = web_page
        return web_page


def parse_schedule(web_page, day: str):
    soup = BeautifulSoup(web_page, "html5lib")

    # Получаем таблицу с расписанием на понедельник
    schedule_table = soup.find("table", attrs={"id": f"{day}day"})
    if schedule_table is None:
        return None

    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list


def get_parity(day: datetime.date) -> int:
    """ Возвратить четность недели для данной даты """
    first_day = datetime.date(datetime.date.today().year, 9, 1)
    if datetime.date.today() < first_day:
        first_day = datetime.date(datetime.date.today().year - 1, 9, 1)
    if first_day.weekday() == 6:
        first_day = datetime.date(datetime.date.today().year, 9, 2)
    else:
        while first_day.weekday() != 0:
            first_day = first_day - datetime.timedelta(days=1)
    passed = day - first_day
    weeks_passed = passed.days // 7
    if weeks_passed % 2 == 0:
        # нечетная неделя
        return 2
    else:
        # четная неделя
        return 1


@bot.message_handler(commands=weekdays)
def get_schedule(message):
    """ Получить расписание на указанный день """
    if 2 <= len(message.text.split()) <= 3:
        if len(message.text.split()) == 3:
            # с учетом четности
            day, week, group = message.text.split()
            group = group.capitalize()
            web_page = get_page(group, week)
        else:
            # без учета четности
            day, group = message.text.split()
            web_page = get_page(group)
        if web_page:
            schedule = parse_schedule(web_page, str(weekdays.index(day.replace('/', '')) % 7 + 1))
            if schedule:
                times_lst, locations_lst, lessons_lst = schedule
                resp = ''
                for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
                    resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
            else:
                # если в данный день нет пар
                bot.send_message(message.chat.id, msg_no_lessons, parse_mode='HTML')
        else:
            # если не найдено расписание для данной группы
            bot.send_message(message.chat.id, msg_wrong_group, parse_mode='HTML')
    else:
        # если в сообщении от пользователя некорректное число аргументов
        bot.send_message(message.chat.id, msg_wrong_message, parse_mode='HTML')

@bot.message_handler(commands=['near', 'ближайший'])
def get_near_lesson(message):
    """ Получить ближайшее занятие """
    if len(message.text.split()) == 2:
        _, group = message.text.split()
        day = datetime.datetime.today().weekday() + 1
        week = get_parity(datetime.date.today())
        web_page = get_page(group, week)
        resp = ''
        if web_page:

            schedule = parse_schedule(web_page, day)
            if schedule:
                # проверяются пары на сегодняшний день
                hour = datetime.datetime.now(datetime.timezone.utc).hour + 3
                minute = datetime.datetime.now().minute
                times_lst, locations_lst, lessons_lst = schedule
                for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
                    if hour < int(time[6:8]) or (hour == int(time[6:8]) and minute < int(time[9:11])):
                        # если текущее время меньше времени конца пары, выводится эта пара
                        resp = 'Ближайшая пара:\n\n<b>Cегодня</b>\n\n'
                        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
                        break

            if resp == '':
                # проверка оставшихся дней текущей недели
                for d in range(day + 1, 7):
                    schedule = parse_schedule(web_page, d)
                    if schedule:
                        times_lst, locations_lst, lessons_lst = schedule
                        resp = 'Ближайшая пара:\n\n<b>{}</b>\n\n'.format(weekdays[d + 27])
                        resp += '<b>{}</b>, {}, {}\n'.format(times_lst[0], locations_lst[0], lessons_lst[0])
                        break

            if resp == '':
                # проверка следующей недели
                if week == 1:
                    week = 2
                else:
                    week = 1
                for d in range(0, 7):
                    schedule = parse_schedule(web_page, d)
                    if schedule:
                        times_lst, locations_lst, lessons_lst = schedule
                        resp = 'Ближайшая пара:\n\n<b>{}</b>\n\n'.format(weekdays[d + 27])
                        resp += '<b>{}</b>, {}, {}\n'.format(times_lst[0], locations_lst[0], lessons_lst[0])
                        break

            bot.send_message(message.chat.id, resp, parse_mode='HTML')
        else:
            # если не найдено расписание для данной группы
            bot.send_message(message.chat.id, msg_wrong_group, parse_mode='HTML')
    else:
        # если в сообщении от пользователя некорректное число аргументов
        bot.send_message(message.chat.id, msg_wrong_message, parse_mode='HTML')


@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
    """ Получить расписание на следующий день """
    if len(message.text.split()) == 2:
        _, group = message.text.split()
        day = datetime.datetime.today().weekday() + 2
        week = get_parity(datetime.date.today())
        web_page = get_page(group, week)
        if web_page:
            schedule = parse_schedule(web_page, day)
            if schedule:
                times_lst, locations_lst, lessons_lst = schedule
                resp = ''
                for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
                    resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
            else:
                # если в данный день нет пар
                bot.send_message(message.chat.id, msg_no_lessons, parse_mode='HTML')
        else:
            # если не найдено расписание для данной группы
            bot.send_message(message.chat.id, msg_wrong_group, parse_mode='HTML')
    else:
        # если в сообщении от пользователя некорректное число аргументов
        bot.send_message(message.chat.id, msg_wrong_message, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    if 2 <= len(message.text.split()) <= 3:
        if len(message.text.split()) == 3:
            # с учетом четности
            _, week, group = message.text.split()
            group = group.capitalize()
            web_page = get_page(group, week)
        else:
            # без учета четности
            _, group = message.text.split()
            web_page = get_page(group)
        if web_page:
            resp = ''
            for i in range(6):
                schedule = parse_schedule(web_page, str(i + 1))
                resp += '\n<b>{}</b>\n\n'.format(weekdays[i + 28])
                if schedule:
                    times_lst, locations_lst, lessons_lst = schedule
                    for time, location, lesson in zip(times_lst, locations_lst, lessons_lst):
                        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lesson)
                else:
                    # если в данный день нет пар
                    resp += f'{msg_no_lessons}\n'
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
        else:
            # если не найдено расписание для данной группы
            bot.send_message(message.chat.id, msg_wrong_group, parse_mode='HTML')
    else:
        # если в сообщении от пользователя некорректное число аргументов
        bot.send_message(message.chat.id, msg_wrong_message, parse_mode='HTML')


if __name__ == '__main__':
    bot.polling(none_stop=True)

