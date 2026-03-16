import flet as ft
from datetime import datetime
from components.lecture_card import LectureCard
from utils.i18n import t

class LecturesList(ft.Column):
    def __init__(self, schedule, refresh_callback):
        super().__init__(expand=True)
        self.schedule = schedule
        self.refresh_callback = refresh_callback
        self.selected_lecture_filter = t("schedule.tab_missing")
        self.current_sort_method = "date"
        self.update_list()

    def change_filter(self, filter_name):
        self.selected_lecture_filter = filter_name
        self.update_list()
        self.update()

    def change_sort_method(self, e):
        self.current_sort_method = e.control.value
        self.update_list()
        self.update()

    def update_list(self):
        filters = [t("schedule.tab_missing"), t("schedule.tab_future"), t("schedule.tab_past")]
        filter_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)
        
        for f_name in filters:
            is_sel = (f_name == self.selected_lecture_filter)
            
            btn = ft.Container(
                content=ft.Text(f_name, color="onSecondaryContainer" if is_sel else "onSurfaceVariant", weight="bold"), 
                bgcolor="secondaryContainer" if is_sel else "surfaceVariant",
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
                border_radius=20,
                on_click=lambda e, fn=f_name: self.change_filter(fn),
                ink=True
            )
            filter_row.controls.append(btn)

        sort_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("date", t("schedule.sort_date", default="מיון: תאריך")),
                ft.dropdown.Option("duration", t("schedule.sort_duration", default="מיון: אורך")),
                ft.dropdown.Option("type", t("schedule.sort_type", default="מיון: סוג"))
            ],
            value=self.current_sort_method, width=150, dense=True
        )
        sort_dropdown.on_change = self.change_sort_method
        
        top_bar = ft.Row([filter_row, sort_dropdown], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        list_view = ft.ListView(expand=True, padding=20, spacing=10)
        
        if self.selected_lecture_filter == t("schedule.tab_missing"):
            lectures = self.schedule.get_pending_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_past"):
            lectures = self.schedule.get_past_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_future"):
            lectures = self.schedule.get_future_lectures()
            
        if self.current_sort_method == "duration":
            lectures.sort(key=lambda x: x.duration_mins or 0, reverse=True)
        elif self.current_sort_method == "type":
            lectures.sort(key=lambda x: str(x.meeting_type))
        else:
            lectures.sort(key=lambda x: (x.date_obj if x.date_obj else datetime.min.date(), x.start_time if x.start_time else "00:00"))

        # --- חישוב הזמן הכולל של ההרצאות שמוצגות כרגע ---
        total_mins = 0
        for l in lectures:
            if l.duration_mins:
                total_mins += l.duration_mins
            elif l.start_time and l.end_time:
                try:
                    h1, m1 = map(int, l.start_time.split(':'))
                    h2, m2 = map(int, l.end_time.split(':'))
                    total_mins += (h2 * 60 + m2) - (h1 * 60 + m1)
                except Exception:
                    pass

        hours = total_mins // 60
        mins = total_mins % 60
        time_str = ""
        if hours > 0: time_str += f"{hours}h "
        time_str += f"{mins}m"
        if total_mins == 0: time_str = "0m"

        # יצירת השורה של סך הכל זמן (מוסתרת אם הרשימה ריקה)
        summary_text = t("schedule.total_duration", default="סה״כ זמן:") + f" {time_str}"
        summary_row = ft.Container(
            content=ft.Row([
                ft.Image(src="icons/access_time.svg", width=18, height=18, color="primary"),
                ft.Text(summary_text, weight="bold", color="primary", size=14)
            ], spacing=6, alignment=ft.MainAxisAlignment.START),
            padding=ft.padding.only(left=20, right=20, top=5),
            visible=len(lectures) > 0  # להציג רק אם יש הרצאות להשלים
        )
        # --------------------------------------------------

        if not lectures:
            empty_state = ft.Column([
                ft.Image(src="icons/event_busy.svg", width=60, height=60, color="onSurfaceVariant"), 
                ft.Text(t("schedule.no_lectures"), size=18, weight="w500", color="onSurfaceVariant")
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            list_view.controls.append(ft.Container(content=empty_state, alignment=ft.Alignment(0, 0), padding=ft.padding.only(top=100)))
        else:
            for lec in lectures:
                list_view.controls.append(LectureCard(lec, self.refresh_callback, is_mobile=False, show_date=True))

        self.controls = [
            ft.Container(content=top_bar, padding=ft.padding.only(top=10, bottom=5, left=10, right=10)),
            summary_row, # הוספת השורה ממש מתחת לתפריטי הסינון
            list_view
        ]