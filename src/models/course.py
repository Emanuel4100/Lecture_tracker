import time
from datetime import timedelta
from models.lecture import LectureSession, LectureStatus

class Course:
    def __init__(self, course_id, title, lecturer):
        self.course_id = course_id
        self.title = title
        self.lecturer = lecturer
        self.lectures = []

    def add_weekly_meeting(self, semester_start, semester_end, day_name, start_time, end_time, room):
        weekdays = {"שני": 0, "שלישי": 1, "רביעי": 2, "חמישי": 3, "שישי": 4, "שבת": 5, "ראשון": 6}
        target_weekday = weekdays.get(day_name, 6)

        current_date = semester_start
        
        while current_date <= semester_end:
            if current_date.weekday() == target_weekday:
                new_id = str(time.time()) + str(current_date)
                new_lec = LectureSession(
                    session_id=new_id,
                    title=self.title,
                    lecturer=self.lecturer,
                    date_obj=current_date,
                    start_time=start_time,
                    end_time=end_time,
                    room=room,
                    status=LectureStatus.NEEDS_WATCHING
                )
                self.lectures.append(new_lec)
            current_date += timedelta(days=1)
        
        self.lectures.sort(key=lambda l: (l.date_obj, l.start_time))