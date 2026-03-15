import flet as ft
import time
from datetime import datetime
from models.course import Course
from utils.i18n import t

class OnboardingView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func
        
        self.current_step = 0
        self.current_course_meetings = [] 
        self.added_courses = []
        self.content_area = ft.Container(expand=True, padding=20)
        
        self.start_picker = ft.DatePicker(on_change=self.start_date_changed)
        self.end_picker = ft.DatePicker(on_change=self.end_date_changed)
        if self.start_picker not in self.app_page.overlay: self.app_page.overlay.extend([self.start_picker, self.end_picker])
            
        self.start_text = ft.Text(t("common.not_selected"), size=16, weight="bold", color="#1976D2")
        self.end_text = ft.Text(t("common.not_selected"), size=16, weight="bold", color="#1976D2")
        self.build_ui()

    def build_ui(self):
        self.controls.clear()
        header = ft.Container(content=ft.Text(t("onboarding.title"), size=24, weight="bold", color="white"), bgcolor="#1976D2", padding=15, alignment=ft.Alignment(0, 0), border_radius=10)
        self.update_step_content()
        self.controls = [header, self.content_area]

    def next_step(self, e=None):
        self.current_step += 1
        self.update_step_content()
        self.update()

    def update_step_content(self):
        if self.current_step == 0: self.content_area.content = self.build_welcome_screen()
        elif self.current_step == 1: self.content_area.content = self.build_semester_dates_screen()
        elif self.current_step == 2: self.content_area.content = self.build_initial_courses_screen()
        elif self.current_step == 3: self.content_area.content = self.build_notifications_setup_screen()
        elif self.current_step == 4: self.content_area.content = self.build_tutorial_screen()

    def build_welcome_screen(self):
        return ft.Column([
            ft.Image(src="icons/school.svg", width=80, height=80, color="#1976D2"), 
            ft.Text(t("onboarding.welcome"), size=22, weight="bold", text_align="center"),
            ft.Container(height=30),
            ft.ElevatedButton(t("onboarding.create_semester"), on_click=self.next_step, bgcolor="#1976D2", color="white", width=200)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)

    def open_picker(self, picker): picker.open = True; self.app_page.update()

    def start_date_changed(self, e):
        if self.start_picker.value: self.start_text.value = self.start_picker.value.strftime("%d/%m/%Y"); self.update()

    def end_date_changed(self, e):
        if self.end_picker.value: self.end_text.value = self.end_picker.value.strftime("%d/%m/%Y"); self.update()

    def build_semester_dates_screen(self):
        return ft.Column([
            ft.Text(t("onboarding.step1_title"), size=20, weight="bold", color="#1976D2"),
            ft.Container(height=20),
            ft.Row([ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/calendar_month.svg", width=20, height=20, color="white"), ft.Text(t("onboarding.choose_start"))]), on_click=lambda _: self.open_picker(self.start_picker)), self.start_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Row([ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/calendar_month.svg", width=20, height=20, color="white"), ft.Text(t("onboarding.choose_end"))]), on_click=lambda _: self.open_picker(self.end_picker)), self.end_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=30),
            ft.ElevatedButton(t("onboarding.next_step"), on_click=self.save_dates_and_continue, bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def save_dates_and_continue(self, e):
        if self.start_text.value == t("common.not_selected") or self.end_text.value == t("common.not_selected"):
            self.app_page.snack_bar = ft.SnackBar(ft.Text(t("onboarding.dates_error"))); self.app_page.snack_bar.open = True; self.app_page.update(); return
        self.schedule.set_semester(self.start_text.value, self.end_text.value)
        self.next_step()

    def calc_duration_text(self, start, end):
        h1, m1 = map(int, start.split(':'))
        h2, m2 = map(int, end.split(':'))
        total_mins = (h2 * 60 + m2) - (h1 * 60 + m1)
        if total_mins <= 0: return None
        hours = total_mins // 60
        mins = total_mins % 60
        res = []
        if hours == 1: res.append(t("duration.h1"))
        elif hours == 2: res.append(t("duration.h2"))
        elif hours > 2: res.append(t("duration.h_many", h=hours))
        if mins > 0:
            if hours > 0: res.append(t("duration.and_m", m=mins))
            else: res.append(t("duration.m", m=mins))
        return " ".join(res)

    def build_initial_courses_screen(self):
        self.c_title = ft.TextField(label=t("course_form.name"), col={"xs": 12, "sm": 6})
        self.c_code = ft.TextField(label=t("course_form.code"), col={"xs": 6, "sm": 3})
        self.c_location = ft.TextField(label=t("course_form.location"), col={"xs": 6, "sm": 3})
        
        self.c_type = ft.Dropdown(label=t("course_form.type"), options=[ft.dropdown.Option(key="meeting_types.lecture", text=t("meeting_types.lecture")), ft.dropdown.Option(key="meeting_types.practice", text=t("meeting_types.practice")), ft.dropdown.Option(key="meeting_types.lab", text=t("meeting_types.lab"))], value="meeting_types.lecture", col={"xs": 6, "sm": 3})
        self.c_day = ft.Dropdown(label=t("course_form.day"), options=[ft.dropdown.Option(key=f"days.{d}", text=t(f"days.{d}")) for d in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]], col={"xs": 6, "sm": 3})
        
        times = [f"{h:02d}:{m:02d}" for h in range(8, 23) for m in (0, 30)]
        self.c_start = ft.Dropdown(label=t("course_form.start"), options=[ft.dropdown.Option(time) for time in times[:-1]], value="10:00", col={"xs": 6, "sm": 3})
        self.c_end = ft.Dropdown(label=t("course_form.end"), options=[ft.dropdown.Option(time) for time in times[1:]], value="12:00", col={"xs": 6, "sm": 3})
        
        self.tree_view = ft.Column(spacing=10)
        self.added_courses_list = ft.ListView(height=80, spacing=5)

        return ft.Column([
            ft.Text(t("onboarding.step2_title"), size=20, weight="bold", color="#1976D2"),
            ft.ResponsiveRow([self.c_title, self.c_code, self.c_location], alignment=ft.MainAxisAlignment.CENTER),
            ft.ResponsiveRow([self.c_type, self.c_day, self.c_start, self.c_end], alignment=ft.MainAxisAlignment.CENTER),
            ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/add_circle.svg", width=20, height=20, color="white"), ft.Text(t("course_form.add_time_btn"))]), on_click=self.add_meeting_to_temp, bgcolor="#F57C00", color="white"),
            ft.Container(content=self.tree_view, margin=ft.margin.only(top=10, bottom=10)),
            ft.ElevatedButton(content=ft.Row([ft.Image(src="icons/save.svg", width=20, height=20, color="white"), ft.Text(t("course_form.save_temp_btn"))]), on_click=self.save_temp_course, bgcolor="#1976D2", color="white"),
            ft.Divider(),
            self.added_courses_list,
            ft.ElevatedButton(t("onboarding.next_step"), on_click=self.next_step, bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)

    def add_meeting_to_temp(self, e):
        if not self.c_day.value or not self.c_start.value or not self.c_end.value: return
        dur_text = self.calc_duration_text(self.c_start.value, self.c_end.value)
        if not dur_text:
            self.app_page.snack_bar = ft.SnackBar(ft.Text(t("course_form.time_error"), color="red")); self.app_page.snack_bar.open = True; self.app_page.update(); return
            
        meeting = {"day_key": self.c_day.value, "start": self.c_start.value, "end": self.c_end.value, "location": self.c_location.value, "type_key": self.c_type.value, "dur_text": dur_text}
        self.current_course_meetings.append(meeting)
        self.update_tree_view()
        self.app_page.update()

    def update_tree_view(self):
        self.tree_view.controls.clear()
        if not self.current_course_meetings: return

        groups = {"meeting_types.lecture": [], "meeting_types.practice": [], "meeting_types.lab": []}
        for m in self.current_course_meetings: groups[m["type_key"]].append(m)

        c_title = self.c_title.value if self.c_title.value else t("course_form.new_course_def")
        c_code = f" ({self.c_code.value})" if self.c_code.value else ""
        tree_nodes = [ft.Row([ft.Image(src="icons/menu_book.svg", width=20, height=20, color="#1976D2"), ft.Text(f"{c_title}{c_code}", size=16, weight="bold", color="#1976D2")])]
        
        for m_type_key, m_list in groups.items():
            if not m_list: continue
            plural_key = m_type_key.replace("meeting_types.", "plurals.")
            type_col = ft.Column([ft.Text(t(plural_key), weight="bold", color="black87")])
            
            for m in m_list:
                loc_text = f" | {m['location']}" if m['location'] else ""
                type_col.controls.append(ft.Row([
                    ft.Image(src="icons/schedule.svg", width=14, height=14, color="grey600"),
                    ft.Text(f"{t(m['day_key'])}, {m['start']} - {m['end']} | {m['dur_text']}{loc_text}", color="grey700", size=13)
                ]))
            tree_nodes.append(ft.Container(content=type_col, border=ft.border.only(right=ft.border.BorderSide(2, "#E0E0E0")), padding=ft.padding.only(right=15), margin=ft.margin.only(right=10)))
            
        self.tree_view.controls.extend(tree_nodes)

    def save_temp_course(self, e):
        if not self.c_title.value or len(self.current_course_meetings) == 0: return
        new_course = Course(course_id=str(time.time()), title=self.c_title.value, lecturer="לא הוגדר", course_code=self.c_code.value)
        for m in self.current_course_meetings:
            new_course.add_weekly_meeting(self.schedule.semester_start, self.schedule.semester_end, m["day_key"], m["start"], m["end"], m["location"], m["type_key"])
        self.schedule.add_course(new_course)
        
        self.added_courses_list.controls.append(ft.Row([ft.Image(src="icons/check_circle.svg", width=16, height=16, color="green"), ft.Text(t("course_form.success_msg", title=self.c_title.value), color="green")]))
        self.current_course_meetings.clear(); self.tree_view.controls.clear(); self.c_title.value = ""; self.c_code.value = ""
        self.app_page.update()

    def build_notifications_setup_screen(self):
        options = [ft.dropdown.Option(str(m)) for m in [0, 5, 10, 15, 30, 60]]
        self.notif_before = ft.Dropdown(label=t("onboarding.notify_before"), options=options, value="15", width=150)
        return ft.Column([
            ft.Image(src="icons/notifications_active.svg", width=60, height=60, color="#1976D2"),
            ft.Text(t("onboarding.step3_title"), size=20, weight="bold", color="#1976D2"),
            self.notif_before, ft.Container(height=20),
            ft.ElevatedButton(t("onboarding.continue"), on_click=lambda _: self.next_step(), bgcolor="#43A047", color="white")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def build_tutorial_screen(self):
        return ft.Column([
            ft.Text(t("onboarding.step4_title"), size=20, weight="bold", color="#1976D2"),
            ft.Container(height=20),
            ft.ElevatedButton(t("onboarding.finish_go"), on_click=lambda _: self.change_screen("schedule"), bgcolor="#1976D2", color="white", width=280)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)