import flet as ft
from datetime import datetime
from utils.i18n import translator, t

class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func

        self.lang_dropdown = ft.Dropdown(label=t("settings.language"), options=[ft.dropdown.Option("he", "עברית"), ft.dropdown.Option("en", "English")], value=self.schedule.language, width=200)
        self.lang_dropdown.on_change = self.change_language

        self.weekend_switch = ft.Switch(label=t("settings.show_weekend"), value=self.schedule.show_weekend, on_change=self.toggle_weekend)
        
        self.numbers_switch = ft.Switch(
            label=t("settings.enable_numbering", default="הפעל מספור אוטומטי"),
            value=self.schedule.enable_meeting_numbers,
            on_change=self.toggle_numbers
        )

        def pick_date(e, is_start):
            def handle_change(ev):
                val = ev.control.value
                if val:
                    if isinstance(val, str): parsed_date = datetime.strptime(val[:10], "%Y-%m-%d").date()
                    elif hasattr(val, 'date'): parsed_date = val.date()
                    else: parsed_date = val

                    if is_start: self.schedule.semester_start = parsed_date
                    else: self.schedule.semester_end = parsed_date
                    self.update_date_texts(); self.recalc_all()

            picker = ft.DatePicker(first_date=datetime(2020, 1, 1), last_date=datetime(2030, 12, 31), on_change=handle_change)
            self.app_page.overlay.append(picker); picker.open = True; self.app_page.update()

        self.start_text = ft.Text("")
        self.end_text = ft.Text("")
        self.update_date_texts()

        date_section = ft.Column([
            ft.Text(t("settings.dates"), weight="bold"),
            ft.Row([ft.ElevatedButton(t("settings.change_start"), icon="calendar_month", on_click=lambda e: pick_date(e, True)), self.start_text]),
            ft.Row([ft.ElevatedButton(t("settings.change_end"), icon="calendar_month", on_click=lambda e: pick_date(e, False)), self.end_text])
        ], spacing=10)

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Row([ft.Icon("arrow_forward", size=18, color="onPrimary"), ft.Text(t("common.back"), color="onPrimary", weight="bold")]), on_click=lambda _: self.change_screen("schedule")),
                ft.Text(t("schedule.settings"), size=20, weight="bold", color="onPrimary")
            ]), bgcolor="primary", padding=5, border_radius=10
        )

        self.controls = [header, ft.Container(padding=20, content=ft.Column([self.lang_dropdown, self.weekend_switch, self.numbers_switch, ft.Divider(height=30), date_section], spacing=20))]

    def update_date_texts(self):
        if self.schedule.semester_start: self.start_text.value = self.schedule.semester_start.strftime("%d/%m/%Y")
        if self.schedule.semester_end: self.end_text.value = self.schedule.semester_end.strftime("%d/%m/%Y")
        
        # התיקון: מבצע רענון תצוגה רק אם הרכיב כבר נטען בהצלחה לעמוד!
        if self.page:
            self.update()

    def change_language(self, e):
        self.schedule.language = self.lang_dropdown.value
        translator.set_language(self.schedule.language)
        self.app_page.rtl = (self.schedule.language == "he")
        self.schedule.save_to_file(); self.app_page.update(); self.change_screen("settings") 

    def toggle_weekend(self, e): self.schedule.show_weekend = self.weekend_switch.value; self.schedule.save_to_file()
    def toggle_numbers(self, e): self.schedule.enable_meeting_numbers = self.numbers_switch.value; self.recalc_all()

    def recalc_all(self):
        if self.schedule.is_semester_set():
            for c in self.schedule.courses: c.recalculate_all_lectures(self.schedule.semester_start, self.schedule.semester_end, self.schedule.enable_meeting_numbers)
            self.schedule.save_to_file()