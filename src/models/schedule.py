import os
import json
from datetime import datetime, timedelta
from models.lecture import LectureStatus
from models.course import Course

class SemesterSchedule:
    def __init__(self):
        self.courses = []
        self.semester_start = None
        self.semester_end = None
        self.notify_before_mins = 15
        self.notify_after_mins = 15
        self.show_weekend = False
        self.filepath = "my_schedule_data.json"

    def save_to_file(self):
        data = {
            "semester_start": self.semester_start.strftime("%d/%m/%Y") if self.semester_start else None,
            "semester_end": self.semester_end.strftime("%d/%m/%Y") if self.semester_end else None,
            "notify_before_mins": self.notify_before_mins,
            "notify_after_mins": self.notify_after_mins,
            "show_weekend": self.show_weekend,
            "courses": [c.to_dict() for c in self.courses]
        }
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_from_file(self):
        if not os.path.exists(self.filepath):
            return False
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if data.get("semester_start") and data.get("semester_end"):
                self.semester_start = datetime.strptime(data["semester_start"], "%d/%m/%Y").date()
                self.semester_end = datetime.strptime(data["semester_end"], "%d/%m/%Y").date()

            self.notify_before_mins = data.get("notify_before_mins", 15)
            self.notify_after_mins = data.get("notify_after_mins", 15)
            self.show_weekend = data.get("show_weekend", False)

            self.courses = []
            for c_data in data.get("courses", []):
                self.courses.append(Course.from_dict(c_data))
            return True
        except Exception:
            return False

    def is_semester_set(self):
        return self.semester_start is not None and self.semester_end is not None

    def set_semester(self, start_date_str, end_date_str):
        self.semester_start = datetime.strptime(start_date_str, "%d/%m/%Y").date()
        self.semester_end = datetime.strptime(end_date_str, "%d/%m/%Y").date()
        for course in self.courses:
            course.recalculate_all_lectures(self.semester_start, self.semester_end)
        self.save_to_file()

    def set_notifications(self, before_mins, after_mins):
        self.notify_before_mins = int(before_mins)
        self.notify_after_mins = int(after_mins)
        self.save_to_file()

    def add_course(self, course):
        self.courses.append(course)
        self.save_to_file()

    def get_all_lectures_flat(self):
        all_lecs = []
        for c in self.courses:
            all_lecs.extend(c.lectures)
        return sorted(all_lecs, key=lambda l: (l.date_obj, l.start_time))

    def get_weekly_lectures(self, target_date=None):
        if target_date is None:
            target_date = datetime.now().date()
        idx = (target_date.weekday() + 1) % 7 
        sun = target_date - timedelta(days=idx)
        sat = sun + timedelta(days=6)
        return [lec for lec in self.get_all_lectures_flat() if sun <= lec.date_obj <= sat]

    def get_pending_lectures(self):
        today = datetime.now().date()
        return [lec for lec in self.get_all_lectures_flat() if lec.status == LectureStatus.NEEDS_WATCHING and lec.date_obj <= today]

    def get_past_lectures(self):
        today = datetime.now().date()
        return [lec for lec in self.get_all_lectures_flat() if lec.date_obj < today or (lec.date_obj == today and lec.status != LectureStatus.NEEDS_WATCHING)]

    def get_future_lectures(self):
        today = datetime.now().date()
        return [lec for lec in self.get_all_lectures_flat() if lec.date_obj > today]