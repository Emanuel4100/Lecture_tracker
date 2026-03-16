import flet as ft
from datetime import datetime, timedelta
from components.lecture_card import LectureCard
from utils.i18n import t

class WeeklyGrid(ft.Column):
    def __init__(self, schedule, refresh_callback, is_narrow_screen):
        super().__init__(expand=True)
        self.schedule = schedule
        self.refresh_callback = refresh_callback
        self.is_narrow_screen = is_narrow_screen
        self.current_week_offset = 0
        self.update_grid()

    def set_narrow_screen(self, is_narrow):
        if self.is_narrow_screen != is_narrow:
            self.is_narrow_screen = is_narrow
            self.update_grid()

    def change_week(self, delta):
        self.current_week_offset += delta
        self.update_grid()
        self.update()

    def time_to_minutes(self, t_str):
        h, m = map(int, t_str.split(':'))
        return h * 60 + m

    def update_grid(self):
        target_date = datetime.now().date() + timedelta(days=7 * self.current_week_offset)
        lectures = self.schedule.get_weekly_lectures(target_date)
        day_keys = ["days.sunday", "days.monday", "days.tuesday", "days.wednesday", "days.thursday", "days.friday", "days.saturday"]
        days_to_show = 7 if self.schedule.show_weekend else 5
        idx = (target_date.weekday() + 1) % 7
        sun = target_date - timedelta(days=idx)

        prev_icon = "arrow_forward" if self.schedule.language == "he" else "arrow_back"
        next_icon = "arrow_back" if self.schedule.language == "he" else "arrow_forward"
        
        nav_row = ft.Row([
            ft.TextButton(content=ft.Row([ft.Icon(prev_icon, size=18, color="primary"), ft.Text(t("common.prev"), color="primary")]), on_click=lambda _: self.change_week(-1)),
            ft.Text(t("schedule.week_of", date=sun.strftime('%d/%m')), weight="bold", size=14 if self.is_narrow_screen else 15, color="primary"),
            ft.TextButton(content=ft.Row([ft.Text(t("common.next"), color="primary"), ft.Icon(next_icon, size=18, color="primary")]), on_click=lambda _: self.change_week(1)),
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
                header_elements.append(ft.Container(content=ft.Row([ft.Icon("flag", size=12, color="onError"), ft.Text(t("schedule.end_of_sem"), color="onError", weight="bold", size=10)], spacing=2), bgcolor="error", padding=4, border_radius=5))
            
            col_header = ft.Container(content=ft.Column(header_elements, alignment="center", horizontal_alignment="center", spacing=2), alignment=ft.Alignment(0, 0), padding=5, bgcolor="secondaryContainer", border_radius=8, height=65)
            
            day_stack = ft.Stack(height=TOTAL_HEIGHT)
            for h in range(START_HOUR, END_HOUR + 1): day_stack.controls.append(ft.Container(top=(h - START_HOUR) * 60 * SCALE, height=1, bgcolor="outlineVariant", left=0, right=0))

            day_lecs = [l for l in lectures if l.date_obj == current_day_date]
            for lec in day_lecs:
                lec_start_m, lec_end_m = self.time_to_minutes(lec.start_time), self.time_to_minutes(lec.end_time)
                is_overlapping = any(lec.session_id != other.session_id and max(lec_start_m, self.time_to_minutes(other.start_time)) < min(lec_end_m, self.time_to_minutes(other.end_time)) for other in day_lecs)
                
                top_pos, height = max(0, (lec_start_m - START_HOUR * 60) * SCALE), max(30, (lec_end_m - lec_start_m) * SCALE)
                card = LectureCard(lec, self.refresh_callback, is_mobile=self.is_narrow_screen, show_date=False)
                
                if is_overlapping:
                    card.border = ft.border.all(2, "error")
                    if not self.is_narrow_screen: card.content.controls.insert(0, ft.Row([ft.Icon("warning_amber", size=12, color="error"), ft.Text(t("schedule.overlap"), color="error", weight="bold", size=10)]))
                day_stack.controls.append(ft.Container(top=top_pos, height=height, left=0, right=0, content=card, opacity=0.9 if is_overlapping else 1.0))

            day_col = ft.Column([col_header, ft.Container(content=day_stack, expand=True)], spacing=10)
            day_columns.append(ft.Container(content=day_col, expand=True, padding=2))

        grid_row = ft.Row(controls=day_columns + [ft.Container(content=time_column, width=30 if self.is_narrow_screen else 40)], vertical_alignment="start")
        self.controls = [nav_row, ft.Container(content=ft.Column([grid_row], scroll=ft.ScrollMode.AUTO, expand=True), expand=True)]