import flet as ft
from components.lecture_card import LectureCard

class ScheduleView(ft.View):
    def __init__(self, page: ft.Page, schedule):
        super().__init__(route="/")
        self.page = page
        self.schedule = schedule

        self.tabs = ft.Tabs(selected_index=0, animation_duration=300, expand=True)

        for day_name, lectures in self.schedule.days.items():
            day_list_view = ft.ListView(expand=True, padding=20)
            
            if not lectures:
                day_list_view.controls.append(
                    ft.Container(content=ft.Text(f"אין הרצאות ביום {day_name} 🎉", size=16, color=ft.colors.GREY), alignment=ft.alignment.center, padding=50)
                )
            else:
                for lec in lectures:
                    day_list_view.controls.append(LectureCard(lec))
            
            self.tabs.tabs.append(ft.Tab(text=day_name, content=day_list_view))

        self.controls = [
            ft.AppBar(title=ft.Text("מערכת השעות שלי"), center_title=True, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE),
            self.tabs
        ]

        self.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, bgcolor=ft.colors.AMBER_500, on_click=lambda _: self.page.go("/add")
        )