# OCL Rules Catalog

This document contains the standalone catalogue of OCL rules used to specify and validate GDPR-aware enrichment of event-log graphs. It isolates the rules from the experimental report and omits evaluation metrics, plots, and methodology details.

Each rule is documented with its identifier, GDPR article coverage, purpose, and OCL specification.

## 1. `AUTOMATED_DECISION_DISCLOSURE_REQUIRED`

- **GDPR articles:** Articles 13(2)(f) and 22 GDPR
- **Description:** Checks transparency or contestation evidence for automated decision-making and profiling.
- **OCL specification:**

```ocl
context Trace
inv AUTOMATED_DECISION_DISCLOSURE_REQUIRED:
    for all e where e.type = AUTOMATED_DECISION:
        exists g where
            g.name = automated_logic_disclosure AND
            g.position = BEFORE AND
            g.order < e.order
```

## 2. `CASE_END_ERASURE`

- **GDPR articles:** Articles 5(1)(e), 17, 19 and 25 GDPR
- **Description:** Checks that retention and erasure evidence is present when the data lifecycle requires deletion or cleanup.
- **OCL specification:**

```ocl
context Trace
inv CASE_END_ERASURE:
for all e in events where e.type = CASE_END:
if not context.retention_period.oclIsUndefined() then
exists g in events such that
g.name = 'confirm_data_erasure' AND
g.position = BEFORE AND
g.order < e.order
else
true
endif
```

## 3. `CASE_END_MISSING_RETENTION_CONTEXT`

- **GDPR articles:** Articles 5(1)(e), 17 and 25 GDPR
- **Description:** Checks retention-period evidence and end-of-case lifecycle controls.
- **OCL specification:**

```ocl
context Trace
inv CASE_END_MISSING_RETENTION_CONTEXT:
    for all e where e.type = CASE_END:
        context.retention_period is not undefined
```

## 4. `CASE_END_RETENTION_VERIFY`

- **GDPR articles:** Articles 5(1)(e), 17 and 25 GDPR
- **Description:** Checks retention-period evidence and end-of-case lifecycle controls.
- **OCL specification:**

```ocl
context Trace
inv CASE_END_RETENTION_VERIFY:
for all e in events where e.type = CASE_END:
exists g in events such that
g.name = 'retention_period_verify' AND
g.position = BEFORE AND
g.order < e.order
```

## 5. `CASE_START_VERIFY_LEGAL_BASIS`

- **GDPR articles:** Articles 5 and 6 GDPR
- **Description:** Checks that the processing flow contains explicit evidence of a lawful basis before or immediately after the relevant processing point.
- **OCL specification:**

```ocl
context Trace
inv CASE_START_VERIFY_LEGAL_BASIS:
for all e in events where e.type = CASE_START:
exists g in events such that
g.name = verify_legal_basis AND
g.position = AFTER AND
g.order > e.order
```

## 6. `CASE_START_VERIFY_LEGAL_BASIS_DUPLICATED`

- **GDPR articles:** Articles 5 and 6 GDPR
- **Description:** Ensures that compliance evidence is not duplicated in a way that would distort the audit trail.
- **OCL specification:**

```ocl
context Trace
inv CASE_START_VERIFY_LEGAL_BASIS_DUPLICATED:
    for all e where e.type = CASE_START:
        events where name = CASE_START count <= 1
```

## 7. `DATA_ACCESS_CONTROL_DUPLICATED`

- **GDPR articles:** Article 32 GDPR
- **Description:** Ensures that compliance evidence is not duplicated in a way that would distort the audit trail.
- **OCL specification:**

```ocl
context Trace
inv DATA_ACCESS_CONTROL_DUPLICATED:
    for all e where e.type = DATA_ACCESS:
        events where name = access_control_check count <= 1
```

## 8. `DATA_ACCESS_CONTROL_FORBIDDEN`

- **GDPR articles:** Article 32 GDPR
- **Description:** Prevents unnecessary or contextually invalid GDPR evidence from being inserted when the selected context does not activate the obligation.
- **OCL specification:**

```ocl
context Trace
inv DATA_ACCESS_CONTROL_FORBIDDEN:
if data_category not in {HEALTH, SPECIAL}:
not exists g where g.name = access_control_check
```

