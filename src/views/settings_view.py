import flet as ft
from datetime import datetime

class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func

        start_val = self.schedule.semester_start.strftime("%d/%m/%Y") if self.schedule.semester_start else ""
        end_val = self.schedule.semester_end.strftime("%d/%m/%Y") if self.schedule.semester_end else ""

        self.start_input = ft.TextField(label="תאריך התחלה (DD/MM/YYYY)", value=start_val)
        self.end_input = ft.TextField(label="תאריך סיום (DD/MM/YYYY)", value=end_val)

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(
                    content=ft.Text("חזור", color="white", weight="bold"), 
                    on_click=lambda _: self.change_screen("schedule")
                ),
                ft.Text("הגדרות סמסטר", size=20, weight="bold", color="white"),
                ft.Container(width=40)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1976D2",
            padding=5,
            border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("ערוך את תאריכי הסמסטר שלך:", size=16),
                    self.start_input,
                    self.end_input,
                    ft.ElevatedButton("שמור שינויים", on_click=self.save_settings, bgcolor="#43A047", color="white")
                ], spacing=15)
            )
        ]

    def save_settings(self, e):
        try:
            datetime.strptime(self.start_input.value, "%d/%m/%Y")
            datetime.strptime(self.end_input.value, "%d/%m/%Y")
            
            self.schedule.set_semester(self.start_input.value, self.end_input.value)
            
            snack = ft.SnackBar(ft.Text("ההגדרות נשמרו בהצלחה!"))
            self.app_page.snack_bar = snack
            snack.open = True
            self.app_page.update()
            
            self.change_screen("schedule")
        except ValueError:
            snack = ft.SnackBar(ft.Text("שגיאה! אנא השתמש בפורמט DD/MM/YYYY"))
            self.app_page.snack_bar = snack
            snack.open = True
            self.app_page.update()