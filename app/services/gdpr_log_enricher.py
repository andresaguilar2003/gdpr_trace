from datetime import timedelta

from collections import defaultdict, Counter

from app.services.gdpr_event_annotator import GDPREventAnnotator
from app.services.activity_classifier import ActivityClassifier
from app.services.trace_context_inferer import GDPRContextNormalizer, TraceContextInferer

from app.models.gdpr_event import GDPREvent

from app.specifications.activity_gdpr_mapping import ACTIVITY_GDPR_PATTERNS
from app.specifications.event_position import EventPosition
from app.specifications.activity_types import ActivityType

import copy


class GDPRLogEnricher:

    IGNORE_ATTRS = {}

    def __init__(self):

        self.annotator = GDPREventAnnotator()
        self.last_activity_map = {}
        self.last_dataset_context = None

    # =====================================================
    # BUILD ACTIVITY PROFILES
    # =====================================================

    def _build_activity_profiles(self, traces):

        activity_attrs = defaultdict(Counter)
        activity_counter = Counter()

        for trace in traces:

            for event in trace.events:

                activity = event.name

                activity_counter[activity] += 1

                if not getattr(event, "attributes", None):
                    continue

                for k in event.attributes.keys():

                    activity_attrs[activity][k] += 1

        profiles = []

        for activity, attr_counter in activity_attrs.items():

            activity_total = activity_counter[activity]

            filtered = {

                attr: count
                for attr, count in attr_counter.items()
                if (count / activity_total) >= 0.5
            }

            if not filtered:
                filtered = dict(attr_counter.most_common(5))

            profiles.append({
                "name": activity,
                "example_attributes": filtered
            })

        return profiles

    # =====================================================
    # SORT GDPR RULES
    # =====================================================

    def _sort_rules(self, rules):

        return sorted(
            rules,
            key=lambda r: (
                r["position"].value,
                r.get("priority", 100)
            )
        )

    # =====================================================
    # CREATE GDPR EVENT
    # =====================================================

    def _create_gdpr_event(
        self,
        trace,
        event,
        gdpr_counter,
        rule
    ):

        return GDPREvent(

            event_id=f"{trace.trace_id}_gdpr_{gdpr_counter}",

            name=rule["event"],

            timestamp=event.timestamp,

            order=event.order,

            position=rule["position"],

            activity_type=ActivityType.GDPR_COMPLIANCE.name
        )

    # =====================================================
    # ENRICH LOG
    # =====================================================

    def enrich_log(self, traces, dataset_context=None):

        enriched_traces = []

        # =====================================================
        # 1️⃣ DATASET CONTEXT
        # =====================================================

        if dataset_context is None:
            dataset_context = TraceContextInferer.infer_dataset_context(
                traces
            )

        self.last_dataset_context = dataset_context

        strict_context = GDPRContextNormalizer.normalize(
            copy.deepcopy(dataset_context)
        )

        print("\n===== DATASET CONTEXT =====")
        print(dataset_context)

        dataset_context_text = (
            f"Domain: {dataset_context.processing_domain}. "
            f"Purpose: {dataset_context.purpose}. "
            f"Data category: {dataset_context.data_category}."
        )

        # =====================================================
        # 2️⃣ BUILD ACTIVITY PROFILES
        # =====================================================

        activity_profiles = self._build_activity_profiles(traces)

        # =====================================================
        # 3️⃣ ACTIVITY CLASSIFICATION
        # =====================================================

        activity_map = ActivityClassifier.classify(
            activity_profiles,
            dataset_context_text
        )
        self.last_activity_map = activity_map

        # =====================================================
        # 4️⃣ ENRICH EACH TRACE
        # =====================================================

        for trace in traces:

            first_event = trace.events[0]
            last_event = trace.events[-1]

            # -------------------------------------------------
            # CASE START
            # -------------------------------------------------

            case_start_event = GDPREvent(

                event_id=f"{trace.trace_id}_case_start",

                name="CASE_START",

                timestamp=first_event.timestamp - timedelta(milliseconds=1),

                order=-1,

                position=None,

                activity_type=ActivityType.CASE_START.name
            )

            # -------------------------------------------------
            # CASE END
            # -------------------------------------------------

            case_end_event = GDPREvent(

                event_id=f"{trace.trace_id}_case_end",

                name="CASE_END",

                timestamp=last_event.timestamp + timedelta(milliseconds=1),

                order=999999,

                position=None,

                activity_type=ActivityType.CASE_END.name
            )

            # -------------------------------------------------

            new_events = []

            gdpr_counter = 0

            events_with_boundaries = (
                [case_start_event]
                + trace.events
                + [case_end_event]
            )

            # =====================================================
            # PROCESS EVENTS
            # =====================================================

            for event in events_with_boundaries:

                event_name = event.name

                # -------------------------------------------------
                # SPECIAL EVENTS
                # -------------------------------------------------

                if event_name == "CASE_START":

                    activity_type = ActivityType.CASE_START
                    user_right_type = None

                elif event_name == "CASE_END":

                    activity_type = ActivityType.CASE_END
                    user_right_type = None

                else:

                    activity_info = activity_map.get(

                        event_name,

                        {
                            "activity_type": ActivityType.OTHER,
                            "user_right_type": None
                        }
                    )

                    activity_type = activity_info["activity_type"]

                    user_right_type = activity_info["user_right_type"]

                # -------------------------------------------------
                # ANNOTATION
                # -------------------------------------------------

                if event_name in ["CASE_START", "CASE_END"]:

                    annotated_event = event

                else:

                    annotated_event = self.annotator.annotate(
                        event,
                        activity_type
                    )

                # -------------------------------------------------
                # ENRICH METADATA
                # -------------------------------------------------

                annotated_event.original_name = event.name

                annotated_event.name = event.name

                annotated_event.activity_type = activity_type.name

                annotated_event.user_right_type = user_right_type

                # =====================================================
                # GDPR RULES
                # =====================================================

                rules = self._sort_rules(
                    ACTIVITY_GDPR_PATTERNS.get(
                        activity_type,
                        []
                    )
                )

                # =====================================================
                # BEFORE EVENTS
                # =====================================================

                before_rules = [

                    r for r in rules
                    if r["position"] == EventPosition.BEFORE
                ]

                for rule in before_rules:

                    if not rule["condition"](
                        strict_context,
                        annotated_event
                    ):
                        continue

                    gdpr_event = self._create_gdpr_event(
                        trace,
                        event,
                        gdpr_counter,
                        rule
                    )

                    new_events.append(gdpr_event)

                    gdpr_counter += 1

                # =====================================================
                # ORIGINAL EVENT
                # =====================================================

                new_events.append(annotated_event)

                # =====================================================
                # AFTER EVENTS
                # =====================================================

                after_rules = [

                    r for r in rules
                    if r["position"] == EventPosition.AFTER
                ]

                for rule in after_rules:

                    if not rule["condition"](
                        strict_context,
                        annotated_event
                    ):
                        continue

                    gdpr_event = self._create_gdpr_event(
                        trace,
                        event,
                        gdpr_counter,
                        rule
                    )

                    new_events.append(gdpr_event)

                    gdpr_counter += 1

            # =====================================================
            # FINAL SORT
            # =====================================================

            trace.events = new_events

            trace.sort_events()

            for i, e in enumerate(trace.events):

                e.order = i

            enriched_traces.append(trace)

        return enriched_traces
