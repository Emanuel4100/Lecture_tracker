import flet as ft
import time
from models.lecture import Lecture

class AddLectureView(ft.View):
    def __init__(self, page: ft.Page, schedule):
        super().__init__(route="/add")
        self.page = page
        self.schedule = schedule

        # שדות הטופס
        self.title_input = ft.TextField(label="שם הקורס")
        self.lecturer_input = ft.TextField(label="שם המרצה")
        self.room_input = ft.TextField(label="חדר/אולם")
        self.day_dropdown = ft.Dropdown(
            label="יום בשבוע",
            options=[ft.dropdown.Option(day) for day in self.schedule.days.keys()]
        )
        self.start_input = ft.TextField(label="שעת התחלה (למשל 10:00)", width=150)
        self.end_input = ft.TextField(label="שעת סיום (למשל 12:00)", width=150)

        self.controls = [
            ft.AppBar(title=ft.Text("הוספת הרצאה"), bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE),
            ft.Container(
                padding=20,
                content=ft.Column([
                    self.title_input,
                    self.lecturer_input,
                    self.day_dropdown,
                    ft.Row([self.start_input, self.end_input]),
                    self.room_input,
                    ft.ElevatedButton("שמור הרצאה", on_click=self.save_lecture, bgcolor=ft.colors.GREEN_600, color=ft.colors.WHITE)
                ], spacing=15)
            )
        ]

    def save_lecture(self, e):
        # יצירת מזהה ייחודי פשוט בעזרת הזמן הנוכחי
        new_id = str(time.time())
        
        # יצירת אובייקט הרצאה חדש
        new_lec = Lecture(
            id=new_id,
            title=self.title_input.value,
            lecturer=self.lecturer_input.value,
            day=self.day_dropdown.value,
            start_time=self.start_input.value,
            end_time=self.end_input.value,
            room=self.room_input.value
        )
        
        # הוספה ללוח ושליחת הודעה
        self.schedule.add_lecture(new_lec)
        self.page.snack_bar = ft.SnackBar(ft.Text("ההרצאה נשמרה בהצלחה!"))
        self.page.snack_bar.open = True
        
        # חזרה לעמוד הראשי
        self.page.go("/")