## 9. `DATA_ACCESS_CONTROL_REQUIRED`

- **GDPR articles:** Article 32 GDPR
- **Description:** Checks access-control evidence for activities involving sensitive or protected data.
- **OCL specification:**

```ocl
context Trace
inv DATA_ACCESS_CONTROL_REQUIRED:
if data_category in {HEALTH, SPECIAL}:
exists g where
g.name = access_control_check AND
g.position = BEFORE AND
g.order  e.order
```

## 10. `DATA_COLLECTION_CONSENT_FORBIDDEN`

- **GDPR articles:** Articles 6 and 7 GDPR
- **Description:** Prevents unnecessary or contextually invalid GDPR evidence from being inserted when the selected context does not activate the obligation.
- **OCL specification:**

```ocl
context Trace
inv DATA_COLLECTION_CONSENT_FORBIDDEN:
if legal_basis != consent:
not exists g where g.name = check_consent
```

## 11. `DATA_COLLECTION_CONSENT_REQUIRED`

- **GDPR articles:** Articles 6 and 7 GDPR
- **Description:** Checks whether consent evidence is present or absent according to the selected legal basis.
- **OCL specification:**

```ocl
context Trace
inv DATA_COLLECTION_CONSENT_REQUIRED:
if legal_basis = consent:
exists g where
g.name = check_consent AND
g.position = BEFORE AND
g.order  e.order
```

## 12. `DATA_COLLECTION_LEGAL_BASIS_FLOW`

- **GDPR articles:** Articles 5 and 6 GDPR
- **Description:** Checks that the processing flow contains explicit evidence of a lawful basis before or immediately after the relevant processing point.
- **OCL specification:**

```ocl
context Trace
inv DATA_COLLECTION_LEGAL_BASIS_FLOW:
    for all e where e.type = CASE_START:
        exists g where
            g.name = CASE_START AND
            g.position = BEFORE AND
            g.order < e.order
```

## 13. `DATA_COLLECTION_NOTICE`

- **GDPR articles:** Articles 12, 13 and 14 GDPR
- **Description:** Checks that the data subject receives privacy-information evidence associated with data collection.
- **OCL specification:**

```ocl
context Trace
inv DATA_COLLECTION_NOTICE:
for all e where e.type = DATA_COLLECTION:
exists g where
g.name = privacy_notice_disclosed AND
g.position = AFTER AND
g.order >= e.order
```

## 14. `DATA_COLLECTION_PURPOSE_REQUIRED`

- **GDPR articles:** Articles 5(1)(b) and 30 GDPR
- **Description:** Checks that the processing purpose is recorded as explicit accountability evidence.
- **OCL specification:**

```ocl
context Trace
inv DATA_COLLECTION_PURPOSE_REQUIRED:
    for all e where e.type = CASE_START:
        exists g where
            g.name = CASE_START AND
            g.position = BEFORE AND
            g.order < e.order
```

## 15. `DATA_DELETION_ERASE_REQUIRED`

- **GDPR articles:** Articles 5(1)(e), 17, 19 and 25 GDPR
- **Description:** Checks that retention and erasure evidence is present when the data lifecycle requires deletion or cleanup.
- **OCL specification:**

```ocl
context Trace
inv DATA_DELETION_ERASE_REQUIRED:
    for all e where e.type = DATA_DELETION:
        exists g where
            g.name = erase_data AND
            g.position = BEFORE AND
            g.order < e.order
```

## 16. `DATA_DELETION_RETENTION_REQUIRED`

- **GDPR articles:** Articles 5(1)(e), 17, 19 and 25 GDPR
- **Description:** Checks that retention and erasure evidence is present when the data lifecycle requires deletion or cleanup.
- **OCL specification:**

```ocl
context Trace
inv DATA_DELETION_RETENTION_REQUIRED:
    for all e where e.type = DATA_DELETION:
        exists g where
            g.name = erase_data AND
            g.position = BEFORE AND
            g.order < e.order
```

## 17. `DATA_PROCESSING_ENCRYPTION_FORBIDDEN`

- **GDPR articles:** Article 32 GDPR
- **Description:** Prevents unnecessary or contextually invalid GDPR evidence from being inserted when the selected context does not activate the obligation.
- **OCL specification:**

