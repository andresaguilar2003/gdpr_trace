class Context:

    def __init__(
        self,
        purpose=None,
        legal_basis=None,
        data_category=None,
        data_subject_type=None,
        processing_operation=None,
        retention_period=None,
        processing_domain=None,
        has_third_party_recipients=False,
        international_transfer="none",
        transfer_safeguard="none",
        consent_status="not_needed"
    ):

        self.purpose = purpose
        self.legal_basis = legal_basis
        self.data_category = data_category
        self.data_subject_type = data_subject_type
        self.processing_operation = processing_operation
        self.retention_period = retention_period
        self.processing_domain = processing_domain
        self.has_third_party_recipients = has_third_party_recipients
        self.international_transfer = international_transfer
        self.transfer_safeguard = transfer_safeguard
        self.consent_status = consent_status

    def requires_consent(self):

        """
        GDPR Art.6 lawful basis logic
        """

        if self.purpose in [
            "vital_interest",
            "contract",
            "legal_obligation"
        ]:
            return False

        return True

    def __repr__(self):

        return (
            f"Context("
            f"purpose={self.purpose}, "
            f"legal_basis={self.legal_basis}, "
            f"data_category={self.data_category}, "
            f"data_subject_type={self.data_subject_type}, "
            f"processing_operation={self.processing_operation}, "
            f"retention_period={self.retention_period}, "
            f"processing_domain={self.processing_domain}, "
            f"third_party={self.has_third_party_recipients}, "
            f"international_transfer={self.international_transfer}, "
            f"consent_status={self.consent_status}"
            f")"
        )