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
            label="יום בשבוע",
            options=[ft.dropdown.Option(d) for d in ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי"]],
            width=100
        )
        self.start_input = ft.TextField(label="התחלה", width=90, value="10:00")
        self.end_input = ft.TextField(label="סיום", width=90, value="12:00")
        
        self.meetings_list_view = ft.ListView(height=150, spacing=5)

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(
                    content=ft.Text("חזור", color="white", weight="bold"), 
                    on_click=lambda _: self.change_screen("schedule")
                ),
                ft.Text("הוספת קורס חדש", size=20, weight="bold", color="white")
            ]),
            bgcolor="#1976D2",
            padding=5,
            border_radius=10
        )

        self.controls = [
            header,
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("פרטי הקורס:", weight="bold", size=16),
                    ft.Row([self.title_input, self.lecturer_input]),
                    ft.Divider(),
                    
                    ft.Text("הוסף זמני מפגשים (הרצאה / תרגול):", weight="bold", size=16),
                    ft.Row([self.day_dropdown, self.start_input, self.end_input, self.room_input], alignment=ft.MainAxisAlignment.START),
                    ft.ElevatedButton("➕ הוסף זמן לקורס", on_click=self.add_meeting, bgcolor="#F57C00", color="white"),
                    
                    self.meetings_list_view,
                    ft.Divider(),
                    
                    ft.ElevatedButton("✅ שמור קורס וייצר הכל לסמסטר", on_click=self.save_course, bgcolor="#43A047", color="white", width=300)
                ], spacing=15)
            )
        ]

    def add_meeting(self, e):
        if not self.day_dropdown.value:
            return
        
        meeting = {
            "day": self.day_dropdown.value,
            "start": self.start_input.value,
            "end": self.end_input.value,
            "room": self.room_input.value
        }
        self.weekly_meetings.append(meeting)
        
        self.meetings_list_view.controls.append(
            ft.Text(f"📌 יום {meeting['day']}, {meeting['start']}-{meeting['end']} (חדר: {meeting['room']})", color="#1976D2")
        )
        self.app_page.update()

    def save_course(self, e):
        if not self.title_input.value or len(self.weekly_meetings) == 0:
            snack = ft.SnackBar(ft.Text("שגיאה! חובה להזין שם קורס ולפחות מועד הרצאה אחד."))
            self.app_page.snack_bar = snack
            snack.open = True
            self.app_page.update()
            return
            
        new_course = Course(
            course_id=str(time.time()),
            title=self.title_input.value,
            lecturer=self.lecturer_input.value
        )
        
        for m in self.weekly_meetings:
            new_course.add_weekly_meeting(
                semester_start=self.schedule.semester_start,
                semester_end=self.schedule.semester_end,
                day_name=m["day"],
                start_time=m["start"],
                end_time=m["end"],
                room=m["room"]
            )
            
        self.schedule.add_course(new_course)
        
        snack = ft.SnackBar(ft.Text(f"הקורס '{self.title_input.value}' וכל ההרצאות שלו נוספו בהצלחה!"))
        self.app_page.snack_bar = snack
        snack.open = True
        self.app_page.update()
        
        self.change_screen("schedule")