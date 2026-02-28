import flet as ft
from models.lecture import LectureStatus

class LectureCard(ft.Container):
    def __init__(self, lecture, update_callback):
        super().__init__()
        self.lecture = lecture
        self.update_callback = update_callback 
        
        self.border_radius = 8
        self.padding = 5
        self.margin = ft.margin.only(bottom=5)
        
        self.bgcolor = self.lecture.course_color

        title = ft.Text(self.lecture.title, weight="bold", size=12, color="black87", no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS)
        time_room = ft.Text(f"{self.lecture.start_time}-{self.lecture.end_time} | {self.lecture.room}", color="black54", size=10)

        self.content = ft.Column([
            title,
            time_room,
            self.build_status_icons()
        ], spacing=2)

    def build_status_icons(self):
        def create_icon(emoji, status_value, tooltip_text):
            is_active = (self.lecture.status == status_value)
            
            return ft.Container(
                content=ft.Text(emoji, size=14, tooltip=tooltip_text),
                padding=4,
                bgcolor="white" if is_active else "transparent",
                border=ft.border.all(2, "black87") if is_active else None,
                border_radius=15,
                on_click=lambda e: self.set_status(status_value)
            )

        return ft.Row([
            create_icon("✅", LectureStatus.ATTENDED, "הלכתי"),
            create_icon("🎥", LectureStatus.WATCHED_RECORDING, "הקלטה"),
            create_icon("⏳", LectureStatus.NEEDS_WATCHING, "להשלים"),
            create_icon("❌", LectureStatus.SKIPPED, "דילגתי"),
            create_icon("🚫", LectureStatus.CANCELLED, "בוטלה"),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)

    def set_status(self, new_status):
        self.lecture.status = new_status
        if self.update_callback:
            self.update_callback()