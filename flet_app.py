import flet as ft
from datetime import datetime
import locale
import json
import os

# Устанавливаем русскую локаль для отображения дат
try:
    locale.setlocale(locale.LC_TIME, 'Russian_Russia')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    except:
        pass  # Если локаль не найдена, используем системную по умолчанию

# Путь к файлу для сохранения данных
DATA_FILE = "expenses_data.json"

def main(page: ft.Page):
    # Настройка страницы
    page.title = 'Мои расходы'
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    
    # Словарь для хранения карточек по датам
    cards_by_date = {}
    
    # Переменная для хранения общей суммы
    total_sum = 0
    
    # Переменная для диалога подтверждения удаления
    confirm_delete_dialog = None

    # ===== ФУНКЦИИ СОХРАНЕНИЯ И ЗАГРУЗКИ =====
    
    def save_data():
        """Сохранение данных в JSON файл"""
        data_to_save = {}
        
        for date in cards_by_date:
            data_to_save[date] = []
            for card in cards_by_date[date]["cards"]:
                # Получаем данные из карточки
                title = card.content.content.controls[0].controls[0].value
                price_text = card.content.content.controls[0].controls[1].value
                price = price_text.split(': ')[1].split(' ')[0]
                
                # Сохраняем данные
                data_to_save[date].append({
                    "title": title,
                    "price": price
                })
        
        # Записываем в файл
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
    
    def load_data():
        """Загрузка данных из JSON файла"""
        if not os.path.exists(DATA_FILE):
            return
        
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Создаем карточки из загруженных данных
            for date in data:
                for item in data[date]:
                    create_card_from_data(item["title"], item["price"], date)
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
    
    def create_card_from_data(card_title, card_price, time_now):
        """Создание карточки из загруженных данных"""
        # Диалог подтверждения удаления
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text('Точно хотите удалить?'),
            actions=[
                ft.TextButton('Да', on_click=lambda e: remove_card(e, time_now, confirm_dialog)),
                ft.TextButton('Нет', on_click=lambda e: page.close(confirm_dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Кнопки и элементы управления карточки
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE, 
            icon_color=ft.Colors.RED_300, 
            on_click=lambda e: page.open(confirm_dialog)
        )
        check_box = ft.Checkbox(value=False)
        
        # Создание карточки
        new_card = ft.Card(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(card_title, size=18, weight=ft.FontWeight.BOLD, max_lines=3, overflow=ft.TextOverflow.VISIBLE),
                                ft.Text(f'Цена: {card_price} BYN', size=14, color=ft.Colors.GREY, overflow=ft.TextOverflow.VISIBLE),
                                ft.Text(f'Дата: {time_now}', size=14, color=ft.Colors.GREY, overflow=ft.TextOverflow.VISIBLE)
                            ],
                            expand=True
                        ),
                        delete_btn,
                        check_box
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=15,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10
            ),
            elevation=4,
            width=page.width
        )
        
        # Функция для удаления карточки
        def remove_card(e, date, dialog):
            cards_by_date[date]["cards"].remove(new_card)
            expanses_list.controls.remove(new_card)

            if len(cards_by_date[date]["cards"]) == 0:
                expanses_list.controls.remove(cards_by_date[date]["header"])
                del cards_by_date[date]

            if dialog:
                page.close(dialog)
            page.update()
            save_data()  # Сохраняем данные после удаления

        # Добавление заголовка даты, если его еще нет
        if time_now not in cards_by_date:
            header = ft.Column([
                ft.Divider(thickness=1),
                ft.Text(f'{time_now}', size=16, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                ft.Divider(thickness=1)
            ])
            expanses_list.controls.append(header)
            cards_by_date[time_now] = {
                "header": header,
                "cards": []
            }

        # Добавление карточки в список
        cards_by_date[time_now]["cards"].append(new_card)
        expanses_list.controls.append(new_card)
        page.update()

    # ===== ФУНКЦИИ =====
    
    def calculate_sum(e):
        """Подсчет суммы выбранных расходов"""
        nonlocal total_sum
        total_sum = 0
        
        # Проверяем, есть ли выбранные элементы
        has_selected = False
        for date in cards_by_date:
            for card in cards_by_date[date]["cards"]:
                checkbox = card.content.content.controls[2]
                if checkbox.value:
                    has_selected = True
                    break
            if has_selected:
                break
        
        # Если ничего не выбрано, показываем уведомление
        if not has_selected:
            page.open(ft.SnackBar(ft.Text('Выберите расходы для подсчета!'), bgcolor=ft.Colors.RED_400, duration=1500))
            return
        
        # Если есть выбранные элементы, считаем сумму
        for date in cards_by_date:
            for card in cards_by_date[date]["cards"]:
                # Проверяем, выбран ли чекбокс
                checkbox = card.content.content.controls[2]
                if checkbox.value:
                    # Получаем строку с ценой из карточки
                    price_text = card.content.content.controls[0].controls[1].value
                    # Извлекаем числовое значение
                    price_value = float(price_text.split(': ')[1].split(' ')[0])
                    total_sum += price_value
        
        # Создаем диалог с результатом
        result_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Результат"),
            content=ft.Text(f"Сумма выбранных расходов: {total_sum} BYN", size=18),
            actions=[
                ft.TextButton("Хорошо", on_click=lambda e: page.close(result_dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Показываем диалог
        page.open(result_dialog)

    def create_card(e):
        """Создание новой карточки расхода"""
        months = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]

        now = datetime.now()
        day = str(now.day)
        month = months[now.month - 1]

        time_now = f"{day} {month}"

        # Проверка ввода
        if title.value == '':
            page.open(ft.SnackBar(ft.Text('Введите название!'), bgcolor=ft.Colors.RED_300, duration=1500))
            return
        elif price.value == '':
            page.open(ft.SnackBar(ft.Text('Введите цену!'), bgcolor=ft.Colors.RED_400, duration=1500))
            return
        
        # Проверка, что введено число
        try:
            float(price.value)
        except ValueError:
            page.open(ft.SnackBar(ft.Text('Цена должна быть числом!'), bgcolor=ft.Colors.RED_400, duration=1500))
            return
        
        # Создание карточки из введенных данных
        card_title = title.value
        card_price = price.value
        create_card_from_data(card_title, card_price, time_now)
        
        # Очистка полей ввода
        title.value = ''
        price.value = ''
        page.close(dialog)
        
        # Сохраняем данные после добавления
        save_data()

    def delete_selected(e):
        """Удаление выбранных расходов"""
        nonlocal confirm_delete_dialog
        
        # Проверяем, есть ли выбранные элементы
        has_selected = False
        for date in cards_by_date:
            for card in cards_by_date[date]["cards"]:
                checkbox = card.content.content.controls[2]
                if checkbox.value:
                    has_selected = True
                    break
            if has_selected:
                break
        
        # Если ничего не выбрано, показываем уведомление
        if not has_selected:
            page.open(ft.SnackBar(ft.Text('Выберите расходы для удаления!'), bgcolor=ft.Colors.RED_400, duration=1500))
            return
        
        # Если есть выбранные элементы, показываем диалог подтверждения
        confirm_delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text('Удалить выбранные расходы?'),
            actions=[
                ft.TextButton('Да', on_click=perform_delete),
                ft.TextButton('Нет', on_click=lambda e: page.close(confirm_delete_dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        page.open(confirm_delete_dialog)
        
    def perform_delete(e):
        """Выполнение удаления выбранных расходов"""
        nonlocal confirm_delete_dialog
        
        # Собираем все карточки для удаления
        for date in list(cards_by_date.keys()):
            cards_to_remove = []
            for card in cards_by_date[date]["cards"]:
                checkbox = card.content.content.controls[2]
                if checkbox.value:
                    cards_to_remove.append(card)
                    expanses_list.controls.remove(card)
            
            # Удаляем карточки из списка
            for card in cards_to_remove:
                cards_by_date[date]["cards"].remove(card)
            
            # Если все карточки даты удалены, удаляем заголовок
            if len(cards_by_date[date]["cards"]) == 0:
                expanses_list.controls.remove(cards_by_date[date]["header"])
                del cards_by_date[date]
        
        page.close(confirm_delete_dialog)
        page.update()
        
        # Сохраняем данные после удаления
        save_data()
    
    def select_all(e):
        """Выбор всех расходов или снятие выбора со всех"""
        all_selected = True
        
        # Проверяем, все ли уже выбраны
        for date in cards_by_date:
            for card in cards_by_date[date]["cards"]:
                checkbox = card.content.content.controls[2]
                if not checkbox.value:
                    all_selected = False
                    break
            if not all_selected:
                break
        
        # Устанавливаем значение для всех чекбоксов
        for date in cards_by_date:
            for card in cards_by_date[date]["cards"]:
                checkbox = card.content.content.controls[2]
                checkbox.value = not all_selected
        
        page.update()
        
        # Показываем уведомление
        if not all_selected:
            page.open(ft.SnackBar(ft.Text('Все расходы выбраны!'), bgcolor=ft.Colors.GREEN_400, duration=1500))
        else:
            page.open(ft.SnackBar(ft.Text('Выбор снят со всех расходов!'), bgcolor=ft.Colors.BLUE_400, duration=1500))

    # ===== ЭЛЕМЕНТЫ ИНТЕРФЕЙСА =====
    
    # Поля ввода
    title = ft.TextField(
        label='Введите название',
        border_radius=8,
        focused_border_color=ft.Colors.BLUE_400
    )
    
    price = ft.TextField(
        label='Введите цену',
        hint_text='Только числа',
        border_radius=8,
        focused_border_color=ft.Colors.BLUE_400
    )

    # Заголовок приложения
    title_text = ft.Text(
        'Мои расходы',
        size=30,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_700
    )

    # Кнопка добавления расхода
    add_btn = ft.IconButton(
        icon=ft.Icons.ADD,
        tooltip='Добавить расход',
        icon_size=40,
        bgcolor=ft.Colors.BLUE_300,
        icon_color=ft.Colors.WHITE,
        on_click=lambda e: page.open(dialog)
    )

    # Кнопка подсчета суммы
    sum_btn = ft.ElevatedButton(
        'Посчитать',
        bgcolor=ft.Colors.BLUE_300,
        color=ft.Colors.WHITE,
        width=120,
        height=45,
        on_click=calculate_sum,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )

    # Диалог добавления расхода
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text('Введите данные'),
        content=ft.Column([
            title,
            price
        ], height=120, spacing=20),
        actions=[
            ft.TextButton('Сохранить', on_click=create_card),
            ft.TextButton('Отмена', on_click=lambda e: page.close(dialog))
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    # Список расходов
    expanses_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=10,
        auto_scroll=True
    )

    # Кнопка удаления выбранных расходов
    delete_selected_btn = ft.IconButton(
        icon=ft.Icons.DELETE,
        tooltip='Удалить выбранные',
        icon_size=40,
        bgcolor=ft.Colors.RED_300,
        icon_color=ft.Colors.WHITE,
        on_click=delete_selected
    )
    
    # Кнопка "Выбрать все"
    select_all_btn = ft.IconButton(
        icon=ft.Icons.SELECT_ALL,
        tooltip='Выбрать все/Снять выбор',
        icon_size=40,
        bgcolor=ft.Colors.GREEN_300,
        icon_color=ft.Colors.WHITE,
        on_click=select_all
    )

    # ===== СБОРКА ИНТЕРФЕЙСА =====
    page.add(
        ft.Stack(
            [
                ft.Column([
                    ft.Row([title_text], alignment=ft.MainAxisAlignment.CENTER),
                    expanses_list,
                    ft.Container( 
                        content=sum_btn,
                        bgcolor=ft.Colors.BLUE_100,
                        padding=10,
                        border_radius=25,
                        alignment=ft.alignment.center,
                        height=62
                    )
                ]),
                ft.Container(
                    content=add_btn,
                    right=3,
                    bottom=3,
                    alignment=ft.alignment.bottom_right
                ),
                ft.Container(
                    content=delete_selected_btn,
                    left=3,
                    bottom=3,
                    alignment=ft.alignment.bottom_left
                ),
                ft.Container(
                    content=select_all_btn,
                    top=3,
                    right=3,
                    alignment=ft.alignment.top_right
                )
            ],
            expand=True
        )
    )
    
    # Загружаем данные при запуске
    load_data()