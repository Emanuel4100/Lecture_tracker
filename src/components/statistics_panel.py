import flet as ft
from models.lecture import LectureStatus
from utils.i18n import t

class StatisticsPanel(ft.Column):
    def __init__(self, schedule):
        super().__init__(expand=True, horizontal_alignment="center")
        self.schedule = schedule
        self.build_view()

    def build_view(self):
        all_lectures = self.schedule.get_all_lectures_flat()
        
        if not all_lectures:
            self.controls.append(ft.Container(content=ft.Text(t("stats.no_data"), size=16, color="grey"), alignment=ft.Alignment(0, 0), padding=50))
            return

        attended = sum(1 for lec in all_lectures if lec.status in [LectureStatus.ATTENDED, LectureStatus.WATCHED_RECORDING])
        skipped = sum(1 for lec in all_lectures if lec.status == LectureStatus.SKIPPED)
        needs_watching = sum(1 for lec in all_lectures if lec.status == LectureStatus.NEEDS_WATCHING)
        cancelled = sum(1 for lec in all_lectures if lec.status == LectureStatus.CANCELLED)
        total = len(all_lectures)
        
        bar_controls = []
        if attended > 0: bar_controls.append(ft.Container(content=ft.Text(f"{int((attended/total)*100)}%", color="white", weight="bold"), alignment=ft.Alignment(0, 0), expand=attended, bgcolor="#4CAF50"))
        if skipped > 0: bar_controls.append(ft.Container(content=ft.Text(f"{int((skipped/total)*100)}%", color="white", weight="bold"), alignment=ft.Alignment(0, 0), expand=skipped, bgcolor="#757575"))
        if needs_watching > 0: bar_controls.append(ft.Container(content=ft.Text(f"{int((needs_watching/total)*100)}%", color="black", weight="bold"), alignment=ft.Alignment(0, 0), expand=needs_watching, bgcolor="#E0E0E0"))
        if cancelled > 0: bar_controls.append(ft.Container(content=ft.Text(f"{int((cancelled/total)*100)}%", color="white", weight="bold"), alignment=ft.Alignment(0, 0), expand=cancelled, bgcolor="#F44336"))

        stat_bar = ft.Container(content=ft.Row(bar_controls, spacing=0), height=40, border_radius=8, margin=ft.margin.symmetric(vertical=20))
        
        legend = ft.Column([
            ft.Row([ft.Container(width=15, height=15, bgcolor="#4CAF50", border_radius=10), ft.Text(t("stats.attended", count=attended), size=16)]),
            ft.Row([ft.Container(width=15, height=15, bgcolor="#757575", border_radius=10), ft.Text(t("stats.skipped", count=skipped), size=16)]),
            ft.Row([ft.Container(width=15, height=15, bgcolor="#E0E0E0", border_radius=10), ft.Text(t("stats.needs_watching", count=needs_watching), size=16)]),
            ft.Row([ft.Container(width=15, height=15, bgcolor="#F44336", border_radius=10), ft.Text(t("stats.cancelled", count=cancelled), size=16)])
        ], alignment="center")
        
        self.controls.extend([
            ft.Text(t("stats.title"), size=22, weight="bold", color="#1976D2", text_align="center"),
            ft.Text(t("stats.total_lectures", total=total), size=14, color="grey", text_align="center"),
            stat_bar, legend
        ])