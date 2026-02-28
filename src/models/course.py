import time
import random
from datetime import timedelta
from models.lecture import LectureSession, LectureStatus

COURSE_COLORS = [
    "#FFCDD2", "#F8BBD0", "#E1BEE7", "#D1C4E9", "#C5CAE9", 
    "#BBDEFB", "#B3E5FC", "#B2EBF2", "#B2DFDB", "#C8E6C9", 
    "#DCEDC8", "#F0F4C3", "#FFF9C4", "#FFECB3", "#FFE0B2"
]

class Course:
    def __init__(self, course_id, title, lecturer):
        self.course_id = course_id
        self.title = title
        self.lecturer = lecturer
        self.color = random.choice(COURSE_COLORS)
        self.meetings = []
        self.lectures = []

    def add_weekly_meeting(self, semester_start, semester_end, day_name, start_time, end_time, room):
        meeting_rule = {
            "day_name": day_name,
            "start_time": start_time,
            "end_time": end_time,
            "room": room
        }
        self.meetings.append(meeting_rule)
        self._generate_lectures_for_rule(semester_start, semester_end, meeting_rule)
        self.lectures.sort(key=lambda l: (l.date_obj, l.start_time))

    def _generate_lectures_for_rule(self, semester_start, semester_end, rule, preserved_statuses=None):
        weekdays = {"שני": 0, "שלישי": 1, "רביעי": 2, "חמישי": 3, "שישי": 4, "שבת": 5, "ראשון": 6}
        target_weekday = weekdays.get(rule["day_name"], 6)

        current_date = semester_start
        
        while current_date <= semester_end:
            if current_date.weekday() == target_weekday:
                date_str = current_date.strftime("%d/%m/%Y")
                status = LectureStatus.NEEDS_WATCHING
                
                if preserved_statuses:
                    key = (date_str, rule["start_time"])
                    if key in preserved_statuses:
                        status = preserved_statuses[key]

                new_id = str(time.time()) + str(current_date) + rule["start_time"]
                new_lec = LectureSession(
                    session_id=new_id,
                    title=self.title,
                    lecturer=self.lecturer,
                    date_obj=current_date,
                    start_time=rule["start_time"],
                    end_time=rule["end_time"],
                    room=rule["room"],
                    status=status
                )
                new_lec.course_color = self.color
                self.lectures.append(new_lec)
            current_date += timedelta(days=1)

    def recalculate_all_lectures(self, new_start, new_end):
        preserved_statuses = {}
        for lec in self.lectures:
            preserved_statuses[(lec.date_str, lec.start_time)] = lec.status
        
        self.lectures = []
        for rule in self.meetings:
            self._generate_lectures_for_rule(new_start, new_end, rule, preserved_statuses)
        self.lectures.sort(key=lambda l: (l.date_obj, l.start_time))

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "title": self.title,
            "lecturer": self.lecturer,
            "color": self.color,
            "meetings": self.meetings,
            "lectures": [l.to_dict() for l in self.lectures]
        }

    @classmethod
    def from_dict(cls, data):
        course = cls(
            course_id=data["course_id"],
            title=data["title"],
            lecturer=data["lecturer"]
        )
        course.color = data.get("color", random.choice(COURSE_COLORS))
        course.meetings = data.get("meetings", [])
        course.lectures = [LectureSession.from_dict(l) for l in data.get("lectures", [])]
        return course