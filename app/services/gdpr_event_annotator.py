from app.models.gdpr_annotation import GDPRAnnotation
from app.specifications.data_categories import DataCategory


class GDPREventAnnotator:

    def annotate(self, event, activity_type):

        data_category = self.infer_data_category(activity_type)

        annotation = GDPRAnnotation(
            legal_basis=None,
            data_category=data_category,
            notes=f"Inferred from activity type {activity_type.name}"
        )

        event.set_gdpr_annotation(annotation)

        return event

    def infer_data_category(self, activity_type):

        if activity_type.name == "DATA_PROCESSING":
            return DataCategory.HEALTH

        if activity_type.name == "DATA_ACCESS":
            return DataCategory.STANDARD

        if activity_type.name == "DATA_TRANSFER":
            return DataCategory.INTERNATIONAL_TRANSFER

        if activity_type.name == "AUTOMATED_DECISION":
            return DataCategory.PROFILING

        return DataCategory.STANDARD