import flet as ft
from models.lecture import LectureStatus

class LectureCard(ft.Container):
    def __init__(self, lecture, update_callback):
        super().__init__()
        self.lecture = lecture
        self.update_callback = update_callback 
        
        self.border_radius = 8
        self.padding = 10
        self.margin = ft.margin.only(bottom=10)
        
        self.bgcolor = self.get_bg_color()

        self.status_dropdown = ft.Dropdown(
            value=self.lecture.status,
            options=[
                ft.dropdown.Option(LectureStatus.NEEDS_WATCHING),
                ft.dropdown.Option(LectureStatus.ATTENDED),
                ft.dropdown.Option(LectureStatus.WATCHED_RECORDING),
                ft.dropdown.Option(LectureStatus.SKIPPED),
            ],
            text_size=12,
            content_padding=5
        )
        
        self.status_dropdown.on_change = self.status_changed
        
        self.content = ft.Column([
            ft.Text(self.lecture.title, weight="bold", size=14, color="#0D47A1"),
            ft.Text(f"{self.lecture.date_str} | {self.lecture.start_time}-{self.lecture.end_time}", color="black", size=11),
            ft.Text(f"{self.lecture.lecturer} | חדר: {self.lecture.room}", color="grey", size=11),
            ft.Container(height=2),
            self.status_dropdown
        ], spacing=2)

    def get_bg_color(self):
        if self.lecture.status in [LectureStatus.ATTENDED, LectureStatus.WATCHED_RECORDING]:
            return "#C8E6C9" 
        elif self.lecture.status == LectureStatus.SKIPPED:
            return "#FFCDD2" 
        else:
            return "#E3F2FD" 

    def status_changed(self, e):
        self.lecture.status = self.status_dropdown.value
        self.bgcolor = self.get_bg_color()
        if self.update_callback:
            self.update_callback()