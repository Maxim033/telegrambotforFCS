from datetime import datetime
import logging

class VSUService:
    @staticmethod
    def get_week_type():
        try:
            now = datetime.now()
            if now.month == 9 and 1 <= now.day <= 7:
                return "числитель"
            week_number = now.isocalendar()[1]
            return "числитель" if week_number % 2 == 1 else "знаменатель"
        except Exception as error:
            logging.error(f"Ошибка в get_week_type: {error}")
            return "не определен"

    @staticmethod
    def get_buildings_info():
        return {
            'Главный корпус': {
                'address': 'Университетская площадь 1, Воронеж',
                'yandex_maps_link': 'https://yandex.ru/maps/?text=Университетская+площадь+1,+Воронеж'
            },
            'Второй корпус': {
                'address': 'Улица Ленина 10, Воронеж',
                'yandex_maps_link': 'https://yandex.ru/maps/?text=Улица+Ленина+10,+Воронеж'
            },
            'Третий корпус': {
                'address': 'Проспект Революции 24, Воронеж',
                'yandex_maps_link': 'https://yandex.ru/maps/?text=Проспект+Революции+24,+Воронеж'
            },
            'Пятый корпус': {
                'address': 'Улица Хользунова 40, Воронеж',
                'yandex_maps_link': 'https://yandex.ru/maps/?text=Улица+Хользунова+40,+Воронеж'
            },
            'Шестой корпус': {
                'address': 'Улица Хользунова 40а, Воронеж',
                'yandex_maps_link': 'https://yandex.ru/maps/?text=Улица+Хользунова+40а,+Воронеж'
            }
        }
