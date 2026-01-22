from gdpr.validators.validators import validate_trace
from gdpr.remediation import apply_recommendations
from gdpr.recommendations import generate_recommendations

def test_remediation_reduces_violations(non_compliant_trace):
    violations_before = validate_trace(non_compliant_trace)
    recs = generate_recommendations(violations_before)

    remediated = apply_recommendations(non_compliant_trace, recs)
    violations_after = validate_trace(remediated)

    print("\nViolaciones antes:", len(violations_before))
    print("Violaciones después:", len(violations_after))

    assert len(violations_after) <= len(violations_before)
