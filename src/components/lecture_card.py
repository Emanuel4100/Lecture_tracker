import flet as ft

class LectureCard(ft.Container):
    def __init__(self, lecture):
        super().__init__()
        self.lecture = lecture
        
        # Using Hex colors prevents version mismatch errors
        self.bgcolor = "#E3F2FD" 
        self.border_radius = 10
        self.padding = 15
        self.margin = ft.margin.only(bottom=10)
        
        self.content = ft.Column([
            ft.Text(self.lecture.title, weight=ft.FontWeight.BOLD, size=16, color="#0D47A1"),
            ft.Text(f"{self.lecture.start_time} - {self.lecture.end_time} | חדר: {self.lecture.room}", color="black"),
            ft.Text(f"מרצה: {self.lecture.lecturer}", color="grey", size=12)
        ], spacing=5)