import os
import pm4py
import xml.etree.ElementTree as ET
from collections import defaultdict

from app.services.trace_builder import build_traces_from_pm4py_log
from app.validation.ocl_engine import OCLEngine


BASE_DIR = "app/validation/data"


# =====================================================
# CONTEXT EXTRACTION
# =====================================================

def extract_log_context_from_xes(path):
    tree = ET.parse(path)
    root = tree.getroot()

    ns = {"xes": "http://www.xes-standard.org/"}

    context = {}

    for string in root.findall("xes:string", ns):
        key = string.get("key")
        value = string.get("value")
        context[key] = value

    return context


# =====================================================
# VALIDATION
# =====================================================

def load_and_validate(log_path):

    print("\n" + "=" * 70)
    print(f"📄 TEST FILE: {os.path.basename(log_path)}")
    print("=" * 70)

    log = pm4py.read_xes(log_path)

    if hasattr(log, "columns"):
        log = pm4py.convert_to_event_log(log)

    raw_ctx = extract_log_context_from_xes(log_path)
    traces = build_traces_from_pm4py_log(log)

    # Inject context
    for t in traces:
        t.context.legal_basis = raw_ctx.get("gdpr:legal_basis")
        t.context.data_category = raw_ctx.get("gdpr:data_category")
        t.context.retention_period = raw_ctx.get("gdpr:retention_period")
        t.context.has_third_party_recipients = raw_ctx.get("gdpr:has_third_party_recipients") == "true"
        t.context.international_transfer = raw_ctx.get("gdpr:international_transfer")

    # Mostrar contexto
    print("📌 Context:")
    print(f"   legal_basis: {raw_ctx.get('gdpr:legal_basis')}")
    print(f"   data_category: {raw_ctx.get('gdpr:data_category')}")
    print(f"   retention_period: {raw_ctx.get('gdpr:retention_period')}")
    print(f"   third_party: {raw_ctx.get('gdpr:has_third_party_recipients')}")
    print(f"   international_transfer: {raw_ctx.get('gdpr:international_transfer')}")

    engine = OCLEngine()
    errors = engine.validate_traces(traces)

    # =====================================================
    # RESULT OUTPUT
    # =====================================================

    # Si el diccionario de errores está completamente vacío, es un PASS directo
    if not errors:
        print("\n✅ RESULT: PASS")
        return True

    # Contadores globales del archivo actual
    total_violations = 0
    total_warnings = 0

    # Primero hacemos un barrido rápido para ver si hay ALGUNA violación en alguna traza.
    # Si solo hay warnings en todo el archivo, el archivo sigue siendo apto (PASS) con advertencias.
    has_any_violation = any(len(res.get("violations", [])) > 0 for res in errors.values())

    if has_any_violation:
        print("\n❌ RESULT: FAIL (Strict GDPR Violations Found)\n")
    else:
        print("\n⚠️ RESULT: PASS (With Warnings)\n")

    for trace_id, result in errors.items():
        violations = result.get("violations", [])
        warnings = result.get("warnings", [])

        # Si esta traza específica no tiene nada, saltamos
        if not violations and not warnings:
            continue

        print(f"🔎 Trace: {trace_id}")

        # 1. PROCESAR VIOLACIONES (CRÍTICAS)
        if violations:
            grouped_viols = defaultdict(list)
            for v in violations:
                grouped_viols[v["rule"]].append(v)

            print("   🔴 CRITICAL VIOLATIONS:")
            for rule, items in grouped_viols.items():
                print(f"      🚫 Rule: {rule} ({len(items)} violation(s))")
                for v in items:
                    msg = v.get("message", "")
                    event = v.get("event", "")
                    print(f"         → [{event}] {msg}")
            total_violations += len(violations)

        # 2. PROCESAR WARNINGS (NO CRÍTICOS)
        if warnings:
            grouped_warns = defaultdict(list)
            for w in warnings:
                grouped_warns[w["rule"]].append(w)

            print("   🟡 NON-CRITICAL WARNINGS:")
            for rule, items in grouped_warns.items():
                print(f"      ⚠️ Rule: {rule} ({len(items)} warning(s))")
                for w in items:
                    msg = w.get("message", "")
                    event = w.get("event", "")
                    print(f"         → [{event}] {msg}")
            total_warnings += len(warnings)
        
        print("-" * 40) # Separador por traza interesada

    print(f"\n📊 File Summary -> Violations: {total_violations} | Warnings: {total_warnings}")

    # El test global solo cuenta como fallido (False) si hubo violaciones estrictas del RGPD
    return not has_any_violation


# =====================================================
# RUN ALL TESTS
# =====================================================

def run_all_tests():

    total = 0
    passed = 0

    print("\n🚀 RUNNING ALL TESTS\n")

    for root, _, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".xes"):
                total += 1
                path = os.path.join(root, file)

                ok = load_and_validate(path)
                if ok:
                    passed += 1

    print("\n" + "=" * 70)
    print("📊 GLOBAL SUMMARY")
    print("=" * 70)
    print(f"Total tests: {total}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {total - passed}")
    print(f"Success %:   {round((passed/total)*100, 2) if total else 0}%")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()