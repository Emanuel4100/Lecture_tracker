class WeeklySchedule:
    def __init__(self):
        self.days = {
            "ראשון": [], "שני": [], "שלישי": [], 
            "רביעי": [], "חמישי": [], "שישי": []
        }

    def add_lecture(self, lecture):
        if lecture.day in self.days:
            self.days[lecture.day].append(lecture)
            # Sort chronologically by start time
            self.days[lecture.day].sort(key=lambda l: l.start_time)