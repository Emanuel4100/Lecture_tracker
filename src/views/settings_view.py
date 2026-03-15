import flet as ft
from datetime import datetime
from utils.i18n import t, translator

class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func

        start_val = self.schedule.semester_start.strftime("%d/%m/%Y") if self.schedule.semester_start else t("common.not_set")
        end_val = self.schedule.semester_end.strftime("%d/%m/%Y") if self.schedule.semester_end else t("common.not_set")

        self.start_text = ft.Text(start_val, size=16, weight="bold", color="#1976D2")
        self.end_text = ft.Text(end_val, size=16, weight="bold", color="#1976D2")

        self.start_picker = ft.DatePicker(on_change=self.start_date_changed)
        self.end_picker = ft.DatePicker(on_change=self.end_date_changed)
        
        if self.start_picker not in self.app_page.overlay:
            self.app_page.overlay.extend([self.start_picker, self.end_picker])

        self.weekend_switch = ft.Switch(label=t("settings.show_weekend"), value=self.schedule.show_weekend)
        
        self.lang_dropdown = ft.Dropdown(
            label=t("settings.language"), 
            options=[ft.dropdown.Option(key="he", text="עברית (Hebrew)"), ft.dropdown.Option(key="en", text="English (אנגלית)")], 
            value=self.schedule.language, 
            width=200
        )

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Row([ft.Image(src="icons/arrow_forward.svg", width=18, height=18, color="white"), ft.Text(t("common.back"), color="white", weight="bold")]), on_click=lambda _: self.change_screen("schedule")),
                ft.Text(t("settings.title"), size=20, weight="bold", color="white"),
                ft.Container(width=40)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1976D2", padding=5, border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text(t("settings.dates"), size=16),
                    ft.Row([
                        ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/calendar_month.svg", width=20, height=20, color="white"), ft.Text(t("settings.choose_start"))]), on_click=lambda _: self.open_picker(self.start_picker)),
                        self.start_text
                    ]),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/calendar_month.svg", width=20, height=20, color="white"), ft.Text(t("settings.choose_end"))]), on_click=lambda _: self.open_picker(self.end_picker)),
                        self.end_text
                    ]),
                    ft.Divider(),
                    ft.Text(t("settings.display"), size=16),
                    self.weekend_switch,
                    self.lang_dropdown,
                    ft.Container(height=10),
                    ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/save.svg", width=20, height=20, color="white"), ft.Text(t("common.save"))]), on_click=self.save_settings, bgcolor="#43A047", color="white")
                ], spacing=15)
            )
        ]

    def open_picker(self, picker): picker.open = True; self.app_page.update()

    def start_date_changed(self, e):
        if self.start_picker.value: self.start_text.value = self.start_picker.value.strftime("%d/%m/%Y"); self.update()

    def end_date_changed(self, e):
        if self.end_picker.value: self.end_text.value = self.end_picker.value.strftime("%d/%m/%Y"); self.update()

    def save_settings(self, e):
        if self.start_text.value == t("common.not_set") or self.end_text.value == t("common.not_set"):
            self.app_page.snack_bar = ft.SnackBar(ft.Text(t("onboarding.dates_error"))); self.app_page.snack_bar.open = True; self.app_page.update(); return
            
        self.schedule.show_weekend = self.weekend_switch.value
        self.schedule.set_semester(self.start_text.value, self.end_text.value)
        
        if self.schedule.language != self.lang_dropdown.value:
            self.schedule.language = self.lang_dropdown.value
            translator.set_language(self.schedule.language)
            self.app_page.rtl = (self.schedule.language == "he")
            
        self.schedule.save_to_file()
        
        self.app_page.snack_bar = ft.SnackBar(ft.Text(t("settings.save_success")))
        self.app_page.snack_bar.open = True
        self.app_page.update()
        self.change_screen("schedule")