from datetime import datetime, timedelta
from models.lecture import LectureStatus

class SemesterSchedule:
    def __init__(self):
        self.courses = []
        self.semester_start = None
        self.semester_end = None
        
        self.notify_before_mins = 15
        self.notify_after_mins = 15

    def is_semester_set(self):
        return self.semester_start is not None and self.semester_end is not None

    def set_semester(self, start_date_str, end_date_str):
        self.semester_start = datetime.strptime(start_date_str, "%d/%m/%Y").date()
        self.semester_end = datetime.strptime(end_date_str, "%d/%m/%Y").date()

    def set_notifications(self, before_mins, after_mins):
        self.notify_before_mins = int(before_mins)
        self.notify_after_mins = int(after_mins)

    def add_course(self, course):
        self.courses.append(course)

    def get_all_lectures_flat(self):
        all_lecs = []
        for c in self.courses:
            all_lecs.extend(c.lectures)
        return sorted(all_lecs, key=lambda l: (l.date_obj, l.start_time))

    def get_pending_lectures(self):
        today = datetime.now().date()
        return [lec for lec in self.get_all_lectures_flat() if lec.status == LectureStatus.NEEDS_WATCHING and lec.date_obj <= today]

    def get_weekly_lectures(self):
        today = datetime.now().date()
        idx = (today.weekday() + 1) % 7 
        sun = today - timedelta(days=idx)
        sat = sun + timedelta(days=6)
        
        return [lec for lec in self.get_all_lectures_flat() if sun <= lec.date_obj <= sat]

    def get_all_lectures(self):
        return [lec for lec in self.get_all_lectures_flat() if lec.status == LectureStatus.NEEDS_WATCHING]

    def get_history_lectures(self):
        return [lec for lec in self.get_all_lectures_flat() if lec.status != LectureStatus.NEEDS_WATCHING]