import flet as ft
from utils.i18n import t

class AddMeetingView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func

        # יצירת רשימת הקורסים הקיימים לבחירה
        course_options = [ft.dropdown.Option(key=c.course_id, text=c.title) for c in self.schedule.courses]

        self.course_dropdown = ft.Dropdown(label=t("add_meeting.select_course"), options=course_options, col={"xs": 12, "sm": 6})
        self.location_input = ft.TextField(label=t("course_form.location"), hint_text=t("course_form.location_hint"), col={"xs": 12, "sm": 6})
        
        self.type_dropdown = ft.Dropdown(label=t("course_form.type"), options=[ft.dropdown.Option(key="meeting_types.lecture", text=t("meeting_types.lecture")), ft.dropdown.Option(key="meeting_types.practice", text=t("meeting_types.practice")), ft.dropdown.Option(key="meeting_types.lab", text=t("meeting_types.lab"))], value="meeting_types.lecture", col={"xs": 6, "sm": 4, "md": 3})
        self.day_dropdown = ft.Dropdown(label=t("course_form.day"), options=[ft.dropdown.Option(key=f"days.{d}", text=t(f"days.{d}")) for d in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]], col={"xs": 6, "sm": 4, "md": 3})
        
        times = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in (0, 30)]
        self.start_dropdown = ft.Dropdown(label=t("course_form.start"), options=[ft.dropdown.Option(tm) for tm in times[:-1]], value="10:00", col={"xs": 6, "sm": 4, "md": 3})
        self.end_dropdown = ft.Dropdown(label=t("course_form.end"), options=[ft.dropdown.Option(tm) for tm in times[1:]], value="12:00", col={"xs": 6, "sm": 6, "md": 3})

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Row([ft.Image(src="icons/arrow_forward.svg", width=18, height=18, color="white"), ft.Text(t("common.back"), color="white", weight="bold")]), on_click=lambda _: self.change_screen("schedule")),
                ft.Text(t("add_meeting.title"), size=20, weight="bold", color="white")
            ]),
            bgcolor="#1976D2", padding=5, border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text(t("add_meeting.select_course"), weight="bold", size=16),
                    ft.ResponsiveRow([self.course_dropdown, self.location_input]),
                    ft.Divider(),
                    ft.Text(t("course_form.add_times"), weight="bold", size=16),
                    ft.ResponsiveRow([self.type_dropdown, self.day_dropdown, self.start_dropdown, self.end_dropdown]),
                    ft.Container(height=10),
                    ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/save.svg", width=20, height=20, color="white"), ft.Text(t("common.save"))], alignment=ft.MainAxisAlignment.CENTER), on_click=self.save_meeting, bgcolor="#43A047", color="white", height=45)
                ], spacing=15)
            )
        ]

    def save_meeting(self, e):
        course_id = self.course_dropdown.value
        if not course_id or not self.day_dropdown.value or not self.start_dropdown.value or not self.end_dropdown.value:
            self.app_page.snack_bar = ft.SnackBar(ft.Text(t("course_form.time_error"), color="red"))
            self.app_page.snack_bar.open = True
            self.app_page.update()
            return

        selected_course = next((c for c in self.schedule.courses if c.course_id == course_id), None)
        if selected_course:
            selected_course.add_weekly_meeting(
                self.schedule.semester_start, 
                self.schedule.semester_end, 
                self.day_dropdown.value, 
                self.start_dropdown.value, 
                self.end_dropdown.value, 
                self.location_input.value, 
                self.type_dropdown.value
            )
            self.schedule.save_to_file()
            self.app_page.snack_bar = ft.SnackBar(ft.Text(t("add_meeting.success_msg", title=selected_course.title)))
            self.app_page.snack_bar.open = True
            self.app_page.update()
            self.change_screen("schedule")