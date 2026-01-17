import streamlit as st
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
import requests
from streamlit_js_eval import get_geolocation
import random

# ============================================================================
# КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ
# ============================================================================

st.set_page_config(
    page_title="FoboGreen",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# СТИЛИ CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .waste-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .eco-tip {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .point-card {
        background: #f8f9fa;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        border: 2px solid #e9ecef;
        transition: all 0.3s;
    }
    .point-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(102,126,234,0.2);
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .impact-stats {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .route-step {
        background: #f8f9fa;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        border-radius: 5px;
    }
    .route-instruction {
        font-weight: bold;
        color: #667eea;
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# БАЗА ДАННЫХ ПУНКТОВ ПЕРЕРАБОТКИ
# ============================================================================

WASTE_POINTS = [
    {
        "id": 1,
        "name": "КазМетКор",
        "address": "Улица Байтерекулы, 2",
        "lat": 43.278949,
        "lon": 68.222928,
        "types": ["Металл", "Алюминий", "Жесть"],
        "working_hours": "Пн-Сб: 8:00-18:00",
        "accepts_payment": True,
        "price_per_kg": 45
    },
    {
        "id": 2,
        "name": "Склад Металл",
        "address": "Улица Талканбаева, 53",
        "lat": 43.306709,
        "lon": 68.256672,
        "types": ["Металл", "Алюминий", "Жесть"],
        "working_hours": "Пн-Сб: 8:00-18:00",
        "accepts_payment": True,
        "price_per_kg": 42
    },
    {
        "id": 3,
        "name": "Прием пластика",
        "address": "Улица Бесторангыла, 37",
        "lat": 43.317095,
        "lon": 68.326897,
        "types": ["Пластик", "ПЭТ бутылки", "Пластиковые контейнеры"],
        "working_hours": "Пн-Пт: 8:00-20:00, Сб: 9:00-18:00",
        "accepts_payment": True,
        "price_per_kg": 15
    },
    {
        "id": 4,
        "name": "Центр примем пластика",
        "address": "Улица Талас, 94",
        "lat": 43.276863,
        "lon": 68.252282,
        "types": ["Пластик", "ПЭТ бутылки", "Пластиковые контейнеры"],
        "working_hours": "Ежедневно: 9:00-18:00",
        "accepts_payment": True,
        "price_per_kg": 12
    },
    {
        "id": 5,
        "name": "Прием макулатуры",
        "address": "Улица Еркиндик, 63",
        "lat": 43.279399,
        "lon": 68.26368,
        "types": ["Бумага", "Картон", "Газеты"],
        "working_hours": "Пн-Сб: 8:00-19:00",
        "accepts_payment": True,
        "price_per_kg": 8
    },
    {
        "id": 6,
        "name": "Прием бумаг/макулатур ",
        "address": "Улица Мустафы Шокая, 62",
        "lat": 43.295846,
        "lon": 68.332209,
        "types": ["Бумага", "Картон", "Газеты"],
        "working_hours": "Пн-Сб: 9:00-18:00",
        "accepts_payment": True,
        "price_per_kg": 9
    },
    {
        "id": 7,
        "name": "Прием бутылки",
        "address": "Улица Кайнарлы, 41",
        "lat": 43.313429,
        "lon": 68.219483,
        "types": ["Стекло", "Стеклотара", "Бутылки"],
        "working_hours": "Пн-Пт: 9:00-17:00",
        "accepts_payment": True,
        "price_per_kg": 5
    },
    {
        "id": 8,
        "name": "Удобрение",
        "address": "Улица Машат, 89",
        "lat": 43.274938,
        "lon": 68.300787,
        "types": ["Органика", "Компост", "Пищевые отходы"],
        "working_hours": "Ежедневно: 7:00-20:00",
        "accepts_payment": False,
        "price_per_kg": 0
    },
    {
        "id": 9,
        "name": "Центр переработки органических веществ",
        "address": "Улица Калдаякова, 67",
        "lat": 43.274675,
        "lon": 68.31422,
        "types": ["Органика", "Компост", "Пищевые отходы"],
        "working_hours": "Ежедневно: 7:00-20:00",
        "accepts_payment": False,
        "price_per_kg": 0
    },
    {
        "id": 10,
        "name": "Электро",
        "address": "Улица Кабанбай батыра, 33",
        "lat": 43.3076,
        "lon": 68.308389,
        "types": ["Батарейки", "Аккумуляторы", "Электроника"],
        "working_hours": "Пн-Пт: 10:00-19:00",
        "accepts_payment": False,
        "price_per_kg": 0
    },
    {
        "id": 11,
        "name": "ЭкоСвет",
        "address": "Улица Гаухар ана, 98",
        "lat": 43.273568,
        "lon": 68.309051,
        "types": ["Батарейки", "Аккумуляторы", "Электроника"],
        "working_hours": "Пн-Пт: 10:00-19:00",
        "accepts_payment": False,
        "price_per_kg": 0
    },
    {
        "id": 12,
        "name": "Сдача одежды для нуждаюхщихся",
        "address": "Улица Улыкбека, 5",
        "lat": 43.304334,
        "lon": 68.201536,
        "types": ["Текстиль", "Одежда", "Обувь"],
        "working_hours": "Пн-Сб: 9:00-18:00",
        "accepts_payment": True,
        "price_per_kg": 20
    },
    {
        "id": 13,
        "name": "Прием текстиль",
        "address": "Улица Рахимова, 50",
        "lat": 43.279629,
        "lon": 68.193871,
        "types": ["Текстиль", "Одежда", "Обувь"],
        "working_hours": "Пн-Сб: 9:00-18:00",
        "accepts_payment": True,
        "price_per_kg": 20
    },
    {
        "id": 14,
        "name": "Центр стекловаты",
        "address": "5-й Ерубаева, 8",
        "lat": 43.307189,
        "lon": 68.249544,
        "types": ["Стекло", "Стеклотара", "Бутылки"],
        "working_hours": "Пн-Пт: 9:00-17:00",
        "accepts_payment": True,
        "price_per_kg": 5
    }
]

# ============================================================================
# КАТЕГОРИИ ОТХОДОВ
# ============================================================================

WASTE_CATEGORIES = {
    "Пластик": {
        "examples": ["ПЭТ бутылки", "Пластиковые пакеты", "Контейнеры", "Упаковка", "Пленка"],
        "color": "blue",
        "icon": "♻️",
        "decomposition_time": "450 лет",
        "recyclability": "95%",
        "co2_saved_per_kg": 2.5,
        "description": "Пластик - один из самых важных материалов для переработки"
    },
    "Бумага": {
        "examples": ["Газеты", "Журналы", "Картонные коробки", "Офисная бумага", "Тетради"],
        "color": "green",
        "icon": "📄",
        "decomposition_time": "2-6 месяцев",
        "recyclability": "85%",
        "co2_saved_per_kg": 1.8,
        "description": "Переработка бумаги спасает деревья и экономит воду"
    },
    "Стекло": {
        "examples": ["Бутылки", "Банки", "Стеклотара", "Оконное стекло"],
        "color": "lightgreen",
        "icon": "🍾",
        "decomposition_time": "4000 лет",
        "recyclability": "100%",
        "co2_saved_per_kg": 0.3,
        "description": "Стекло можно перерабатывать бесконечно без потери качества"
    },
    "Металл": {
        "examples": ["Алюминиевые банки", "Жестяные банки", "Металлолом", "Проволока"],
        "color": "gray",
        "icon": "🔩",
        "decomposition_time": "100-500 лет",
        "recyclability": "90%",
        "co2_saved_per_kg": 9.0,
        "description": "Переработка металла экономит огромное количество энергии"
    },
    "Органика": {
        "examples": ["Пищевые отходы", "Растительные остатки", "Садовый мусор", "Листья"],
        "color": "orange",
        "icon": "🍃",
        "decomposition_time": "2-12 месяцев",
        "recyclability": "100%",
        "co2_saved_per_kg": 0.5,
        "description": "Органика превращается в полезный компост для почвы"
    },
    "Батарейки": {
        "examples": ["Батарейки AA/AAA", "Аккумуляторы", "Электроника", "Старые телефоны"],
        "color": "red",
        "icon": "🔋",
        "decomposition_time": "100+ лет",
        "recyclability": "70%",
        "co2_saved_per_kg": 1.2,
        "description": "Батарейки содержат опасные вещества и требуют специальной переработки"
    },
    "Текстиль": {
        "examples": ["Старая одежда", "Обувь", "Ткани", "Постельное белье"],
        "color": "purple",
        "icon": "👕",
        "decomposition_time": "20-200 лет",
        "recyclability": "80%",
        "co2_saved_per_kg": 3.2,
        "description": "Текстиль можно переработать или дать вторую жизнь"
    }
}

ECO_TIPS = [
    "💡 Одна переработанная пластиковая бутылка экономит энергию для работы лампочки 3 часа!",
    "🌳 Переработка 1 тонны бумаги спасает 17 деревьев!",
    "💧 Производство алюминия из вторсырья экономит 95% энергии!",
    "🌍 Стекло можно перерабатывать бесконечное количество раз!",
    "♻️ Каждая тонна переработанного пластика экономит 700 кг нефти!",
    "🔋 Одна батарейка загрязняет 20 м² земли токсичными веществами!",
    "🌱 Компостирование органических отходов уменьшает мусор на 30%!",
    "👕 Производство одной футболки требует 2700 литров воды!"
]

# ============================================================================
# ФУНКЦИИ МАРШРУТИЗАЦИИ
# ============================================================================

def get_osrm_route(start_lat, start_lon, end_lat, end_lon):
    """Получение детального маршрута через OSRM API"""
    try:
        url = f"http://router.project-osrm.org/route/v1/foot/{start_lon},{start_lat};{end_lon},{end_lat}?steps=true&geometries=geojson&overview=full"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 'Ok' and 'routes' in data:
                return data['routes'][0]
        return None
    except Exception as e:
        st.error(f"Ошибка при получении маршрута: {e}")
        return None

def format_instruction(instruction):
    """Форматирование инструкций маршрута на русский"""
    instruction = instruction.lower()
    
    if 'turn right' in instruction or 'right' in instruction:
        return '➡️ Поверните направо'
    elif 'turn left' in instruction or 'left' in instruction:
        return '⬅️ Поверните налево'
    elif 'straight' in instruction or 'continue' in instruction:
        return '⬆️ Двигайтесь прямо'
    elif 'arrive' in instruction or 'destination' in instruction:
        return '🎯 Вы прибыли к месту назначения'
    elif 'depart' in instruction or 'head' in instruction:
        return '🚶 Начните движение'
    elif 'u-turn' in instruction:
        return '↩️ Развернитесь'
    elif 'slight right' in instruction:
        return '↗️ Поверните слегка направо'
    elif 'slight left' in instruction:
        return '↖️ Поверните слегка налево'
    elif 'sharp right' in instruction:
        return '⤴️ Резко поверните направо'
    elif 'sharp left' in instruction:
        return '⤵️ Резко поверните налево'
    else:
        return f'{instruction}'

def display_route_instructions(route_data):
    """Отображение пошаговых инструкций маршрута"""
    if not route_data or 'legs' not in route_data:
        return
    
    st.markdown("### Пошаговые инструкции маршрута")
    
    total_distance = route_data.get('distance', 0)
    total_duration = route_data.get('duration', 0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Общее расстояние", f"{total_distance:.0f} м")
    with col2:
        pass
    
    st.markdown("---")
    
    step_number = 1
    for leg in route_data['legs']:
        if 'steps' in leg:
            for step in leg['steps']:
                distance = step.get('distance', 0)
                duration = step.get('duration', 0)
                maneuver = step.get('maneuver', {})
                instruction = maneuver.get('instruction', 'Продолжайте движение')
                
                formatted_instruction = format_instruction(instruction)
                
                street_name = step.get('name', '')
                if street_name and street_name != '':
                    street_info = f" по улице {street_name}"
                else:
                    street_info = ""
                
                st.markdown(f"""
                <div class='route-step'>
                    <div class='route-instruction'>
                        Шаг {step_number}: {formatted_instruction}{street_info}
                    </div>
                    <div style='font-size: 0.9rem; color: #666;'>
                      {distance:.0f} м
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                step_number += 1

# ============================================================================
# ФУНКЦИИ РАБОТЫ С ДАННЫМИ
# ============================================================================

def calculate_distance(lat1, lon1, lat2, lon2):
    """Вычисление расстояния между двумя точками"""
    return geodesic((lat1, lon1), (lat2, lon2)).meters

def calculate_walking_time(distance_meters):
    """Расчет времени пешком"""
    return int(distance_meters / 83)

def calculate_driving_time(distance_meters):
    """Расчет времени на машине"""
    return int(distance_meters / 500)

def find_nearest_points(user_lat, user_lon, waste_type, limit=10):
    """Поиск ближайших пунктов переработки"""
    points_with_distance = []
    
    for point in WASTE_POINTS:
        if waste_type == "Все типы" or any(waste_type in t for t in point["types"]):
            distance = calculate_distance(user_lat, user_lon, point["lat"], point["lon"])
            walking_time = calculate_walking_time(distance)
            driving_time = calculate_driving_time(distance)
            
            points_with_distance.append({
                **point,
                "distance": distance,
                "walking_time": walking_time,
                "driving_time": driving_time
            })
    
    points_with_distance.sort(key=lambda x: x["distance"])
    return points_with_distance[:limit]

def calculate_eco_impact(waste_type, weight_kg):
    """Расчет экологического воздействия"""
    if waste_type in WASTE_CATEGORIES:
        co2_saved = WASTE_CATEGORIES[waste_type]["co2_saved_per_kg"] * weight_kg
        trees_saved = weight_kg * 0.017 if waste_type == "Бумага" else 0
        energy_saved = weight_kg * 12 if waste_type == "Металл" else weight_kg * 2
        
        return {
            "co2_saved": round(co2_saved, 2),
            "trees_saved": round(trees_saved, 2),
            "energy_saved": round(energy_saved, 2)
        }
    return None

def create_route_map(user_lat, user_lon, point, route_data):
    """Создание карты с детальным маршрутом"""
    m = folium.Map(
        location=[user_lat, user_lon],
        zoom_start=15,
        tiles="OpenStreetMap"
    )
    
    # Маркер пользователя
    folium.Marker(
        [user_lat, user_lon],
        popup="<b>Вы здесь</b>",
        tooltip="Ваше местоположение",
        icon=folium.Icon(color='red', icon='user', prefix='fa')
    ).add_to(m)
    
    # Маркер назначения
    folium.Marker(
        [point['lat'], point['lon']],
        popup=f"<b>{point['name']}</b><br>{point['address']}",
        tooltip=point['name'],
        icon=folium.Icon(color='green', icon='recycle', prefix='fa')
    ).add_to(m)
    
    # Отрисовка маршрута
    if route_data and 'geometry' in route_data:
        coordinates = route_data['geometry']['coordinates']
        route_coords = [[coord[1], coord[0]] for coord in coordinates]
        
        folium.PolyLine(
            locations=route_coords,
            color='blue',
            weight=5,
            opacity=0.7,
            tooltip=f"Маршрут до {point['name']}"
        ).add_to(m)
        
        # Добавление точек поворотов
        if 'legs' in route_data:
            for leg in route_data['legs']:
                if 'steps' in leg:
                    for step in leg['steps']:
                        if 'maneuver' in step:
                            maneuver_location = step['maneuver'].get('location')
                            if maneuver_location:
                                folium.CircleMarker(
                                    location=[maneuver_location[1], maneuver_location[0]],
                                    radius=4,
                                    color='orange',
                                    fill=True,
                                    fillColor='orange',
                                    fillOpacity=0.8,
                                    popup=step['maneuver'].get('instruction', '')
                                ).add_to(m)
    
    return m

def create_advanced_map(user_lat, user_lon, nearest_points, show_all=False):
    """Создание продвинутой карты с маршрутами"""
    m = folium.Map(
        location=[user_lat, user_lon],
        zoom_start=14,
        tiles="OpenStreetMap"
    )
    
    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='CartoDB Dark').add_to(m)
    
    folium.Marker(
        [user_lat, user_lon],
        popup="<div style='width: 150px; text-align: center;'><h4>Вы здесь</h4><p>Ваше текущее местоположение</p></div>",
        tooltip="Ваше местоположение",
        icon=folium.Icon(color='red', icon='user', prefix='fa')
    ).add_to(m)
    
    folium.Circle(
        [user_lat, user_lon],
        radius=1000,
        color='red',
        fill=True,
        fillColor='red',
        fillOpacity=0.1,
        popup='Радиус 1 км'
    ).add_to(m)
    
    points_to_show = WASTE_POINTS if show_all else nearest_points
    
    for i, point in enumerate(points_to_show, 1):
        primary_type = point["types"][0]
        color_map = {
            "Пластик": "blue",
            "Бумага": "green",
            "Стекло": "lightgreen",
            "Металл": "gray",
            "Органика": "orange",
            "Батарейки": "red",
            "Текстиль": "purple"
        }
        color = "blue"
        for waste_type, c in color_map.items():
            if waste_type in primary_type:
                color = c
                break
        
        distance_info = ""
        if "distance" in point:
            distance_info = f"""
            <p><b>Расстояние:</b> {point['distance']:.0f} м</p>
            <p><b>Пешком:</b> ~{point['walking_time']} мин</p>
            <p><b>На машине:</b> ~{point['driving_time']} мин</p>
            """
        
        payment_info = ""
        if point.get("accepts_payment"):
            payment_info = f"<p><b>Оплата:</b> {point.get('price_per_kg', 0)} тг/кг</p>"
        
        popup_html = f"""
        <div style='width: 280px; font-family: Arial;'>
            <h3 style='color: #667eea; margin-bottom: 10px;'>{point['name']}</h3>
            <p><b>Адрес:</b> {point['address']}</p>
            <p><b>Принимают:</b><br>{', '.join(point['types'])}</p>
            <p><b>Часы работы:</b><br>{point['working_hours']}</p>
            {payment_info}
            {distance_info}
        </div>
        """
        
        tooltip_text = f"{i}. {point['name']}"
        if "distance" in point:
            tooltip_text += f" ({point['distance']:.0f}м)"
        
        folium.Marker(
            [point['lat'], point['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip_text,
            icon=folium.Icon(color=color, icon='recycle', prefix='fa')
        ).add_to(m)
        
        if "distance" in point and not show_all:
            folium.PolyLine(
                locations=[[user_lat, user_lon], [point['lat'], point['lon']]],
                color=color,
                weight=3,
                opacity=0.6,
                popup=f"Маршрут до {point['name']}"
            ).add_to(m)
    
    folium.LayerControl().add_to(m)
    return m

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ SESSION STATE
# ============================================================================

if 'total_recycled' not in st.session_state:
    st.session_state.total_recycled = 0
if 'co2_saved' not in st.session_state:
    st.session_state.co2_saved = 0
if 'visits' not in st.session_state:
    st.session_state.visits = 0
if 'selected_point' not in st.session_state:
    st.session_state.selected_point = None
if 'show_route' not in st.session_state:
    st.session_state.show_route = False

# ============================================================================
# ЗАГОЛОВОК
# ============================================================================

st.markdown("""
<div class='main-header'>
    <h1>FoboGreen - Умная переработка отходов</h1>
    <p style='font-size: 1.2rem; margin-top: 1rem;'>
        Интеллектуальная система с детальной маршрутизацией
    </p>
    <p style='font-size: 0.9rem; opacity: 0.9;'>
        Туркестан, Казахстан | Сделано с любовью к природе
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================================================

with st.sidebar:
    st.markdown("## Панель управления")
    
    st.markdown("""
    <div style='background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;'>
        <b>⚠️ Важно!</b><br>
        Для точной работы разрешите доступ к геолокации в браузере
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("## Ваше местоположение")
    location_mode = st.radio(
        "Способ определения:",
        ["Автоматически (GPS)",  "Ввести вручную", "Выбрать район"]
    )
    
    if location_mode == "Автоматически (GPS)":
        loc = get_geolocation()
        if loc:
            user_lat = loc['coords']['latitude']
            user_lon = loc['coords']['longitude']
            st.success(f"Координаты: {user_lat:.4f}, {user_lon:.4f}")
        else:
            st.warning("Ожидание доступа к геолокации...")
            user_lat = 43.288273
            user_lon = 68.298183
    elif location_mode == "Ввести вручную":
        user_lat = st.number_input("Широта:", value=43.288273, format="%.6f", step=0.0001)
        user_lon = st.number_input("Долгота:", value=68.298183, format="%.6f", step=0.0001)
    else:
        district = st.selectbox(
            "Выберите район:",
            ["Центр города", "Район Оралман", "Старый город", "Новый город"]
        )
        district_coords = {
            "Центр города": (43.296981, 68.283009),
            "Район Оралман": (43.318509, 68.330659),
            "Старый город": (43.306413, 68.265656),
            "Новый город": (43.273324, 68.344046)
        }
        user_lat, user_lon = district_coords[district]
    
    st.markdown("---")
    
    st.markdown("### Тип отходов")
    waste_type = st.selectbox(
        "Выберите:",
        ["Все типы"] + list(WASTE_CATEGORIES.keys())
    )
    
    if waste_type != "Все типы":
        category_info = WASTE_CATEGORIES[waste_type]
        st.markdown(f"""
        <div class='waste-card'>
            <h3>{category_info['icon']} {waste_type}</h3>
            <p>{category_info['description']}</p>
            <p><b>Время разложения:</b> {category_info['decomposition_time']}</p>
            <p><b>Возможность переработки:</b> {category_info['recyclability']}</p>
            <p><b>CO₂ экономия/кг:</b> {category_info['co2_saved_per_kg']} кг</p>
            <p><b>Примеры:</b></p>
            <ul style='margin: 0.5rem 0;'>
                {''.join([f"<li>{ex}</li>" for ex in category_info['examples']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Эко-калькулятор")
    calc_waste_type = st.selectbox("Тип:", list(WASTE_CATEGORIES.keys()), key="calc")
    calc_weight = st.number_input("Вес (кг):", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)
    
    if st.button(" Рассчитать", use_container_width=True):
        impact = calculate_eco_impact(calc_waste_type, calc_weight)
        if impact:
            st.markdown(f"""
            <div class='impact-stats'>
                <h4>Ваш вклад:</h4>
                <p>🌍 CO₂: {impact['co2_saved']} кг</p>
                <p>🌳 Деревья: {impact['trees_saved']}</p>
                <p>⚡ Энергия: {impact['energy_saved']} кВт⋅ч</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Быстрые действия")
    if st.button("Показать все пункты", use_container_width=True):
        st.session_state.show_all = True
    if st.button("Только ближайшие", use_container_width=True):
        st.session_state.show_all = False

# ============================================================================
# ГЛАВНАЯ ОБЛАСТЬ
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Карта и маршруты",
    "Список пунктов",
    "Статистика",
    "Эко-советы",
    "О проекте"
])

# ============================================================================
# ВКЛАДКА 1: КАРТА И МАРШРУТЫ
# ============================================================================

with tab1:
    st.markdown("## Карта с детальной маршрутизацией")
    
    nearest_points = find_nearest_points(user_lat, user_lon, waste_type, limit=14)
    
    if nearest_points:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-container'>
                <h3 style='color: #667eea; margin: 0;'></h3>
                <h2 style='margin: 0.5rem 0;'>{len(nearest_points)}</h2>
                <p style='margin: 0; color: #666;'>Найдено пунктов</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-container'>
                <h3 style='color: #f5576c; margin: 0;'></h3>
                <h2 style='margin: 0.5rem 0;'>{int(nearest_points[0]['distance'])} м</h2>
                <p style='margin: 0; color: #666;'>До ближайшего</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-container'>
                <h3 style='color: #84fab0; margin: 0;'></h3>
                <h2 style='margin: 0.5rem 0;'>{nearest_points[0]['walking_time']} мин</h2>
                <p style='margin: 0; color: #666;'>Время пешком</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_distance = sum([p['distance'] for p in nearest_points]) / len(nearest_points)
            st.markdown(f"""
            <div class='metric-container'>
                <h3 style='color: #ffd700; margin: 0;'></h3>
                <h2 style='margin: 0.5rem 0;'>{int(avg_distance)} м</h2>
                <p style='margin: 0; color: #666;'>Средняя дистанция</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Выбор пункта для маршрута
        st.markdown("### Выберите пункт для построения детального маршрута")
        
        point_options = [f"{p['name']} - {int(p['distance'])}м ({p['walking_time']} мин)" for p in nearest_points]
        selected_index = st.selectbox("Пункт назначения:", range(len(point_options)), format_func=lambda x: point_options[x])
        
        selected_point = nearest_points[selected_index]
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Построить детальный маршрут", use_container_width=True, type="primary"):
                with st.spinner('Построение маршрута...'):
                    route_data = get_osrm_route(user_lat, user_lon, selected_point['lat'], selected_point['lon'])
                    
                    if route_data:
                        st.session_state.selected_point = selected_point
                        st.session_state.route_data = route_data
                        st.session_state.show_route = True
                        st.success("Маршрут построен!")
                        st.rerun()
                    else:
                        st.error("Не удалось построить маршрут. Попробуйте другой пункт.")
        
        with col_btn2:
            if st.button("Показать общую карту", use_container_width=True):
                st.session_state.show_route = False
                st.rerun()
        
        st.markdown("---")
        
        # Отображение карты и инструкций
        if st.session_state.show_route and 'route_data' in st.session_state:
            st.markdown(f"### Маршрут до: {st.session_state.selected_point['name']}")
            
            # Карта с маршрутом
            route_map = create_route_map(
                user_lat, user_lon,
                st.session_state.selected_point,
                st.session_state.route_data
            )
            folium_static(route_map, width=1200, height=500)
            
            st.markdown("---")
            
            # Пошаговые инструкции
            display_route_instructions(st.session_state.route_data)
            
        else:
            # Переключатель режима карты
            map_mode = st.radio(
                "Режим отображения:",
                ["Только ближайшие с маршрутами", "Все пункты на карте"],
                horizontal=True
            )
            
            show_all = map_mode == "Все пункты на карте"
            map_obj = create_advanced_map(user_lat, user_lon, nearest_points, show_all=show_all)
            folium_static(map_obj, width=1200, height=600)
    else:
        st.warning("⚠️ Пункты переработки не найдены. Попробуйте изменить параметры поиска.")

# ============================================================================
# ВКЛАДКА 2: СПИСОК ПУНКТОВ
# ============================================================================

with tab2:
    st.markdown("## Подробная информация о пунктах")
    
    if nearest_points:
        sort_by = st.selectbox("Сортировать по:", ["Расстоянию", "Цене за кг"])
        
        if sort_by == "Цене за кг":
            nearest_points.sort(key=lambda x: x.get('price_per_kg', 0), reverse=True)
        
        for i, point in enumerate(nearest_points, 1):
            with st.container():
                st.markdown(f"""
                <div class='point-card'>
                    <h3 style='color: #667eea; margin-bottom: 1rem;'>
                        {i}. {point['name']}
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"Адрес: {point['address']}")
                    st.write(f"Принимают: {', '.join(point['types'])}")
                    st.write(f"Режим: {point['working_hours']}")
                
                with col2:
                    st.metric("Расстояние", f"{point['distance']:.0f} м")
                    st.metric("Пешком", f"~{point['walking_time']} мин")
                    st.metric("На машине", f"~{point['driving_time']} мин")
                
                with col3:
                    if point.get('accepts_payment'):
                        st.metric("Цена за кг", f"{point.get('price_per_kg', 0)} ₸")
                    else:
                        st.info("Без оплаты")
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button(f"Маршрут", key=f"route_{point['id']}", use_container_width=True):
                        with st.spinner('Построение маршрута...'):
                            route_data = get_osrm_route(user_lat, user_lon, point['lat'], point['lon'])
                            if route_data:
                                st.session_state.selected_point = point
                                st.session_state.route_data = route_data
                                st.session_state.show_route = True
                                st.rerun()
                
                with col_btn2:
                    maps_url = f"https://www.google.com/maps/dir/{user_lat},{user_lon}/{point['lat']},{point['lon']}"
                    st.link_button("Google Maps", maps_url, use_container_width=True)
                
                with col_btn3:
                    gis_url = f"https://2gis.kz/turkestan?m={point['lon']},{point['lat']}/16"
                    st.link_button("2ГИС", gis_url, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("Выберите тип отходов для поиска пунктов")

# ============================================================================
# ВКЛАДКА 3: СТАТИСТИКА
# ============================================================================

with tab3:
    st.markdown("## Статистика и аналитика")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='stat-card'>
            <h2 style='margin: 0;'>14</h2>
            <p style='margin: 0.5rem 0 0 0;'>Пунктов переработки</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='stat-card' style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);'>
            <h2 style='margin: 0;'>7</h2>
            <p style='margin: 0.5rem 0 0 0;'>Типов отходов</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Статистика по типам отходов")
    
    category_stats = {}
    for point in WASTE_POINTS:
        for waste_type_item in point['types']:
            main_category = None
            for cat in WASTE_CATEGORIES.keys():
                if cat in waste_type_item:
                    main_category = cat
                    break
            
            if main_category:
                if main_category not in category_stats:
                    category_stats[main_category] = 0
                category_stats[main_category] += 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        for category, count in list(category_stats.items())[:4]:
            icon = WASTE_CATEGORIES[category]['icon']
            progress = count / max(category_stats.values())
            st.markdown(f"**{icon} {category}**")
            st.progress(progress)
            st.write(f"{count} пунктов")
            st.markdown("<br>", unsafe_allow_html=True)
    
    with col2:
        for category, count in list(category_stats.items())[4:]:
            icon = WASTE_CATEGORIES[category]['icon']
            progress = count / max(category_stats.values())
            st.markdown(f"**{icon} {category}**")
            st.progress(progress)
            st.write(f"{count} пунктов")
            st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Ваша статистика")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='metric-container'>
            <h3>♻️</h3>
            <h2>{st.session_state.total_recycled} кг</h2>
            <p>Всего переработано</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-container'>
            <h3>🌍</h3>
            <h2>{st.session_state.co2_saved} кг</h2>
            <p>CO₂ сэкономлено</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-container'>
            <h3>🎯</h3>
            <h2>{st.session_state.visits}</h2>
            <p>Посещений пунктов</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ВКЛАДКА 4: ЭКО-СОВЕТЫ
# ============================================================================

with tab4:
    st.markdown("## Экологические советы и факты")
    
    tip_of_day = random.choice(ECO_TIPS)
    st.markdown(f"""
    <div class='eco-tip'>
        <h3>💡 Совет дня</h3>
        <p style='font-size: 1.1rem; margin: 0.5rem 0;'>{tip_of_day}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Полезные советы по переработке")
    
    col1, col2 = st.columns(2)
    
    with col1:
        for tip in ECO_TIPS[:4]:
            st.markdown(f"""
            <div class='waste-card'>
                <p>{tip}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for tip in ECO_TIPS[4:]:
            st.markdown(f"""
            <div class='waste-card'>
                <p>{tip}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### Подробно о каждом типе отходов")
    
    for category, data in WASTE_CATEGORIES.items():
        with st.expander(f"{data['icon']} {category} - Нажмите для подробностей"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Описание:** {data['description']}")
                st.markdown(f"**Время разложения:** {data['decomposition_time']}")
                st.markdown(f"**Возможность переработки:** {data['recyclability']}")
            
            with col2:
                st.markdown(f"**CO₂ экономия/кг:** {data['co2_saved_per_kg']} кг")
                st.markdown("**Примеры:**")
                for example in data['examples']:
                    st.markdown(f"• {example}")

# ============================================================================
# ВКЛАДКА 5: О ПРОЕКТЕ
# ============================================================================

with tab5:
    st.markdown("## О проекте FoboGreen")
    
    st.markdown("""
    <div class='main-header'>
        <h2>Наша миссия</h2>
        <p style='font-size: 1.1rem; margin-top: 1rem;'>
            Сделать переработку отходов доступной и удобной для каждого жителя Туркестана
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Кто мы и как начали?
    
    **FoboGreen** - это команда энтузиастов из №28 школы-лицея города Туркестан, которые решили 
    внести свой вклад в решение экологических проблем нашего города.
    
    Мы заметили, что многие жители не знают, куда сдать отходы на переработку, и решили создать 
    удобное приложение, которое поможет найти ближайший пункт приема и узнать, какие материалы 
    там принимают.
    
    Наш проект - это первый шаг к более чистому и зеленому Туркестану! 
    """)
    
    st.markdown("###  Что мы предлагаем?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-container'>
            <h3></h3>
            <h4>Интерактивная карта</h4>
            <p>Все пункты переработки на одной карте</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-container'>
            <h3></h3>
            <h4>Детальная навигация</h4>
            <p>Пошаговые инструкции до пункта</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-container'>
            <h3></h3>
            <h4>Информация о ценах</h4>
            <p>Узнайте, сколько можно заработать</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### Наши партнеры")
    
    st.markdown("""
    <div class='eco-tip'>
        <h4> №28 школа-лицей</h4>
        <p>Поддержка и развитие экологических инициатив среди молодежи</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Контакты")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Техническая поддержка**
        
        +7 (775) 706-92-94
        
         +7 (707) 781-14-56
        """)
    
    with col2:
        st.markdown("""
        **Email для связи**
        
        fobogreen.kz@gmail.com
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;'>
        <h3>FoboGreen © 2026</h3>
        <p>Туркестан, Казахстан</p>
        <p>Сделано с любовью учениками №28 школы-лицея</p>
        <p style='font-size: 0.9rem; margin-top: 1rem;'>
            Вместе мы сделаем наш город чище! 
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ФУТЕР
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("""
    <div class='metric-container'>
        <p style='margin: 0; color: #667eea; font-weight: bold;'>Всего пунктов</p>
        <h3 style='margin: 0.5rem 0;'>14</h3>
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    st.markdown("""
    <div class='metric-container'>
        <p style='margin: 0; color: #667eea; font-weight: bold;'>Типов отходов</p>
        <h3 style='margin: 0.5rem 0;'>7</h3>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    st.markdown("""
    <div class='metric-container'>
        <p style='margin: 0; color: #667eea; font-weight: bold;'>Районов охвата</p>
        <h3 style='margin: 0.5rem 0;'>5</h3>
    </div>
    """, unsafe_allow_html=True)
