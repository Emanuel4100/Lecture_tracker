import flet as ft
from datetime import datetime, timedelta
from components.lecture_card import LectureCard
from components.statistics_panel import StatisticsPanel
from utils.i18n import t

class ScheduleView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page 
        self.schedule = schedule
        self.change_screen = change_screen_func

        # צמצמנו ל-3 לשוניות ראשיות בלבד!
        self.tabs = [t("schedule.tab_weekly"), t("schedule.tab_lectures"), t("schedule.tab_stats")]
        self.selected_tab = self.tabs[0]
        
        # משתנה חדש לשמירת הסינון הפנימי בתוך לשונית הרצאות
        self.selected_lecture_filter = t("schedule.tab_missing")
        
        self.current_week_offset = 0
        
        self.is_mobile = self.app_page.width < 1100
        self.app_page.on_resize = self.handle_resize

        self.tabs_row = ft.Row(scroll=ft.ScrollMode.AUTO, alignment="center")
        self.content_area = ft.Container(expand=True)

        self.build_tabs()
        self.update_content()

        header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Image(src="icons/settings.svg", width=24, height=24, color="white"), 
                    tooltip=t("schedule.settings"), 
                    padding=10, 
                    on_click=lambda _: self.change_screen("settings")
                ),
                ft.Text(t("schedule.app_title"), size=22, weight="bold", color="white"),
                ft.Container(width=48)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1976D2", padding=15, border_radius=ft.border_radius.only(bottom_left=15, bottom_right=15), shadow=ft.BoxShadow(blur_radius=10, color="black26")
        )

        add_btn = ft.FloatingActionButton(content=ft.Image(src="icons/add.svg", width=24, height=24, color="white"), bgcolor="#F57C00", shape=ft.RoundedRectangleBorder(radius=16), on_click=self.open_add_menu)
        self.controls = [header, self.tabs_row, self.content_area, ft.Row([add_btn], alignment=ft.MainAxisAlignment.START)]

    def open_add_menu(self, e):
        def close_and_go(screen_name):
            bs.open = False
            self.app_page.update()
            self.change_screen(screen_name)

        bs = ft.BottomSheet(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text(t("schedule_menu.add_options"), size=18, weight="bold"),
                    ft.Divider(),
                    ft.ListTile(
                        leading=ft.Image(src="icons/menu_book.svg", width=24, height=24, color="#1976D2"),
                        title=ft.Text(t("schedule_menu.add_course")),
                        on_click=lambda _: close_and_go("add")
                    ),
                    ft.ListTile(
                        leading=ft.Image(src="icons/schedule.svg", width=24, height=24, color="#F57C00"),
                        title=ft.Text(t("schedule_menu.add_meeting")),
                        on_click=lambda _: close_and_go("add_meeting")
                    )
                ], tight=True)
            )
        )
        self.app_page.overlay.append(bs)
        bs.open = True
        self.app_page.update()

    def handle_resize(self, e):
        new_is_mobile = self.app_page.width < 1100
        if new_is_mobile != self.is_mobile:
            self.is_mobile = new_is_mobile
            self.update_content()
            self.update()

    def build_tabs(self):
        self.tabs_row.controls.clear()
        for tab in self.tabs:
            is_selected = (tab == self.selected_tab)
            btn = ft.TextButton(
                content=ft.Text(tab, color="#1976D2" if is_selected else "grey600", weight="bold" if is_selected else "normal"),
                style=ft.ButtonStyle(bgcolor="#E3F2FD" if is_selected else "transparent", shape=ft.RoundedRectangleBorder(radius=20)),
                on_click=self.create_tab_click_handler(tab)
            )
            self.tabs_row.controls.append(btn)

    def create_tab_click_handler(self, tab):
        def on_click(e):
            self.selected_tab = tab
            self.current_week_offset = 0 
            self.build_tabs()
            self.update_content()
            self.update()
        return on_click
    
    def refresh_ui(self):
        self.schedule.save_to_file()
        self.update_content()
        self.update()

    def change_week(self, delta):
        self.current_week_offset += delta
        self.update_content()
        self.update()

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
            ft.TextButton(content=ft.Row([ft.Image(src=f"icons/{prev_icon}", width=18, height=18, color="#1976D2"), ft.Text(t("common.prev"), color="#1976D2")]), on_click=lambda _: self.change_week(-1)),
            ft.Text(t("schedule.week_of", date=sun.strftime('%d/%m')), weight="bold", size=14 if self.is_mobile else 15, color="#1976D2"),
            ft.TextButton(content=ft.Row([ft.Text(t("common.next"), color="#1976D2"), ft.Image(src=f"icons/{next_icon}", width=18, height=18, color="#1976D2")]), on_click=lambda _: self.change_week(1)),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        SCALE = 1.2
        START_HOUR = 8
        END_HOUR = 22
        TOTAL_HEIGHT = (END_HOUR - START_HOUR) * 60 * SCALE

        time_column = ft.Column(spacing=0)
        time_column.controls.append(ft.Container(height=65)) 
        for h in range(START_HOUR, END_HOUR + 1):
            time_column.controls.append(ft.Container(content=ft.Text(f"{h:02d}:00", color="grey", size=10 if self.is_mobile else 12, weight="w500"), height=60 * SCALE, alignment=ft.Alignment(0, -1)))

        he_short_days = {"ראשון": "א'", "שני": "ב'", "שלישי": "ג'", "רביעי": "ד'", "חמישי": "ה'", "שישי": "ו'", "שבת": "ש'"}

        day_columns = []
        for i in range(days_to_show):
            current_day_date = sun + timedelta(days=i)
            
            d_name_full = t(day_keys[i])
            if self.is_mobile:
                if self.schedule.language == "he": d_name = he_short_days.get(d_name_full, d_name_full)
                else: d_name = d_name_full[:3] 
            else:
                d_name = d_name_full

            header_elements = [ft.Text(f"{d_name}\n{current_day_date.strftime('%d/%m')}", weight="bold", size=12 if self.is_mobile else 14, color="#1976D2", text_align="center")]
            
            if self.schedule.semester_end and current_day_date == self.schedule.semester_end:
                header_elements.append(ft.Container(content=ft.Row([ft.Image(src="icons/flag.svg", width=12, height=12, color="white"), ft.Text(t("schedule.end_of_sem"), color="white", weight="bold", size=10)], spacing=2), bgcolor="red", padding=4, border_radius=5))
            
            col_header = ft.Container(content=ft.Column(header_elements, alignment="center", horizontal_alignment="center", spacing=2), alignment=ft.Alignment(0, 0), padding=5, bgcolor="#E3F2FD", border_radius=8, height=65)
            
            day_stack = ft.Stack(height=TOTAL_HEIGHT)
            for h in range(START_HOUR, END_HOUR + 1):
                day_stack.controls.append(ft.Container(top=(h - START_HOUR) * 60 * SCALE, height=1, bgcolor="#E0E0E0", left=0, right=0))

            day_lecs = [l for l in lectures if l.date_obj == current_day_date]
            
            for lec in day_lecs:
                lec_start_m = self.time_to_minutes(lec.start_time)
                lec_end_m = self.time_to_minutes(lec.end_time)
                is_overlapping = False
                for other in day_lecs:
                    if lec.session_id != other.session_id and max(lec_start_m, self.time_to_minutes(other.start_time)) < min(lec_end_m, self.time_to_minutes(other.end_time)):
                        is_overlapping = True
                        break
                
                top_pos = max(0, (lec_start_m - START_HOUR * 60) * SCALE)
                height = max(30, (lec_end_m - lec_start_m) * SCALE)
                
                card = LectureCard(lec, self.refresh_ui, is_mobile=self.is_mobile, show_date=False)
                
                if is_overlapping:
                    card.border = ft.border.all(2, "red")
                    if not self.is_mobile:
                        card.content.controls.insert(0, ft.Row([ft.Image(src="icons/warning_amber.svg", width=12, height=12, color="red"), ft.Text(t("schedule.overlap"), color="red", weight="bold", size=10)]))
                day_stack.controls.append(ft.Container(top=top_pos, height=height, left=0, right=0, content=card, opacity=0.9 if is_overlapping else 1.0))

            day_col = ft.Column([col_header, ft.Container(content=day_stack, expand=True)], spacing=10)
            day_columns.append(ft.Container(content=day_col, expand=True, padding=2))

        grid_row = ft.Row(controls=day_columns + [ft.Container(content=time_column, width=30 if self.is_mobile else 40)], vertical_alignment="start")
        scrollable_grid = ft.Column([grid_row], scroll=ft.ScrollMode.AUTO, expand=True)
        return ft.Column([nav_row, ft.Container(content=scrollable_grid, expand=True)], expand=True)

    def change_lecture_filter(self, filter_name):
        self.selected_lecture_filter = filter_name
        self.update_content()
        self.update()

    def build_lectures_tab(self):
        # יצירת שורת כפתורי סינון פנימיים (השלמות, עתידיות, שעברו)
        filters = [t("schedule.tab_missing"), t("schedule.tab_future"), t("schedule.tab_past")]
        
        filter_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        for f_name in filters:
            is_sel = (f_name == self.selected_lecture_filter)
            btn = ft.ElevatedButton(
                content=ft.Text(f_name), # התיקון נמצא כאן! במקום text= השתמשנו ב-content
                bgcolor="#1976D2" if is_sel else "#E3F2FD",
                color="white" if is_sel else "#1976D2",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                on_click=lambda e, fn=f_name: self.change_lecture_filter(fn)
            )
            filter_row.controls.append(btn)

        list_view = ft.ListView(expand=True, padding=20, spacing=10)
        
        # שאיבת ההרצאות לפי הסינון שנבחר
        if self.selected_lecture_filter == t("schedule.tab_missing"):
            lectures = self.schedule.get_pending_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_past"):
            lectures = self.schedule.get_past_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_future"):
            lectures = self.schedule.get_future_lectures()
            
        if not lectures:
            empty_state = ft.Column([
                ft.Image(src="icons/event_busy.svg", width=60, height=60, color="grey400"), 
                ft.Text(t("schedule.no_lectures"), size=18, weight="w500", color="grey600")
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            list_view.controls.append(ft.Container(content=empty_state, alignment=ft.Alignment(0, 0), padding=ft.padding.only(top=100)))
        else:
            for lec in lectures:
                list_view.controls.append(LectureCard(lec, self.refresh_ui, is_mobile=False, show_date=True))

        return ft.Column([
            ft.Container(content=filter_row, padding=ft.padding.only(top=10, bottom=5)),
            list_view
        ], expand=True)

    def update_content(self):
        if self.selected_tab == t("schedule.tab_weekly"):
            self.content_area.content = self.build_weekly_grid()
            return
        elif self.selected_tab == t("schedule.tab_stats"):
            self.content_area.content = StatisticsPanel(self.schedule)
            return
        elif self.selected_tab == t("schedule.tab_lectures"):
            # שימוש בבנאי החדש שיצרנו ללשונית המאוחדת!
            self.content_area.content = self.build_lectures_tab()
            return