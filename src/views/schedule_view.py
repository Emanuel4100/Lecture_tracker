import flet as ft
from components.lecture_card import LectureCard

class ScheduleView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page 
        self.schedule = schedule
        self.change_screen = change_screen_func

        self.days = list(self.schedule.days.keys())
        self.selected_day = self.days[0]

        self.tabs_row = ft.Row(scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER)
        self.content_area = ft.Container(expand=True)

        self.build_tabs()
        self.update_content()

        header = ft.Container(
            content=ft.Text("מערכת השעות שלי", size=24, weight="bold", color="white"),
            bgcolor="#1976D2",
            padding=15,
            alignment=ft.Alignment(0, 0), 
            border_radius=10
        )

        # Fixed: Using string literal "add" instead of ft.icons.ADD
        add_btn = ft.FloatingActionButton(
            icon="add", 
            bgcolor="#FFC107", 
            on_click=lambda _: self.change_screen("add")
        )

        self.controls = [
            header,
            self.tabs_row,
            self.content_area,
            ft.Row([add_btn], alignment=ft.MainAxisAlignment.END)
        ]

    def build_tabs(self):
        self.tabs_row.controls.clear()
        
        for day in self.days:
            is_selected = (day == self.selected_day)
            
            btn = ft.TextButton(
                content=ft.Text(
                    day, 
                    color="#1976D2" if is_selected else "grey",
                    weight="bold" if is_selected else "normal"
                ),
                style=ft.ButtonStyle(
                    bgcolor="#E3F2FD" if is_selected else "transparent",
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                on_click=self.create_tab_click_handler(day)
            )
            self.tabs_row.controls.append(btn)

    def create_tab_click_handler(self, day):
        def on_click(e):
            self.selected_day = day
            self.build_tabs()
            self.update_content()
            self.update()
        return on_click

    def update_content(self):
        day_list_view = ft.ListView(expand=True, padding=20)
        lectures = self.schedule.days[self.selected_day]
        
        if not lectures:
            day_list_view.controls.append(
                ft.Container(
                    content=ft.Text(f"אין הרצאות ביום {self.selected_day} 🎉", size=16, color="grey"), 
                    alignment=ft.Alignment(0, 0), 
                    padding=50
                )
            )
        else:
            for lec in lectures:
                day_list_view.controls.append(LectureCard(lec))
        
        self.content_area.content = day_list_view