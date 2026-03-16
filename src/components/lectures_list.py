import flet as ft
from components.lecture_card import LectureCard
from utils.i18n import t

class LecturesList(ft.Column):
    def __init__(self, schedule, refresh_callback):
        super().__init__(expand=True)
        self.schedule = schedule
        self.refresh_callback = refresh_callback
        self.selected_lecture_filter = t("schedule.tab_missing")
        self.update_list()

    def change_filter(self, filter_name):
        self.selected_lecture_filter = filter_name
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

        list_view = ft.ListView(expand=True, padding=20, spacing=10)
        
        if self.selected_lecture_filter == t("schedule.tab_missing"):
            lectures = self.schedule.get_pending_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_past"):
            lectures = self.schedule.get_past_lectures()
        elif self.selected_lecture_filter == t("schedule.tab_future"):
            lectures = self.schedule.get_future_lectures()
            
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
            ft.Container(content=filter_row, padding=ft.padding.only(top=10, bottom=5)),
            list_view
        ]