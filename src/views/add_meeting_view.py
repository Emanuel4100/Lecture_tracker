import flet as ft
from utils.i18n import t

class AddMeetingView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func

        course_options = [ft.dropdown.Option(key=c.course_id, text=c.title) for c in self.schedule.courses]
        self.course_dropdown = ft.Dropdown(label=t("meeting_form.course"), options=course_options, col={"xs": 12, "sm": 6})
        
        self.type_dropdown = ft.Dropdown(label=t("course_form.type"), options=[ft.dropdown.Option(key="meeting_types.lecture", text=t("meeting_types.lecture")), ft.dropdown.Option(key="meeting_types.practice", text=t("meeting_types.practice")), ft.dropdown.Option(key="meeting_types.lab", text=t("meeting_types.lab"))], value="meeting_types.lecture", col={"xs": 6, "sm": 4})
        self.day_dropdown = ft.Dropdown(label=t("course_form.day"), options=[ft.dropdown.Option(key=f"days.{d}", text=t(f"days.{d}")) for d in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]], col={"xs": 6, "sm": 4})
        
        times = [f"{h:02d}:{m:02d}" for h in range(8, 24) for m in (0, 30)]
        self.start_dropdown = ft.Dropdown(label=t("course_form.start"), options=[ft.dropdown.Option(tm) for tm in times[:-1]], value="10:00", col={"xs": 6, "sm": 4})
        self.start_dropdown.on_change = self.handle_start_change
        
        self.end_dropdown = ft.Dropdown(label=t("course_form.end"), options=[ft.dropdown.Option(tm) for tm in times[1:]], value="11:00", col={"xs": 6, "sm": 6})
        self.location_input = ft.TextField(label=t("course_form.location"), hint_text=t("course_form.location_hint"), prefix=ft.Container(content=ft.Icon("location_on", size=18, color="onSurfaceVariant"), margin=ft.margin.only(left=10, right=10)), col={"xs": 12, "sm": 4})

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Row([ft.Icon("arrow_forward", size=18, color="onPrimary"), ft.Text(t("common.back"), color="onPrimary", weight="bold")]), on_click=lambda _: self.change_screen("schedule")),
                ft.Text(t("meeting_form.title"), size=20, weight="bold", color="onPrimary")
            ]),
            bgcolor="primary", padding=5, border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text(t("meeting_form.details"), weight="bold", size=16, color="onSurface"),
                    ft.ResponsiveRow([self.course_dropdown]),
                    ft.Divider(color="outlineVariant"),
                    ft.Text(t("course_form.add_times"), weight="bold", size=16, color="onSurface"),
                    ft.ResponsiveRow([self.type_dropdown, self.day_dropdown, self.start_dropdown, self.end_dropdown, self.location_input]),
                    ft.Divider(color="outlineVariant", height=30),
                    ft.ElevatedButton(content=ft.Row([ft.Icon("save", size=20, color="onPrimary"), ft.Text(t("meeting_form.save_btn"))], alignment=ft.MainAxisAlignment.CENTER), style=ft.ButtonStyle(bgcolor="primary", color="onPrimary"), on_click=self.save_meeting, height=45)
                ], spacing=15)
            )
        ]

    def handle_start_change(self, e):
        if self.start_dropdown.value:
            h, m = map(int, self.start_dropdown.value.split(':'))
            h += 1
            if h > 23: h = 23
            new_end = f"{h:02d}:{m:02d}"
            if any(opt.key == new_end for opt in self.end_dropdown.options):
                self.end_dropdown.value = new_end
                self.app_page.update()

    def save_meeting(self, e):
        if not self.course_dropdown.value or not self.day_dropdown.value or not self.start_dropdown.value or not self.end_dropdown.value:
            self.app_page.overlay.append(ft.SnackBar(ft.Text(t("course_form.missing_info"), color="onError"), bgcolor="error", open=True))
            self.app_page.update()
            return
            
        course = next((c for c in self.schedule.courses if c.course_id == self.course_dropdown.value), None)
        if course:
            course.add_weekly_meeting(self.schedule.semester_start, self.schedule.semester_end, self.day_dropdown.value, self.start_dropdown.value, self.end_dropdown.value, self.location_input.value, self.type_dropdown.value)
            self.schedule.save_to_file()
            self.app_page.overlay.append(ft.SnackBar(ft.Text(t("meeting_form.success_msg", title=course.title)), open=True))
            self.app_page.update()
            self.change_screen("schedule")