import flet as ft

class LectureCard(ft.Container):
    def __init__(self, lecture):
        super().__init__()
        self.lecture = lecture
        self.bgcolor = ft.colors.BLUE_50
        self.border_radius = 10
        self.padding = 15
        self.margin = ft.margin.only(bottom=10)
        
        self.content = ft.Column([
            ft.Text(self.lecture.title, weight=ft.FontWeight.BOLD, size=16, color=ft.colors.BLUE_900),
            ft.Text(f"{self.lecture.start_time} - {self.lecture.end_time} | חדר: {self.lecture.room}", color=ft.colors.BLACK87),
            ft.Text(f"מרצה: {self.lecture.lecturer}", color=ft.colors.BLACK54, size=12)
        ], spacing=5)