```ocl
context Trace
inv DATA_PROCESSING_ENCRYPTION_FORBIDDEN:
if data_category = STANDARD:
not exists g where g.name = encryption_applied
```

## 18. `MERGED_DATA_PROCESSING_CA04E1F9`

- **GDPR articles:** General GDPR accountability and compliance principles
- **Description:** Consolidated invariant covering the following source rules: DATA_PROCESSING_ENCRYPTION_REQUIRED, DATA_PROCESSING_LOG_REQUIRED.
- **OCL specification:**

```ocl
context Trace
inv MERGED_DATA_PROCESSING_CA04E1F9:
    -- Refactors: DATA_PROCESSING_ENCRYPTION_REQUIRED, DATA_PROCESSING_LOG_REQUIRED
    for all e where e.type belongs_to DATA_PROCESSING:
        required controls {encryption_applied, log_processing_activity} satisfy configured BEFORE/AFTER ordering
```

## 19. `DATA_PROCESSING_MINIMISATION`

- **GDPR articles:** Article 5(1)(c) GDPR
- **Description:** Checks that minimisation evidence is available before processing personal or sensitive data.
- **OCL specification:**

```ocl
context Trace
inv DATA_PROCESSING_MINIMISATION:
for all e where e.type = DATA_PROCESSING:
exists g where
g.name = minimisation_check AND
g.position = BEFORE AND
g.order  e.order
```

## 20. `DATA_TRANSFER_INTERNATIONAL_FORBIDDEN`

- **GDPR articles:** Articles 28 and 44-49 GDPR
- **Description:** Prevents unnecessary or contextually invalid GDPR evidence from being inserted when the selected context does not activate the obligation.
- **OCL specification:**

```ocl
context Trace
inv DATA_TRANSFER_INTERNATIONAL_FORBIDDEN:
if international_transfer != "third_country":
not exists g where g.name = verify_international_safeguard
```

## 21. `MERGED_DATA_TRANSFER_4F69B250`

- **GDPR articles:** Articles 28 and 44-49 GDPR
- **Description:** Consolidated invariant covering the following source rules: DATA_TRANSFER_INTERNATIONAL_REQUIRED, DATA_TRANSFER_THIRD_PARTY_REQUIRED.
- **OCL specification:**

```ocl
context Trace
inv MERGED_DATA_TRANSFER_4F69B250:
    -- Refactors: DATA_TRANSFER_INTERNATIONAL_REQUIRED, DATA_TRANSFER_THIRD_PARTY_REQUIRED
    for all e where e.type belongs_to DATA_TRANSFER:
        required controls {check_third_party_agreement} satisfy configured BEFORE/AFTER ordering
```

## 22. `DATA_TRANSFER_THIRD_PARTY_FORBIDDEN`

- **GDPR articles:** Articles 28 and 44-49 GDPR
- **Description:** Prevents unnecessary or contextually invalid GDPR evidence from being inserted when the selected context does not activate the obligation.
- **OCL specification:**

```ocl
context Trace
inv DATA_TRANSFER_THIRD_PARTY_FORBIDDEN:
if has_third_party_recipients = false:
not exists g where g.name = check_third_party_agreement
```

## 23. `MERGED_USER_RIGHT_F8788A46`

- **GDPR articles:** Articles 12-23 GDPR
- **Description:** Consolidated invariant covering the following source rules: USER_RIGHT_ACCESS_COMPLIANCE, USER_RIGHT_AUTOMATED_DECISION_REVIEW_COMPLIANCE, USER_RIGHT_IDENTITY_VERIFICATION, USER_RIGHT_INFORMATION_COMPLIANCE, USER_RIGHT_OBJECTION_COMPLIANCE, USER_RIGHT_PORTABILITY_COMPLIANCE.
- **OCL specification:**

```ocl
context Trace
inv MERGED_USER_RIGHT_F8788A46:
    -- Refactors: USER_RIGHT_ACCESS_COMPLIANCE, USER_RIGHT_AUTOMATED_DECISION_REVIEW_COMPLIANCE, USER_RIGHT_IDENTITY_VERIFICATION, USER_RIGHT_INFORMATION_COMPLIANCE, USER_RIGHT_OBJECTION_COMPLIANCE, USER_RIGHT_PORTABILITY_COMPLIANCE
    for all e where e.type belongs_to USER_RIGHT:
        required controls {contest_automated_decision, generate_interoperable_format, halt_processing_activities, provide_data_copy, provide_transparency_details, respond_user_right} satisfy configured BEFORE/AFTER ordering
```

