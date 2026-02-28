import datetime

class LectureStatus:
    ATTENDED = "הלכתי לראות"
    WATCHED_RECORDING = "ראיתי את ההקלטה"
    NEEDS_WATCHING = "צריך לראות את ההקלטה"
    SKIPPED = "לדלג / אין צורך"
    CANCELLED = "בוטלה"

class LectureSession:
    def __init__(self, session_id, title, lecturer, date_obj, start_time, end_time, room, status=LectureStatus.NEEDS_WATCHING):
        self.session_id = session_id
        self.title = title
        self.lecturer = lecturer
        self.date_obj = date_obj 
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
        self.status = status
        self.course_color = "#E3F2FD" 

    @property
    def date_str(self):
        return self.date_obj.strftime("%d/%m/%Y")

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "title": self.title,
            "lecturer": self.lecturer,
            "date_str": self.date_str,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "room": self.room,
            "status": self.status,
            "course_color": self.course_color
        }

    @classmethod
    def from_dict(cls, data):
        date_obj = datetime.datetime.strptime(data["date_str"], "%d/%m/%Y").date()
        lec = cls(
            session_id=data["session_id"],
            title=data["title"],
            lecturer=data["lecturer"],
            date_obj=date_obj,
            start_time=data["start_time"],
            end_time=data["end_time"],
            room=data["room"],
            status=data.get("status", LectureStatus.NEEDS_WATCHING)
        )
        lec.course_color = data.get("course_color", "#E3F2FD")
        return lec