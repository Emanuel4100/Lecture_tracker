import flet as ft
import time
from models.lecture import Lecture

class AddLectureView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func

        self.title_input = ft.TextField(label="שם הקורס")
        self.lecturer_input = ft.TextField(label="שם המרצה")
        self.room_input = ft.TextField(label="חדר/אולם")
        self.day_dropdown = ft.Dropdown(
            label="יום בשבוע",
            options=[ft.dropdown.Option(day) for day in self.schedule.days.keys()]
        )
        self.start_input = ft.TextField(label="שעת התחלה (למשל 10:00)", width=150)
        self.end_input = ft.TextField(label="שעת סיום (למשל 12:00)", width=150)

        header = ft.Container(
            content=ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_FORWARD, icon_color="white", on_click=lambda _: self.change_screen("schedule")),
                ft.Text("הוספת הרצאה", size=20, weight="bold", color="white")
            ]),
            bgcolor="#1976D2",
            padding=5,
            border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    self.title_input,
                    self.lecturer_input,
                    self.day_dropdown,
                    ft.Row([self.start_input, self.end_input]),
                    self.room_input,
                    ft.ElevatedButton("שמור הרצאה", on_click=self.save_lecture, bgcolor="#43A047", color="white")
                ], spacing=15)
            )
        ]

    def save_lecture(self, e):
        new_id = str(time.time())
        new_lec = Lecture(
            id=new_id,
            title=self.title_input.value,
            lecturer=self.lecturer_input.value,
            day=self.day_dropdown.value,
            start_time=self.start_input.value,
            end_time=self.end_input.value,
            room=self.room_input.value
        )
        
        self.schedule.add_lecture(new_lec)
        self.app_page.open(ft.SnackBar(ft.Text("ההרצאה נשמרה בהצלחה!")))
        self.change_screen("schedule")