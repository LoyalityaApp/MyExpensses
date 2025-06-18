import flet as ft
from flet_app import main
import os

# Запуск приложения
if __name__ == "__main__":
    # Получаем порт из переменной окружения или используем 10000 по умолчанию
    port = int(os.environ.get("PORT", 10000))
    ft.app(main, view=ft.AppView.WEB_BROWSER, port=port)ы