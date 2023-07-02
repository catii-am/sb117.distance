import requests
from functools import lru_cache
import threading
import math

# Координаты дома сотрудника
home_geo = '85.23934,52.52376'

# Координаты заявок
geo_list = [
    '85.07621,52.30945',
    '85.05137,52.29979',
    '84.38182,52.36814',
    '84.41289,52.37175',
    '85.05981,52.30191',
    '85.07259,52.30141'
]

base_url = 'https://router.project-osrm.org/route/v1/driving/'

@lru_cache(maxsize=None)
def get_route_data(start_point, end_point):
    url = base_url + start_point + ';' + end_point + '?overview=false'
    response = requests.get(url)
    data = response.json()

    distance = data['routes'][0]['distance']
    duration = data['routes'][0]['duration']

    return start_point, end_point, distance, duration

def calculate_route(route):
    total_distance = 0
    total_duration = 0
    prev_point = home_geo

    for point in route:
        result = get_route_data(prev_point, point)
        total_distance += result[2]
        total_duration += result[3]
        prev_point = point

    # Вычисляем маршрут от последней точки до home_geo
    result = get_route_data(prev_point, home_geo)
    total_distance += result[2]
    total_duration += result[3]

    return total_duration, total_distance, route

def format_distance(distance):
    if distance >= 1000:
        distance_km = distance / 1000
        return f'{distance_km:.2f} км'
    else:
        return f'{distance:.2f} м'

def format_duration(duration):
    hours = math.floor(duration / 3600)
    minutes = math.floor((duration % 3600) / 60)
    return f'{hours} ч {minutes} мин'

def find_optimal_route():
    current_route = geo_list.copy()
    optimal_route = geo_list.copy()
    current_duration, current_distance, _ = calculate_route(current_route)
    optimal_duration = current_duration
    optimal_distance = current_distance

    while True:
        # Генерируем новый маршрут
        new_route = current_route.copy()
        for i in range(len(new_route)):
            for j in range(i + 1, len(new_route)):
                new_route[i], new_route[j] = new_route[j], new_route[i]
                duration, distance, _ = calculate_route(new_route)
                if duration < optimal_duration:
                    optimal_route = new_route.copy()
                    optimal_duration = duration
                    optimal_distance = distance
                new_route[i], new_route[j] = new_route[j], new_route[i]

        # Проверяем, изменился ли оптимальный маршрут
        if optimal_route != current_route:
            current_route = optimal_route.copy()
            current_duration = optimal_duration
            current_distance = optimal_distance
            formatted_distance = format_distance(current_distance)
            formatted_duration = format_duration(current_duration)
            print(f'Найден более оптимальный маршрут: {current_route}')
            print(f'Общий пробег: {formatted_distance}')
            print(f'Общая продолжительность: {formatted_duration}\n')

        # Проверяем, если пользователь ввел что-нибудь в консоль, чтобы завершить поиск
        if input() != '':
            break

if __name__ == '__main__':
    print(f'Начальная точка: {home_geo}\n')

    # Вычисляем предварительный маршрут и общее время
    total_duration, total_distance, _ = calculate_route(geo_list)
    formatted_distance = format_distance(total_distance)
    formatted_duration = format_duration(total_duration)
    print(f'Предварительный маршрут: {geo_list}')
    print(f'Общий пробег: {formatted_distance}')
    print(f'Общая продолжительность: {formatted_duration}\n\n')

    # В фоновом режиме ищем более оптимальный маршрут
    thread = threading.Thread(target=find_optimal_route)
    thread.start()

    # Ждем завершения фонового потока
    thread.join()