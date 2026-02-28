import flet as ft
from datetime import datetime, timedelta
from components.lecture_card import LectureCard
from components.statistics_panel import StatisticsPanel

class ScheduleView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page 
        self.schedule = schedule
        self.change_screen = change_screen_func

        self.tabs = ["לוח שבועי", "השלמות", "הרצאות שעברו", "הרצאות עתידיות", "סטטיסטיקה"]
        self.selected_tab = self.tabs[0]
        self.current_week_offset = 0

        self.tabs_row = ft.Row(scroll=ft.ScrollMode.AUTO, alignment="center")
        self.content_area = ft.Container(expand=True)

        self.build_tabs()
        self.update_content()

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Text("⚙️ הגדרות", color="white", weight="bold"), on_click=lambda _: self.change_screen("settings")),
                ft.Text("מעקב הרצאות", size=24, weight="bold", color="white"),
                ft.Container(width=80) 
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#1976D2", padding=15, border_radius=10
        )

        add_btn = ft.FloatingActionButton(
            content=ft.Text("➕", size=24, color="white"),
            bgcolor="#F57C00", shape=ft.RoundedRectangleBorder(radius=100),
            on_click=lambda _: self.change_screen("add")
        )

        self.controls = [header, self.tabs_row, self.content_area, ft.Row([add_btn], alignment="start")]

    def build_tabs(self):
        self.tabs_row.controls.clear()
        for tab in self.tabs:
            is_selected = (tab == self.selected_tab)
            btn = ft.TextButton(
                content=ft.Text(tab, color="#1976D2" if is_selected else "grey", weight="bold" if is_selected else "normal"),
                style=ft.ButtonStyle(bgcolor="#E3F2FD" if is_selected else "transparent", shape=ft.RoundedRectangleBorder(radius=8)),
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
        
        day_names = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
        days_to_show = 7 if self.schedule.show_weekend else 5
        
        idx = (target_date.weekday() + 1) % 7
        sun = target_date - timedelta(days=idx)

        nav_row = ft.Row([
            ft.TextButton("➡️ קודם", on_click=lambda _: self.change_week(-1)),
            ft.Text(f"שבוע מתאריך: {sun.strftime('%d/%m/%Y')}", weight="bold", size=16, color="#1976D2"),
            ft.TextButton("הבא ⬅️", on_click=lambda _: self.change_week(1)),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        SCALE = 1.2  # גובה של 72 פיקסלים לכל שעה
        START_HOUR = 8
        END_HOUR = 22
        TOTAL_HEIGHT = (END_HOUR - START_HOUR) * 60 * SCALE

        # עמודת השעות 
        time_column = ft.Column(spacing=0)
        time_column.controls.append(ft.Container(height=65)) # מרווח לכותרות הימים
        for h in range(START_HOUR, END_HOUR + 1):
            time_column.controls.append(
                ft.Container(
                    content=ft.Text(f"{h:02d}:00", color="grey", size=12, weight="bold"),
                    height=60 * SCALE,
                    alignment=ft.Alignment(0, -1)
                )
            )

        day_columns = []
        for i in range(days_to_show):
            current_day_date = sun + timedelta(days=i)
            header_elements = [ft.Text(f"{day_names[i]}\n{current_day_date.strftime('%d/%m')}", weight="bold", size=14, color="#1976D2", text_align="center")]
            
            if self.schedule.semester_end and current_day_date == self.schedule.semester_end:
                header_elements.append(ft.Container(content=ft.Text("🏁 סיום סמסטר", color="white", weight="bold", size=10), bgcolor="red", padding=3, border_radius=5))
            
            col_header = ft.Container(content=ft.Column(header_elements, alignment="center", horizontal_alignment="center", spacing=2), alignment=ft.Alignment(0, 0), padding=5, bgcolor="#E3F2FD", border_radius=8, height=65)
            
            day_stack = ft.Stack(height=TOTAL_HEIGHT)
            
            # קווי רשת לשעות
            for h in range(START_HOUR, END_HOUR + 1):
                day_stack.controls.append(
                    ft.Container(top=(h - START_HOUR) * 60 * SCALE, height=1, bgcolor="#E0E0E0", left=0, right=0)
                )

            day_lecs = [l for l in lectures if l.date_obj == current_day_date]
            
            for lec in day_lecs:
                lec_start_m = self.time_to_minutes(lec.start_time)
                lec_end_m = self.time_to_minutes(lec.end_time)
                
                is_overlapping = False
                for other in day_lecs:
                    if lec.session_id != other.session_id:
                        other_start_m = self.time_to_minutes(other.start_time)
                        other_end_m = self.time_to_minutes(other.end_time)
                        if max(lec_start_m, other_start_m) < min(lec_end_m, other_end_m):
                            is_overlapping = True
                            break
                
                top_pos = max(0, (lec_start_m - START_HOUR * 60) * SCALE)
                height = max(30, (lec_end_m - lec_start_m) * SCALE)
                
                card = LectureCard(lec, self.refresh_ui)
                if is_overlapping:
                    card.border = ft.border.all(2, "red")
                    card.content.controls.insert(0, ft.Text("⚠️ חפיפה!", color="red", weight="bold", size=10))
                
                day_stack.controls.append(
                    ft.Container(top=top_pos, height=height, left=0, right=0, content=card, opacity=0.85 if is_overlapping else 1.0)
                )

            day_col = ft.Column([col_header, ft.Container(content=day_stack, expand=True)], spacing=10)
            day_columns.append(ft.Container(content=day_col, expand=True, padding=2))

        # מניחים את עמודת הזמן בסוף הרשימה (מימין לשמאל זה יופיע בצד שמאל)
        grid_row = ft.Row(controls=day_columns + [ft.Container(content=time_column, width=40)], vertical_alignment="start")
        
        # עטיפת השורה ב-Column נגלל (זה התיקון!)
        scrollable_grid = ft.Column([grid_row], scroll=ft.ScrollMode.AUTO, expand=True)
        
        return ft.Column([nav_row, ft.Container(content=scrollable_grid, expand=True)], expand=True)

    def update_content(self):
        if self.selected_tab == "לוח שבועי":
            self.content_area.content = self.build_weekly_grid()
            return
        elif self.selected_tab == "סטטיסטיקה":
            self.content_area.content = StatisticsPanel(self.schedule)
            return

        list_view = ft.ListView(expand=True, padding=20)
        
        if self.selected_tab == "השלמות":
            lectures = self.schedule.get_pending_lectures()
        elif self.selected_tab == "הרצאות שעברו":
            lectures = self.schedule.get_past_lectures()
        elif self.selected_tab == "הרצאות עתידיות":
            lectures = self.schedule.get_future_lectures()
        
        if not lectures:
            list_view.controls.append(ft.Container(content=ft.Text("אין הרצאות 🏖️", size=16, color="grey"), alignment=ft.Alignment(0, 0), padding=50))
        else:
            for lec in lectures:
                list_view.controls.append(LectureCard(lec, self.refresh_ui))
        
        self.content_area.content = list_view