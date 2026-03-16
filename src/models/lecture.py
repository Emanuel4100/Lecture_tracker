import datetime

class LectureStatus:
    ATTENDED = "status.attended"
    WATCHED_RECORDING = "status.watched"
    NEEDS_WATCHING = "status.needs_watching"
    SKIPPED = "status.skipped"
    CANCELLED = "status.cancelled"

class LectureSession:
    def __init__(self, session_id, title, lecturer, date_obj, start_time="", end_time="", room="", status=LectureStatus.NEEDS_WATCHING, duration_mins=None, is_one_off=False, meeting_number=None, meeting_type=""):
        self.session_id = session_id
        self.title = title
        self.lecturer = lecturer
        self.date_obj = date_obj
        self.start_time = start_time
        self.end_time = end_time
        self.duration_mins = duration_mins 
        self.room = room
        self.status = status
        self.course_color = "surfaceVariant"
        self.is_one_off = is_one_off # True if this is a custom task/event
        self.meeting_number = meeting_number
        self.external_link = "" # Store Drive/Zoom links
        self.meeting_type = meeting_type

    @property
    def date_str(self):
        return self.date_obj.strftime("%d/%m/%Y") if self.date_obj else ""

    @property
    def display_title(self):
        # Display the meeting number if enabled and exists
        if self.meeting_number:
            return f"{self.title} - #{self.meeting_number}"
        return self.title

    def to_dict(self):
        return {
            "session_id": self.session_id, "title": self.title, "lecturer": self.lecturer,
            "date_str": self.date_str, "start_time": self.start_time, "end_time": self.end_time,
            "duration_mins": self.duration_mins, "room": self.room, "status": self.status,
            "course_color": self.course_color, "is_one_off": self.is_one_off,
            "meeting_number": self.meeting_number, "external_link": self.external_link,
            "meeting_type": self.meeting_type
        }

    @classmethod
    def from_dict(cls, data):
        # Compatibility with older versions
        old_status_map = {
            "הלכתי לראות": LectureStatus.ATTENDED, "ראיתי את ההקלטה": LectureStatus.WATCHED_RECORDING,
            "צריך לראות את ההקלטה": LectureStatus.NEEDS_WATCHING, "לדלג / אין צורך": LectureStatus.SKIPPED, "בוטלה": LectureStatus.CANCELLED
        }
        loaded_status = data.get("status", LectureStatus.NEEDS_WATCHING)
        loaded_status = old_status_map.get(loaded_status, loaded_status)
        
        date_str = data.get("date_str", "")
        date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y").date() if date_str else datetime.datetime.now().date()
        
        lec = cls(
            session_id=data["session_id"], title=data["title"], lecturer=data.get("lecturer", ""),
            date_obj=date_obj, start_time=data.get("start_time", ""), end_time=data.get("end_time", ""),
            room=data.get("room", ""), status=loaded_status,
            duration_mins=data.get("duration_mins"), is_one_off=data.get("is_one_off", False),
            meeting_number=data.get("meeting_number"), meeting_type=data.get("meeting_type", "")
        )
        lec.course_color = data.get("course_color", "surfaceVariant")
        lec.external_link = data.get("external_link", "")
        return lec