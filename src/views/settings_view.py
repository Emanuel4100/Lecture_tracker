import flet as ft
from datetime import datetime

class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func

        start_val = self.schedule.semester_start.strftime("%d/%m/%Y") if self.schedule.semester_start else "לא הוגדר"
        end_val = self.schedule.semester_end.strftime("%d/%m/%Y") if self.schedule.semester_end else "לא הוגדר"

        self.start_text = ft.Text(start_val, size=16, weight="bold", color="#1976D2")
        self.end_text = ft.Text(end_val, size=16, weight="bold", color="#1976D2")

        self.start_picker = ft.DatePicker(on_change=self.start_date_changed)
        self.end_picker = ft.DatePicker(on_change=self.end_date_changed)
        
        if self.start_picker not in self.app_page.overlay:
            self.app_page.overlay.extend([self.start_picker, self.end_picker])

        self.weekend_switch = ft.Switch(label="הצג סופ״ש בלוח השבועי (שישי-שבת)", value=self.schedule.show_weekend)

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Text("חזור", color="white", weight="bold"), on_click=lambda _: self.change_screen("schedule")),
                ft.Text("הגדרות סמסטר", size=20, weight="bold", color="white"),
                ft.Container(width=40)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1976D2", padding=5, border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("תאריכי הסמסטר:", size=16),
                    ft.Row([
                        ft.ElevatedButton(content=ft.Row([ft.Text("📅"), ft.Text("בחר תחילת סמסטר")]), on_click=lambda _: self.open_picker(self.start_picker)),
                        self.start_text
                    ]),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(content=ft.Row([ft.Text("📅"), ft.Text("בחר סיום סמסטר")]), on_click=lambda _: self.open_picker(self.end_picker)),
                        self.end_text
                    ]),
                    ft.Divider(),
                    ft.Text("הגדרות תצוגה:", size=16),
                    self.weekend_switch,
                    ft.Container(height=10),
                    ft.ElevatedButton("שמור שינויים", on_click=self.save_settings, bgcolor="#43A047", color="white")
                ], spacing=15)
            )
        ]

    def open_picker(self, picker):
        picker.open = True
        self.app_page.update()

    def start_date_changed(self, e):
        if self.start_picker.value:
            self.start_text.value = self.start_picker.value.strftime("%d/%m/%Y")
            self.update()

    def end_date_changed(self, e):
        if self.end_picker.value:
            self.end_text.value = self.end_picker.value.strftime("%d/%m/%Y")
            self.update()

    def save_settings(self, e):
        if self.start_text.value == "לא נבחר" or self.end_text.value == "לא נבחר":
            self.app_page.snack_bar = ft.SnackBar(ft.Text("חובה לבחור תאריכים!"))
            self.app_page.snack_bar.open = True
            self.app_page.update()
            return
            
        self.schedule.show_weekend = self.weekend_switch.value
        self.schedule.set_semester(self.start_text.value, self.end_text.value)
        self.schedule.save_to_file()
        
        self.app_page.snack_bar = ft.SnackBar(ft.Text("ההגדרות נשמרו בהצלחה!"))
        self.app_page.snack_bar.open = True
        self.app_page.update()
        self.change_screen("schedule")