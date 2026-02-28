import flet as ft
import time
from models.course import Course

class AddCourseView(ft.Column):
    def __init__(self, page: ft.Page, schedule, change_screen_func):
        super().__init__(expand=True)
        self.app_page = page
        self.schedule = schedule
        self.change_screen = change_screen_func
        self.weekly_meetings = [] 

        self.title_input = ft.TextField(label="שם הקורס (למשל: אלגברה)", expand=True)
        self.lecturer_input = ft.TextField(label="שם המרצה", expand=True)
        self.room_input = ft.TextField(label="חדר/אולם", width=120)
        
        self.day_dropdown = ft.Dropdown(
            label="יום", options=[ft.dropdown.Option(d) for d in ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי"]], width=100
        )
        
        times = [f"{h:02d}:{m:02d}" for h in range(8, 22) for m in (0, 30)]
        self.start_dropdown = ft.Dropdown(label="שעת התחלה", options=[ft.dropdown.Option(t) for t in times], width=120, value="10:00")
        
        self.duration_dropdown = ft.Dropdown(
            label="אורך השיעור",
            options=[
                ft.dropdown.Option(key="1", text="שעה"),
                ft.dropdown.Option(key="1.5", text="שעה וחצי"),
                ft.dropdown.Option(key="2", text="שעתיים"),
                ft.dropdown.Option(key="3", text="שלוש שעות")
            ],
            width=120, value="2"
        )
        
        self.meetings_list_view = ft.ListView(height=150, spacing=5)

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(content=ft.Text("חזור", color="white", weight="bold"), on_click=lambda _: self.change_screen("schedule")),
                ft.Text("הוספת קורס חדש", size=20, weight="bold", color="white")
            ]),
            bgcolor="#1976D2", padding=5, border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("פרטי הקורס:", weight="bold", size=16),
                    ft.Row([self.title_input, self.lecturer_input]),
                    ft.Divider(),
                    ft.Text("הוסף זמני מפגשים:", weight="bold", size=16),
                    ft.Row([self.day_dropdown, self.start_dropdown, self.duration_dropdown, self.room_input], alignment=ft.MainAxisAlignment.START, wrap=True),
                    ft.ElevatedButton("➕ הוסף זמן לקורס", on_click=self.add_meeting, bgcolor="#F57C00", color="white"),
                    self.meetings_list_view,
                    ft.Divider(),
                    ft.ElevatedButton("✅ שמור קורס וייצר הכל לסמסטר", on_click=self.save_course, bgcolor="#43A047", color="white", width=300)
                ], spacing=15)
            )
        ]

    def add_meeting(self, e):
        if not self.day_dropdown.value or not self.start_dropdown.value:
            return
            
        start_str = self.start_dropdown.value
        dur = float(self.duration_dropdown.value)
        h, m = map(int, start_str.split(':'))
        
        total_m = m + int((dur - int(dur)) * 60)
        total_h = h + int(dur) + (total_m // 60)
        total_m = total_m % 60
        end_str = f"{total_h:02d}:{total_m:02d}"
        
        meeting = {
            "day": self.day_dropdown.value, "start": start_str, "end": end_str, "room": self.room_input.value
        }
        self.weekly_meetings.append(meeting)
        
        self.meetings_list_view.controls.append(ft.Text(f"📌 יום {meeting['day']}, {meeting['start']}-{meeting['end']} (חדר: {meeting['room']})", color="#1976D2"))
        self.app_page.update()

    def save_course(self, e):
        if not self.title_input.value or len(self.weekly_meetings) == 0:
            self.app_page.snack_bar = ft.SnackBar(ft.Text("שגיאה! חובה להזין שם קורס ולפחות מועד אחד."))
            self.app_page.snack_bar.open = True
            self.app_page.update()
            return
            
        new_course = Course(course_id=str(time.time()), title=self.title_input.value, lecturer=self.lecturer_input.value)
        for m in self.weekly_meetings:
            new_course.add_weekly_meeting(self.schedule.semester_start, self.schedule.semester_end, m["day"], m["start"], m["end"], m["room"])
            
        self.schedule.add_course(new_course)
        self.app_page.snack_bar = ft.SnackBar(ft.Text(f"הקורס '{self.title_input.value}' נוסף בהצלחה!"))
        self.app_page.snack_bar.open = True
        self.app_page.update()
        self.change_screen("schedule")