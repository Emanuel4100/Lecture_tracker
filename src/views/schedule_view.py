import flet as ft
from datetime import datetime, timedelta
import time
from components.lecture_card import LectureCard
from components.statistics_panel import StatisticsPanel
from models.lecture import LectureSession, LectureStatus
from utils.i18n import t

class ScheduleView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True, spacing=0)
        self.app_page = page 
        self.schedule = schedule
        self.change_screen = change_screen_func

        self.is_narrow_screen = self.app_page.width < 1100
        self.is_native_mobile = self.app_page.platform in [ft.PagePlatform.IOS, ft.PagePlatform.ANDROID]
        
        self.tabs = self.get_tabs()
        self.selected_tab = self.tabs[0]
        self.current_week_offset = 0
        self.selected_lecture_filter = t("schedule.tab_missing")
        self.current_sort_method = "date" # Default sort method
        
        self.app_page.on_resize = self.handle_resize

        self.tabs_row = ft.Row(scroll=ft.ScrollMode.AUTO, alignment="center")
        
        self.bottom_nav_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND)
        self.bottom_nav = ft.Container(
            content=self.bottom_nav_row, visible=self.is_native_mobile, bgcolor="surface",
            border=ft.border.only(top=ft.border.BorderSide(1, "outlineVariant")), padding=ft.padding.only(top=10, bottom=20) 
        )

        self.content_area = ft.Container(expand=True)

        self.build_tabs()
        self.update_content()

        header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Image(src="icons/settings.svg", width=24, height=24, color="onPrimary"), tooltip=t("schedule.settings"), padding=10, on_click=lambda _: self.change_screen("settings")),
                ft.Text(t("schedule.app_title"), size=22, weight="bold", color="onPrimary"),
                ft.Container(width=48)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="primary", padding=15, border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15), shadow=ft.BoxShadow(blur_radius=5, color="shadow")
        )

        add_btn = ft.FloatingActionButton(content=ft.Image(src="icons/add.svg", width=24, height=24, color="onPrimaryContainer"), bgcolor="primaryContainer", shape=ft.RoundedRectangleBorder(radius=16), on_click=self.open_add_menu)
        
        top_controls = [header]
        if not self.is_native_mobile:
            top_controls.append(self.tabs_row)
            
        self.controls = [
            ft.Column(top_controls),
            ft.Stack([self.content_area, ft.Container(content=add_btn, bottom=20, left=20)], expand=True),
            self.bottom_nav
        ]

    def get_tabs(self):
        if self.is_narrow_screen: return [t("schedule.tab_weekly"), t("schedule.tab_lectures"), t("schedule.tab_stats")]
        else: return [t("schedule.tab_weekly"), t("schedule.tab_lectures")]

    def handle_resize(self, e):
        new_is_narrow = self.app_page.width < 1100
        if new_is_narrow != self.is_narrow_screen:
            self.is_narrow_screen = new_is_narrow
            self.tabs = self.get_tabs()
            if self.selected_tab not in self.tabs: self.selected_tab = self.tabs[0]
            self.build_tabs(); self.update_content(); self.update()

    def open_add_menu(self, e):
        def close_and_go(screen_name):
            bs.open = False; self.app_page.update(); self.change_screen(screen_name)
            
        def close_and_open_oneoff():
            bs.open = False; self.app_page.update(); self.open_oneoff_event_dialog()

        # Contextual FAB logic
        if self.selected_tab == t("schedule.tab_lectures"):
            options_content = ft.Column([
                ft.Text("Add Task / One-off Event", size=18, weight="bold", color="onSurface"),
                ft.Divider(color="outlineVariant"),
                ft.ListTile(leading=ft.Icon(ft.Icons.VIDEO_CAMERA_FRONT, color="primary"), title=ft.Text("Add Recording Task", color="onSurface"), on_click=lambda _: close_and_open_oneoff()),
                ft.ListTile(leading=ft.Icon(ft.Icons.EVENT, color="tertiary"), title=ft.Text("Add Custom Event", color="onSurface"), on_click=lambda _: close_and_open_oneoff()),
            ], tight=True)
        else:
            options_content = ft.Column([
                ft.Text(t("schedule_menu.add_options"), size=18, weight="bold", color="onSurface"),
                ft.Divider(color="outlineVariant"),
                ft.ListTile(leading=ft.Image(src="icons/menu_book.svg", width=24, height=24, color="primary"), title=ft.Text(t("schedule_menu.add_course"), color="onSurface"), on_click=lambda _: close_and_go("add")),
                ft.ListTile(leading=ft.Image(src="icons/schedule.svg", width=24, height=24, color="tertiary"), title=ft.Text(t("schedule_menu.add_meeting"), color="onSurface"), on_click=lambda _: close_and_go("add_meeting"))
            ], tight=True)

        bs = ft.BottomSheet(ft.Container(padding=20, bgcolor="surface", content=options_content))
        self.app_page.overlay.append(bs); bs.open = True; self.app_page.update()

    def open_oneoff_event_dialog(self):
        course_options = [ft.dropdown.Option(key=c.course_id, text=c.title) for c in self.schedule.courses]
        course_dropdown = ft.Dropdown(label="Select Course", options=course_options, width=280)
        title_input = ft.TextField(label="Topic / Title", width=280)
        duration_input = ft.TextField(label="Duration (mins)", keyboard_type=ft.KeyboardType.NUMBER, width=120)
        
        type_dropdown = ft.Dropdown(label="Type", width=150, options=[
            ft.dropdown.Option("meeting_types.lecture", t("meeting_types.lecture")),
            ft.dropdown.Option("meeting_types.practice", t("meeting_types.practice")),
            ft.dropdown.Option("meeting_types.lab", t("meeting_types.lab")),
            ft.dropdown.Option("meeting_types.recording", "הקלטה/Recording"),
            ft.dropdown.Option("meeting_types.other", "אחר/Other")
        ], value="meeting_types.other")
        
        def save_oneoff(e):
            if not course_dropdown.value or not title_input.value:
                return
            course = next((c for c in self.schedule.courses if c.course_id == course_dropdown.value), None)
            if course:
                session_id = str(time.time())
                dur = int(duration_input.value) if duration_input.value.isdigit() else 60
                
                lec = LectureSession(
                    session_id=session_id,
                    title=f"{course.title} - {title_input.value}",
                    lecturer=course.lecturer,
                    date_obj=datetime.now().date(),
                    duration_mins=dur,
                    is_one_off=True,
                    meeting_type=type_dropdown.value,
                    status=LectureStatus.NEEDS_WATCHING
                )
                lec.course_color = course.color
                course.lectures.append(lec)
                self.schedule.save_to_file()
                self.refresh_ui()
                dlg.open = False
                self.app_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Add Custom Task"),
            content=ft.Column([course_dropdown, title_input, ft.Row([duration_input, type_dropdown])], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(dlg, 'open', False) or self.app_page.update()),
                ft.ElevatedButton("Save", on_click=save_oneoff, bgcolor="primary", color="onPrimary")
            ]
        )
        self.app_page.overlay.append(dlg)
        dlg.open = True
        self.app_page.update()

    def build_tabs(self):
        self.tabs_row.controls.clear()
        for tab in self.tabs:
            is_selected = (tab == self.selected_tab)
            btn = ft.TextButton(
                content=ft.Text(tab, color="onSecondaryContainer" if is_selected else "onSurfaceVariant", weight="bold" if is_selected else "normal"),
                style=ft.ButtonStyle(bgcolor="secondaryContainer" if is_selected else "transparent", shape=ft.RoundedRectangleBorder(radius=20)),
                on_click=self.create_tab_click_handler(tab)
            )
            self.tabs_row.controls.append(btn)

        self.bottom_nav_row.controls.clear()
        nav_items = [("calendar_month", t("schedule.tab_weekly")), ("menu_book", t("schedule.tab_lectures")), ("pie_chart", t("schedule.tab_stats"))]
        for icon_name, tab_name in nav_items:
            is_selected = (self.selected_tab == tab_name)
            color = "primary" if is_selected else "onSurfaceVariant"
            nav_btn = ft.Container(
                content=ft.Column([
                    ft.Image(src=f"icons/{icon_name}.svg", width=24, height=24, color=color),
                    ft.Text(tab_name, size=11, color=color, weight="bold" if is_selected else "normal")
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True, ink=True, padding=ft.padding.symmetric(vertical=8), border_radius=10,
                on_click=self.create_tab_click_handler(tab_name)
            )
            self.bottom_nav_row.controls.append(nav_btn)

    def create_tab_click_handler(self, tab):
        def on_click(e):
            self.selected_tab = tab; self.current_week_offset = 0; self.build_tabs(); self.update_content(); self.update()
        return on_click
    
    def refresh_ui(self):
        self.schedule.save_to_file(); self.update_content(); self.update()

    def change_week(self, delta):
        self.current_week_offset += delta; self.update_content(); self.update()

    def time_to_minutes(self, t_str):
        h, m = map(int, t_str.split(':'))
        return h * 60 + m

    def build_weekly_grid(self):
        target_date = datetime.now().date() + timedelta(days=7 * self.current_week_offset)
        lectures = self.schedule.get_weekly_lectures(target_date)
        day_keys = ["days.sunday", "days.monday", "days.tuesday", "days.wednesday", "days.thursday", "days.friday", "days.saturday"]
        days_to_show = 7 if self.schedule.show_weekend else 5
        idx = (target_date.weekday() + 1) % 7
        sun = target_date - timedelta(days=idx)

        prev_icon = "arrow_forward.svg" if self.schedule.language == "he" else "arrow_back.svg"
        next_icon = "arrow_back.svg" if self.schedule.language == "he" else "arrow_forward.svg"
        
        nav_row = ft.Row([
            ft.TextButton(content=ft.Row([ft.Image(src=f"icons/{prev_icon}", width=18, height=18, color="primary"), ft.Text(t("common.prev"), color="primary")]), on_click=lambda _: self.change_week(-1)),
            ft.Text(t("schedule.week_of", date=sun.strftime('%d/%m')), weight="bold", size=14 if self.is_narrow_screen else 15, color="primary"),
            ft.TextButton(content=ft.Row([ft.Text(t("common.next"), color="primary"), ft.Image(src=f"icons/{next_icon}", width=18, height=18, color="primary")]), on_click=lambda _: self.change_week(1)),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        SCALE = 1.2
        START_HOUR = 8
        END_HOUR = 22
        TOTAL_HEIGHT = (END_HOUR - START_HOUR) * 60 * SCALE

        time_column = ft.Column(spacing=0)
        time_column.controls.append(ft.Container(height=65)) 
        for h in range(START_HOUR, END_HOUR + 1):
            time_column.controls.append(ft.Container(content=ft.Text(f"{h:02d}:00", color="onSurfaceVariant", size=10 if self.is_narrow_screen else 12, weight="w500"), height=60 * SCALE, alignment=ft.Alignment(0, -1)))

        he_short_days = {"ראשון": "א'", "שני": "ב'", "שלישי": "ג'", "רביעי": "ד'", "חמישי": "ה'", "שישי": "ו'", "שבת": "ש'"}

        day_columns = []
        for i in range(days_to_show):
            current_day_date = sun + timedelta(days=i)
            d_name_full = t(day_keys[i])
            d_name = he_short_days.get(d_name_full, d_name_full) if (self.is_narrow_screen and self.schedule.language == "he") else d_name_full[:3] if self.is_narrow_screen else d_name_full

            header_elements = [ft.Text(f"{d_name}\n{current_day_date.strftime('%d/%m')}", weight="bold", size=12 if self.is_narrow_screen else 14, color="onSecondaryContainer", text_align="center")]
            if self.schedule.semester_end and current_day_date == self.schedule.semester_end:
                header_elements.append(ft.Container(content=ft.Row([ft.Image(src="icons/flag.svg", width=12, height=12, color="onError"), ft.Text(t("schedule.end_of_sem"), color="onError", weight="bold", size=10)], spacing=2), bgcolor="error", padding=4, border_radius=5))
            
            col_header = ft.Container(content=ft.Column(header_elements, alignment="center", horizontal_alignment="center", spacing=2), alignment=ft.Alignment(0, 0), padding=5, bgcolor="secondaryContainer", border_radius=8, height=65)
            
            day_stack = ft.Stack(height=TOTAL_HEIGHT)
            for h in range(START_HOUR, END_HOUR + 1): day_stack.controls.append(ft.Container(top=(h - START_HOUR) * 60 * SCALE, height=1, bgcolor="outlineVariant", left=0, right=0))

            day_lecs = [l for l in lectures if l.date_obj == current_day_date]
            for lec in day_lecs:
                lec_start_m, lec_end_m = self.time_to_minutes(lec.start_time), self.time_to_minutes(lec.end_time)
                is_overlapping = any(lec.session_id != other.session_id and max(lec_start_m, self.time_to_minutes(other.start_time)) < min(lec_end_m, self.time_to_minutes(other.end_time)) for other in day_lecs)
                
                top_pos, height = max(0, (lec_start_m - START_HOUR * 60) * SCALE), max(30, (lec_end_m - lec_start_m) * SCALE)
                card = LectureCard(lec, self.refresh_ui, is_mobile=self.is_narrow_screen, show_date=False)
                
                if is_overlapping:
                    card.border = ft.border.all(2, "error")
                    if not self.is_narrow_screen: card.content.controls.insert(0, ft.Row([ft.Image(src="icons/warning_amber.svg", width=12, height=12, color="error"), ft.Text(t("schedule.overlap"), color="error", weight="bold", size=10)]))
                day_stack.controls.append(ft.Container(top=top_pos, height=height, left=0, right=0, content=card, opacity=0.9 if is_overlapping else 1.0))

            day_col = ft.Column([col_header, ft.Container(content=day_stack, expand=True)], spacing=10)
            day_columns.append(ft.Container(content=day_col, expand=True, padding=2))

        grid_row = ft.Row(controls=day_columns + [ft.Container(content=time_column, width=30 if self.is_narrow_screen else 40)], vertical_alignment="start")
        return ft.Column([nav_row, ft.Container(content=ft.Column([grid_row], scroll=ft.ScrollMode.AUTO, expand=True), expand=True)], expand=True)

    def change_lecture_filter(self, filter_name):
        self.selected_lecture_filter = filter_name; self.update_content(); self.update()
        
    def change_sort_method(self, e):
        self.current_sort_method = e.control.value
        self.update_content()
        self.update()

    def build_lectures_tab(self):
        filters = [t("schedule.tab_missing"), t("schedule.tab_future"), t("schedule.tab_past")]
        filter_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        
        for f_name in filters:
            is_sel = (f_name == self.selected_lecture_filter)
            btn = ft.Container(
                content=ft.Text(f_name, color="onSecondaryContainer" if is_sel else "onSurfaceVariant", weight="bold"), 
                bgcolor="secondaryContainer" if is_sel else "surfaceVariant",
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                border_radius=20,
                on_click=lambda e, fn=f_name: self.change_lecture_filter(fn), ink=True
            )
            filter_row.controls.append(btn)

        # Sorting Dropdown
        sort_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("date", "מיון: תאריך"),
                ft.dropdown.Option("duration", "מיון: אורך"),
                ft.dropdown.Option("type", "מיון: סוג")
            ],
            value=self.current_sort_method, width=150, dense=True,
            on_change=self.change_sort_method
        )
        
        top_bar = ft.Row([filter_row, sort_dropdown], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        list_view = ft.ListView(expand=True, padding=20, spacing=10)
        
        if self.selected_lecture_filter == t("schedule.tab_missing"): lectures = self.schedule.get_pending_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_past"): lectures = self.schedule.get_past_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_future"): lectures = self.schedule.get_future_lectures()
            
        # Apply Sorting
        if self.current_sort_method == "duration":
            lectures.sort(key=lambda x: x.duration_mins or 0, reverse=True)
        elif self.current_sort_method == "type":
            lectures.sort(key=lambda x: str(x.meeting_type))
        else:
            lectures.sort(key=lambda x: (x.date_obj, x.start_time))

        if not lectures:
            empty_state = ft.Column([
                ft.Image(src="icons/event_busy.svg", width=60, height=60, color="onSurfaceVariant"), 
                ft.Text(t("schedule.no_lectures"), size=18, weight="w500", color="onSurfaceVariant")
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            list_view.controls.append(ft.Container(content=empty_state, alignment=ft.Alignment(0, 0), padding=ft.padding.only(top=100)))
        else:
            for lec in lectures: list_view.controls.append(LectureCard(lec, self.refresh_ui, is_mobile=False, show_date=True))

        return ft.Column([ft.Container(content=top_bar, padding=ft.padding.only(top=10, bottom=5, left=10, right=10)), list_view], expand=True)

    def update_content(self):
        main_view = None
        if self.selected_tab == t("schedule.tab_weekly"): main_view = self.build_weekly_grid()
        elif self.selected_tab == t("schedule.tab_stats"): main_view = StatisticsPanel(self.schedule)
        elif self.selected_tab == t("schedule.tab_lectures"): main_view = self.build_lectures_tab()

        if not self.is_narrow_screen and self.selected_tab == t("schedule.tab_lectures"):
            border_side = ft.border.only(right=ft.border.BorderSide(width=1, color="outlineVariant")) if self.schedule.language == "he" else ft.border.only(left=ft.border.BorderSide(width=1, color="outlineVariant"))
            side_panel = ft.Container(content=StatisticsPanel(self.schedule), width=350, border=border_side, padding=10)
            self.content_area.content = ft.Row([ft.Container(content=main_view, expand=True), side_panel], expand=True)
        else:
            self.content_area.content = main_view