## 24. `MERGED_USER_RIGHT_1BC41317`

- **GDPR articles:** Articles 12-23 GDPR
- **Description:** Consolidated invariant covering the following source rules: USER_RIGHT_ACCESS_DATA_COPY, USER_RIGHT_AUTOMATED_DECISION_CONTEST, USER_RIGHT_ERASURE_COMPLIANCE, USER_RIGHT_INFORMATION_TRANSPARENCY, USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION, USER_RIGHT_OBJECTION_HALT, USER_RIGHT_PORTABILITY_FORMAT, USER_RIGHT_PORTABILITY_TRANSMISSION, USER_RIGHT_RECTIFICATION_COMPLIANCE, USER_RIGHT_RESTRICTION_COMPLIANCE.
- **OCL specification:**

```ocl
context Trace
inv MERGED_USER_RIGHT_1BC41317:
    -- Refactors: USER_RIGHT_ACCESS_DATA_COPY, USER_RIGHT_AUTOMATED_DECISION_CONTEST, USER_RIGHT_ERASURE_COMPLIANCE, USER_RIGHT_INFORMATION_TRANSPARENCY, USER_RIGHT_OBJECTION_GROUNDS_VERIFICATION, USER_RIGHT_OBJECTION_HALT, USER_RIGHT_PORTABILITY_FORMAT, USER_RIGHT_PORTABILITY_TRANSMISSION, USER_RIGHT_RECTIFICATION_COMPLIANCE, USER_RIGHT_RESTRICTION_COMPLIANCE
    for all e where e.type belongs_to USER_RIGHT:
        required controls {contest_automated_decision, erase_primary_record, generate_interoperable_format, halt_processing_activities, notify_data_rectification_to_recipients, notify_third_party_deletion, propagate_erasure_to_replicas, propagate_rectification_to_replicas, provide_data_copy, provide_transparency_details, respond_user_right, update_primary_record, verify_compelling_legitimate_grounds, verify_erasure_completion, verify_rectification_consistency, verify_request_identity} satisfy configured BEFORE/AFTER ordering
```

## 25. `USER_RIGHT_REQUEST_RESPONSE_REQUIRED`

- **GDPR articles:** Articles 12-23 GDPR
- **Description:** Checks that data-subject-right requests are handled with the required identity, response and execution evidence.
- **OCL specification:**

```ocl
context Trace
inv USER_RIGHT_REQUEST_RESPONSE_REQUIRED:
    for all e where e.type = USER_RIGHT_REQUEST:
        exists g where
            g.name = respond_user_right AND
            g.position = BEFORE AND
            g.order < e.order
```

## 26. `DATA_BREACH_NOTIFICATION_REQUIRED`

- **GDPR articles:** Articles 33 and 34 GDPR
- **Description:** No explicit rule covers GDPR Articles 33 and 34 breach notification timelines.
- **OCL specification:**

```ocl
context Trace
inv DATA_BREACH_NOTIFICATION_REQUIRED:
    for all e where e.name = detect_personal_data_breach:
        exists g where g.name = notify_supervisory_authority AND g.order > e.order
```

## 27. `CONSENT_WITHDRAWAL_STOP_PROCESSING`

- **GDPR articles:** Articles 6 and 7 GDPR
- **Description:** Consent withdrawal is not explicitly connected to halting subsequent processing.
- **OCL specification:**

```ocl
context Trace
inv CONSENT_WITHDRAWAL_STOP_PROCESSING:
    for all e where e.name = withdraw_consent:
        not exists p where p.type = DATA_PROCESSING AND p.order > e.order
```

## 28. `DPIA_HIGH_RISK_PROCESSING_REQUIRED`

- **GDPR articles:** Article 35 GDPR
- **Description:** High-risk or special-category processing should be linked to a DPIA evidence event.
- **OCL specification:**

```ocl
context Trace
inv DPIA_HIGH_RISK_PROCESSING_REQUIRED:
    if context.data_category in {SPECIAL, HEALTH}:
        exists g where g.name = perform_dpia AND g.order < first(DATA_PROCESSING).order
```
