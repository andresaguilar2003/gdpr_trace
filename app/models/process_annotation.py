class ProcessAnnotation:

    def __init__(self):
        self.activity_annotations = {}

    def add_annotation(self, activity_name, gdpr_event, position):

        annotations = self.activity_annotations.setdefault(activity_name, [])

        annotation = {
            "event": gdpr_event,
            "position": position
        }

        if annotation not in annotations:
            annotations.append(annotation)

    def get_annotations(self, activity_name):
        return self.activity_annotations.get(activity_name, [])

    def remove_annotation(self, activity_name, gdpr_event):

        if activity_name not in self.activity_annotations:
            return

        self.activity_annotations[activity_name] = [
            ann for ann in self.activity_annotations[activity_name]
            if ann["event"] != gdpr_event
        ]