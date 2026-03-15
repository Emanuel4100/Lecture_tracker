import datetime

class LectureStatus:
    ATTENDED = "status.attended"
    WATCHED_RECORDING = "status.watched"
    NEEDS_WATCHING = "status.needs_watching"
    SKIPPED = "status.skipped"
    CANCELLED = "status.cancelled"

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
        # מנגנון תאימות לאחור (Backward Compatibility)
        old_status_map = {
            "הלכתי לראות": LectureStatus.ATTENDED,
            "ראיתי את ההקלטה": LectureStatus.WATCHED_RECORDING,
            "צריך לראות את ההקלטה": LectureStatus.NEEDS_WATCHING,
            "לדלג / אין צורך": LectureStatus.SKIPPED,
            "בוטלה": LectureStatus.CANCELLED
        }
        loaded_status = data.get("status", LectureStatus.NEEDS_WATCHING)
        loaded_status = old_status_map.get(loaded_status, loaded_status)

        date_obj = datetime.datetime.strptime(data["date_str"], "%d/%m/%Y").date()
        lec = cls(
            session_id=data["session_id"],
            title=data["title"],
            lecturer=data["lecturer"],
            date_obj=date_obj,
            start_time=data["start_time"],
            end_time=data["end_time"],
            room=data["room"],
            status=loaded_status
        )
        lec.course_color = data.get("course_color", "#E3F2FD")
        return lec