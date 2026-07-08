from app.specifications.data_categories import DataCategory


class GDPRAnnotation:

    def __init__(self, legal_basis: str = None,
                 data_category: DataCategory = None,
                 notes: str = None):

        self.legal_basis = legal_basis

        self.data_category = data_category

        self.notes = notes

    def __repr__(self):

        return f"GDPRAnnotation(category={self.data_category}, legal_basis={self.legal_basis})"