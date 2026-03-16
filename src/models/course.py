import time
import random
from datetime import timedelta
from models.lecture import LectureSession, LectureStatus
from utils.i18n import t

COURSE_COLORS = [
    "red100", "pink100", "purple100", "deepPurple100", "indigo100",
    "blue100", "lightBlue100", "cyan100", "teal100", "green100",
    "lightGreen100", "lime100", "yellow100", "amber100", "orange100"
]

class Course:
    def __init__(self, course_id, title, lecturer="", course_code="", link=""):
        self.course_id = course_id
        self.title = title
        self.lecturer = lecturer
        self.course_code = course_code
        self.link = link
        self.color = random.choice(COURSE_COLORS)
        self.meetings = []
        self.lectures = []

    def add_weekly_meeting(self, semester_start, semester_end, day_name, start_time, end_time, location, meeting_type="meeting_types.lecture"):
        meeting_rule = {
            "day_name": day_name,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "meeting_type": meeting_type
        }
        self.meetings.append(meeting_rule)
        self.recalculate_all_lectures(semester_start, semester_end)

    def _generate_lectures_for_rule(self, semester_start, semester_end, rule, preserved_statuses=None, preserved_links=None):
        weekdays = {"days.monday": 0, "days.tuesday": 1, "days.wednesday": 2, "days.thursday": 3, "days.friday": 4, "days.saturday": 5, "days.sunday": 6,
                    "שני": 0, "שלישי": 1, "רביעי": 2, "חמישי": 3, "שישי": 4, "שבת": 5, "ראשון": 6} 
        target_weekday = weekdays.get(rule["day_name"], 6)

        current_date = semester_start
        while current_date <= semester_end:
            if current_date.weekday() == target_weekday:
                date_str = current_date.strftime("%d/%m/%Y")
                status = LectureStatus.NEEDS_WATCHING
                ext_link = ""
                
                # Restore previous status and links if they existed
                if preserved_statuses:
                    key = (date_str, rule["start_time"])
                    if key in preserved_statuses:
                        status = preserved_statuses[key]
                if preserved_links:
                    key = (date_str, rule["start_time"])
                    if key in preserved_links:
                        ext_link = preserved_links[key]

                new_id = str(time.time()) + str(current_date) + rule["start_time"]
                m_type = rule.get('meeting_type', 'meeting_types.lecture')
                if m_type == "הרצאה": m_type = "meeting_types.lecture"
                elif m_type == "תרגול": m_type = "meeting_types.practice"
                elif m_type == "מעבדה": m_type = "meeting_types.lab"
                
                session_title = f"{self.title} - {t(m_type)}"
                
                new_lec = LectureSession(
                    session_id=new_id, title=session_title, lecturer=self.lecturer,
                    date_obj=current_date, start_time=rule["start_time"], end_time=rule["end_time"],
                    room=rule["location"], status=status, meeting_type=m_type
                )
                new_lec.course_color = self.color
                new_lec.external_link = ext_link
                
                # Calculate duration in minutes for standard lectures
                try:
                    h1, m1 = map(int, rule["start_time"].split(':'))
                    h2, m2 = map(int, rule["end_time"].split(':'))
                    new_lec.duration_mins = (h2 * 60 + m2) - (h1 * 60 + m1)
                except:
                    new_lec.duration_mins = 0
                    
                self.lectures.append(new_lec)
            current_date += timedelta(days=1)

    def recalculate_all_lectures(self, new_start, new_end, enable_numbers=True):
        preserved_statuses = {}
        preserved_links = {}
        
        # Keep custom one-off events
        one_off_lectures = [l for l in self.lectures if l.is_one_off]
        
        for lec in self.lectures:
            if not lec.is_one_off:
                preserved_statuses[(lec.date_str, lec.start_time)] = lec.status
                preserved_links[(lec.date_str, lec.start_time)] = lec.external_link
                
        self.lectures = one_off_lectures
        for rule in self.meetings:
            self._generate_lectures_for_rule(new_start, new_end, rule, preserved_statuses, preserved_links)
            
        self.lectures.sort(key=lambda l: (l.date_obj, l.start_time if l.start_time else "00:00"))
        
        # Auto-numbering logic
        if enable_numbers:
            counters = {}
            for lec in self.lectures:
                if not lec.is_one_off:
                    base_title = lec.title
                    counters[base_title] = counters.get(base_title, 0) + 1
                    lec.meeting_number = counters[base_title]
        else:
            for lec in self.lectures:
                lec.meeting_number = None

    def to_dict(self):
        return {
            "course_id": self.course_id, "title": self.title, "lecturer": self.lecturer,
            "course_code": self.course_code, "link": self.link, "color": self.color, 
            "meetings": self.meetings, "lectures": [l.to_dict() for l in self.lectures]
        }

    @classmethod
    def from_dict(cls, data):
        course = cls(course_id=data["course_id"], title=data["title"], lecturer=data.get("lecturer", ""), course_code=data.get("course_code", ""), link=data.get("link", ""))
        course.color = data.get("color", random.choice(COURSE_COLORS))
        course.meetings = data.get("meetings", [])
        course.lectures = [LectureSession.from_dict(l) for l in data.get("lectures", [])]
        return course