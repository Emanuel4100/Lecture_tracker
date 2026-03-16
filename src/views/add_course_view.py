import flet as ft
import time
from models.course import Course
from utils.i18n import t 

class AddCourseView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func
        self.weekly_meetings = [] 

        self.title_input = ft.TextField(label=t("course_form.name"), hint_text=t("course_form.name_hint"), col={"xs": 12, "sm": 8})
        self.code_input = ft.TextField(label=t("course_form.code"), hint_text=t("course_form.code_hint"), col={"xs": 12, "sm": 4})
        
        self.has_lecturer = ft.Checkbox(label=t("course_form.add_lecturer"), value=False, on_change=self.toggle_optional_fields)
        self.has_link = ft.Checkbox(label=t("course_form.add_link"), value=False, on_change=self.toggle_optional_fields)
        
        self.lecturer_input = ft.TextField(label=t("course_form.lecturer"), prefix=ft.Container(content=ft.Icon("person", size=18, color="onSurfaceVariant"), margin=ft.margin.only(left=10, right=10)), visible=False, col={"xs": 12, "sm": 6})
        self.link_input = ft.TextField(label=t("course_form.link"), hint_text=t("course_form.link_hint"), prefix=ft.Container(content=ft.Icon("link", size=18, color="onSurfaceVariant"), margin=ft.margin.only(left=10, right=10)), visible=False, col={"xs": 12, "sm": 6})
        
        self.type_dropdown = ft.Dropdown(label=t("course_form.type"), options=[ft.dropdown.Option(key="meeting_types.lecture", text=t("meeting_types.lecture")), ft.dropdown.Option(key="meeting_types.practice", text=t("meeting_types.practice")), ft.dropdown.Option(key="meeting_types.lab", text=t("meeting_types.lab"))], value="meeting_types.lecture", col={"xs": 6, "sm": 4, "md": 2})
        self.day_dropdown = ft.Dropdown(label=t("course_form.day"), options=[ft.dropdown.Option(key=f"days.{d}", text=t(f"days.{d}")) for d in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]], col={"xs": 6, "sm": 4, "md": 2})
        
        times = [f"{h:02d}:{m:02d}" for h in range(8, 24) for m in (0, 30)]
        self.start_dropdown = ft.Dropdown(label=t("course_form.start"), options=[ft.dropdown.Option(tm) for tm in times[:-1]], value="10:00", col={"xs": 6, "sm": 4, "md": 2})
        self.start_dropdown.on_change = self.handle_start_change
        
        self.end_dropdown = ft.Dropdown(label=t("course_form.end"), options=[ft.dropdown.Option(tm) for tm in times[1:]], value="11:00", col={"xs": 6, "sm": 6, "md": 2})
        self.location_input = ft.TextField(label=t("course_form.location"), hint_text=t("course_form.location_hint"), prefix=ft.Container(content=ft.Icon("location_on", size=18, color="onSurfaceVariant"), margin=ft.margin.only(left=10, right=10)), col={"xs": 12, "sm": 6, "md": 4})
        
        self.tree_view = ft.Column(spacing=10)

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Row([ft.Icon("arrow_forward", size=18, color="onPrimary"), ft.Text(t("common.back"), color="onPrimary", weight="bold")]), on_click=lambda _: self.change_screen("schedule")),
                ft.Text(t("course_form.title_add"), size=20, weight="bold", color="onPrimary")
            ]),
            bgcolor="primary", padding=5, border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20, expand=True,
                content=ft.Column([
                    ft.Text(t("course_form.details"), weight="bold", size=16, color="onSurface"),
                    ft.ResponsiveRow([self.title_input, self.code_input]),
                    ft.Row([self.has_lecturer, self.has_link]),
                    ft.ResponsiveRow([self.lecturer_input, self.link_input]),
                    ft.Divider(color="outlineVariant"),
                    ft.Text(t("course_form.add_times"), weight="bold", size=16, color="onSurface"),
                    ft.ResponsiveRow([self.type_dropdown, self.day_dropdown, self.start_dropdown, self.end_dropdown, self.location_input]),
                    ft.ElevatedButton(content=ft.Row([ft.Icon("add_circle", size=20, color="onSecondaryContainer"), ft.Text(t("course_form.add_time_btn"))], alignment=ft.MainAxisAlignment.CENTER), style=ft.ButtonStyle(bgcolor="secondaryContainer", color="onSecondaryContainer"), on_click=self.add_meeting),
                    ft.Container(content=self.tree_view, margin=ft.margin.only(top=10, bottom=10)),
                    ft.Divider(color="outlineVariant"),
                    ft.ElevatedButton(content=ft.Row([ft.Icon("save", size=20, color="onPrimary"), ft.Text(t("course_form.save_btn"))], alignment=ft.MainAxisAlignment.CENTER), style=ft.ButtonStyle(bgcolor="primary", color="onPrimary"), on_click=self.save_course, height=45)
                ], spacing=15, scroll=ft.ScrollMode.AUTO)
            )
        ]

    def toggle_optional_fields(self, e):
        self.lecturer_input.visible = self.has_lecturer.value
        self.link_input.visible = self.has_link.value
        self.app_page.update()

    def handle_start_change(self, e):
        if self.start_dropdown.value:
            h, m = map(int, self.start_dropdown.value.split(':'))
            h += 1
            if h > 23: h = 23
            new_end = f"{h:02d}:{m:02d}"
            if any(opt.key == new_end for opt in self.end_dropdown.options):
                self.end_dropdown.value = new_end
                self.app_page.update()

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

    def add_meeting(self, e):
        if not self.day_dropdown.value or not self.start_dropdown.value or not self.end_dropdown.value: return
        dur_text = self.calc_duration_text(self.start_dropdown.value, self.end_dropdown.value)
        if not dur_text:
            self.app_page.overlay.append(ft.SnackBar(ft.Text(t("course_form.time_error"), color="onError"), bgcolor="error", open=True))
            self.app_page.update()
            return
        meeting = {"day_key": self.day_dropdown.value, "start": self.start_dropdown.value, "end": self.end_dropdown.value, "location": self.location_input.value, "type_key": self.type_dropdown.value, "dur_text": dur_text}
        self.weekly_meetings.append(meeting); self.update_tree_view(); self.app_page.update()

    def edit_meeting(self, meeting):
        self.day_dropdown.value = meeting["day_key"]; self.start_dropdown.value = meeting["start"]; self.end_dropdown.value = meeting["end"]; self.location_input.value = meeting["location"]; self.type_dropdown.value = meeting["type_key"]
        self.weekly_meetings.remove(meeting); self.update_tree_view(); self.app_page.update()

    def delete_meeting(self, meeting):
        self.weekly_meetings.remove(meeting); self.update_tree_view(); self.app_page.update()

    def update_tree_view(self):
        self.tree_view.controls.clear()
        if not self.weekly_meetings: return
        groups = {"meeting_types.lecture": [], "meeting_types.practice": [], "meeting_types.lab": []}
        for m in self.weekly_meetings: groups[m["type_key"]].append(m)

        c_title = self.title_input.value if self.title_input.value else t("course_form.new_course_def")
        c_code = f" ({self.code_input.value})" if self.code_input.value else ""
        tree_nodes = [ft.Row([ft.Icon("menu_book", size=20, color="primary"), ft.Text(f"{c_title}{c_code}", size=16, weight="bold", color="primary")])]
        
        for m_type_key, m_list in groups.items():
            if not m_list: continue
            plural_key = m_type_key.replace("meeting_types.", "plurals.")
            type_col = ft.Column([ft.Text(t(plural_key), weight="bold", color="onSurface")])
            for m in m_list:
                loc_text = f" | {m['location']}" if m['location'] else ""
                actions = ft.Row([
                    ft.Container(content=ft.Icon("edit", size=16, color="primary"), on_click=lambda _, meet=m: self.edit_meeting(meet), tooltip="ערוך", padding=4, ink=True, border_radius=10),
                    ft.Container(content=ft.Icon("delete", size=16, color="error"), on_click=lambda _, meet=m: self.delete_meeting(meet), tooltip="מחק", padding=4, ink=True, border_radius=10)
                ], spacing=2)
                item = ft.Row([
                    ft.Row([ft.Icon("schedule", size=14, color="onSurfaceVariant"), ft.Text(f"{t(m['day_key'])}, {m['start']} - {m['end']} | {m['dur_text']}{loc_text}", color="onSurfaceVariant", size=13)], expand=True),
                    actions
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                type_col.controls.append(item)
            tree_nodes.append(ft.Container(content=type_col, border=ft.border.only(right=ft.border.BorderSide(2, "outlineVariant")), padding=ft.padding.only(right=15), margin=ft.margin.only(right=10)))
        self.tree_view.controls.extend(tree_nodes)

    def save_course(self, e):
        if not self.title_input.value or len(self.weekly_meetings) == 0:
            self.app_page.overlay.append(ft.SnackBar(ft.Text(t("course_form.missing_info"), color="onError"), bgcolor="error", open=True))
            self.app_page.update()
            return
            
        new_course = Course(course_id=str(time.time()), title=self.title_input.value, lecturer=(self.lecturer_input.value if self.has_lecturer.value else ""), course_code=self.code_input.value, link=(self.link_input.value if self.has_link.value else ""))
        for m in self.weekly_meetings: new_course.add_weekly_meeting(self.schedule.semester_start, self.schedule.semester_end, m["day_key"], m["start"], m["end"], m["location"], m["type_key"])
        self.schedule.add_course(new_course)
        self.app_page.overlay.append(ft.SnackBar(ft.Text(t("course_form.success_msg", title=self.title_input.value)), open=True))
        self.app_page.update()
        self.change_screen("schedule")