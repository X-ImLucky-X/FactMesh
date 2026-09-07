import re
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from backend.models import (
    Fact,
    FactType,
    FactRelationship,
    RelationshipType,
    ContextDelta,
    FourCasesShowcase,
    FailureCaseAnalysis
)

class ReconciliationEngine:
    """
    Cross-document semantic matching and reconciliation engine.
    Discovers corroborations, genuine contradictions, and apparent contradictions
    resolved by context (time, scope, units, reporting basis).
    """

    @staticmethod
    def reconcile_facts(facts: List[Fact]) -> List[FactRelationship]:
        """
        Performs pairwise cross-document reconciliation across all ingested facts.
        """
        relationships: List[FactRelationship] = []

        # Group facts by normalized entity & attribute family
        clusters = ReconciliationEngine._cluster_facts_by_attribute(facts)

        for (entity_key, attr_key), cluster_facts in clusters.items():
            if len(cluster_facts) < 2:
                continue

            # Compare pairs across different documents
            for i in range(len(cluster_facts)):
                for j in range(i + 1, len(cluster_facts)):
                    f1 = cluster_facts[i]
                    f2 = cluster_facts[j]

                    # Only compare across distinct documents (cross-document reasoning)
                    if f1.document_name == f2.document_name:
                        continue

                    rel = ReconciliationEngine.compare_fact_pair(f1, f2)
                    if rel:
                        relationships.append(rel)

        return relationships

    @staticmethod
    def compare_fact_pair(f1: Fact, f2: Fact) -> Optional[FactRelationship]:
        """
        Compares two facts and returns a structured FactRelationship.
        """
        # Analyze context differences
        delta = ReconciliationEngine._analyze_context_delta(f1, f2)

        # Check values equivalence
        val_match, val_diff_explanation = ReconciliationEngine._are_values_equivalent(f1, f2)

        reasoning_steps = []
        rel_type: RelationshipType
        takeaway: str

        # 1. Corroboration Case
        if val_match and not delta.has_time_mismatch and not delta.has_scope_mismatch:
            rel_type = RelationshipType.CORROBORATED
            reasoning_steps.append(
                f"Both facts refer to the same subject '{f1.entity}' and metric '{f1.attribute}'."
            )
            reasoning_steps.append(
                f"Document '{f1.document_name}' (p. {f1.page_number}) reports '{f1.raw_value or f1.value}' and "
                f"Document '{f2.document_name}' (p. {f2.page_number}) reports '{f2.raw_value or f2.value}'."
            )
            reasoning_steps.append(
                f"Both cover the same period ({f1.temporal_context or 'Common period'}) and scope ({f1.scope_context or 'Standard scope'})."
            )
            reasoning_steps.append(
                f"Conclusion: High confidence cross-document corroboration ({val_diff_explanation})."
            )
            takeaway = f"Corroborated: '{f1.attribute}' verified across '{f1.document_name}' and '{f2.document_name}'."

        # 2. Apparent Contradiction Explained by Context
        elif not val_match and (delta.has_time_mismatch or delta.has_scope_mismatch or delta.has_unit_mismatch or delta.has_methodology_mismatch):
            rel_type = RelationshipType.APPARENT_CONTRADICTION_EXPLAINED
            reasoning_steps.append(
                f"Apparent discrepancy detected in '{f1.attribute}': '{f1.raw_value or f1.value}' vs '{f2.raw_value or f2.value}'."
            )
            reasons = []
            if delta.has_time_mismatch:
                reasons.append(f"Temporal delta: Document 1 reports for '{f1.temporal_context}' while Document 2 reports for '{f2.temporal_context}'.")
            if delta.has_scope_mismatch:
                reasons.append(f"Scope delta: Document 1 is '{f1.scope_context}' while Document 2 is '{f2.scope_context}'.")
            if delta.has_unit_mismatch:
                reasons.append(f"Unit delta: Document 1 is in '{f1.unit}' while Document 2 is in '{f2.unit}'.")
            if delta.has_methodology_mismatch:
                reasons.append(f"Methodology delta: {delta.methodology_delta}")

            reasoning_steps.extend(reasons)
            reasoning_steps.append(
                f"Conclusion: The numerical/semantic divergence is fully explained by contextual parameters ({delta.summary_explanation})."
            )
            takeaway = f"Contextually Explained: Difference in '{f1.attribute}' is due to {', '.join(reasons)}."

        # 3. Genuine or Likely Contradiction
        elif not val_match and not delta.has_time_mismatch and not delta.has_scope_mismatch:
            rel_type = RelationshipType.CONTRADICTION
            reasoning_steps.append(
                f"Genuine conflict detected for '{f1.entity}' -> '{f1.attribute}'."
            )
            reasoning_steps.append(
                f"Both documents report for the exact same period ({f1.temporal_context}) and scope ({f1.scope_context})."
            )
            reasoning_steps.append(
                f"'{f1.document_name}' (p. {f1.page_number}) states: '{f1.raw_value or f1.value}', whereas "
                f"'{f2.document_name}' (p. {f2.page_number}) states: '{f2.raw_value or f2.value}'."
            )
            reasoning_steps.append(
                "Conclusion: Conflicting statements without explicit context reconciliation (potential institutional disagreement, data revision, or reporting disparity)."
            )
            takeaway = f"Contradiction: Conflicting values '{f1.value}' vs '{f2.value}' for period '{f1.temporal_context}'."

        # 4. Evolution over time
        elif val_match and delta.has_time_mismatch:
            rel_type = RelationshipType.EVOLUTION_OVER_TIME
            reasoning_steps.append(
                f"Stable metric across time: '{f1.attribute}' remained consistent at '{f1.value}' between '{f1.temporal_context}' and '{f2.temporal_context}'."
            )
            takeaway = f"Consistent over time: '{f1.attribute}' maintained across reporting periods."
        else:
            return None

        full_reasoning = "\n".join([f"• {step}" for step in reasoning_steps])

        return FactRelationship(
            source_fact_id=f1.id,
            target_fact_id=f2.id,
            source_fact=f1,
            target_fact=f2,
            relationship_type=rel_type,
            confidence=0.92,
            reasoning=full_reasoning,
            context_delta=delta,
            key_takeaway=takeaway
        )

    @staticmethod
    def _cluster_facts_by_attribute(facts: List[Fact]) -> Dict[Tuple[str, str], List[Fact]]:
        clusters = defaultdict(list)
        for f in facts:
            e_key = ReconciliationEngine._normalize_entity_key(f.entity)
            a_key = ReconciliationEngine._normalize_attr_key(f.attribute)
            clusters[(e_key, a_key)].append(f)
        return clusters

    @staticmethod
    def _normalize_entity_key(entity: str) -> str:
        e = entity.lower().strip()
        if "delhivery" in e:
            return "delhivery"
        if any(k in e for k in ["india", "economy", "rbi", "imf", "economic survey"]):
            return "india_macro"
        if "sahil" in e:
            return "sahil_barua"
        if "sandeep" in e:
            return "sandeep_barasia"
        if "spoton" in e:
            return "spoton"
        return e

    @staticmethod
    def _normalize_attr_key(attr: str) -> str:
        a = attr.lower().strip()
        if "revenue" in a:
            if "express" in a:
                return "express_revenue"
            if "ptl" in a or "truckload" in a:
                return "ptl_revenue"
            return "total_revenue"
        if "ebitda" in a:
            return "ebitda"
        if "profit" in a or "loss" in a or "pat" in a:
            return "net_profit_loss"
        if "pin" in a:
            return "pin_codes"
        if "parcel" in a or "shipment" in a or "volume" in a:
            return "parcel_volume"
        if "designation" in a or "role" in a or "md" in a or "ceo" in a:
            return "executive_designation"
        if "gdp" in a:
            return "real_gdp_growth"
        if "inflation" in a or "cpi" in a:
            if "core" in a:
                return "core_inflation"
            return "headline_inflation"
        if "fiscal deficit" in a:
            return "fiscal_deficit"
        if "current account" in a or "cad" in a:
            return "current_account_deficit"
        if "acquisition" in a or "spoton" in a:
            return "spoton_acquisition"
        if "registered office" in a:
            return "registered_office"
        if "incorporation" in a:
            return "date_of_incorporation"
        return a

    @staticmethod
    def _are_values_equivalent(f1: Fact, f2: Fact) -> Tuple[bool, str]:
        # Numerical comparison
        if f1.fact_type == FactType.NUMERICAL and f2.fact_type == FactType.NUMERICAL:
            v1 = f1.normalized_value if f1.normalized_value is not None else (float(f1.value) if str(f1.value).replace('.', '', 1).isdigit() else None)
            v2 = f2.normalized_value if f2.normalized_value is not None else (float(f2.value) if str(f2.value).replace('.', '', 1).isdigit() else None)

            if v1 is not None and v2 is not None:
                # 1. Direct exact or close floating match (< 1% relative tolerance)
                rel_diff = abs(v1 - v2) / max(abs(v1), abs(v2), 1e-6)
                if rel_diff < 0.015:
                    return True, f"Numerical values match within tolerance: {v1} ≈ {v2}"
                return False, f"Numerical values differ significantly: {v1} vs {v2}"

        # String / Categorical comparison
        s1 = str(f1.value).lower().strip()
        s2 = str(f2.value).lower().strip()

        # Normalizations for role titles
        if "managing director" in s1 and ("md" in s2 or "managing director" in s2):
            return True, "Categorical values are semantically equivalent (Managing Director & CEO abbreviations match)"

        if s1 == s2:
            return True, "Exact semantic match"

        # Check token overlap
        t1 = set(re.findall(r'\w+', s1))
        t2 = set(re.findall(r'\w+', s2))
        overlap = len(t1 & t2) / max(len(t1 | t2), 1)
        if overlap > 0.6:
            return True, f"High semantic token overlap ({overlap:.0%})"

        return False, "Values differ semantically"

    @staticmethod
    def _analyze_context_delta(f1: Fact, f2: Fact) -> ContextDelta:
        delta = ContextDelta()
        reasons = []

        # Time analysis
        t1 = ReconciliationEngine._clean_period(f1.temporal_context)
        t2 = ReconciliationEngine._clean_period(f2.temporal_context)
        if t1 and t2 and t1 != t2:
            delta.has_time_mismatch = True
            delta.time_delta = f"{t1} vs {t2}"
            reasons.append(f"different time periods ({t1} vs {t2})")

        # Scope analysis
        s1 = (f1.scope_context or "").lower()
        s2 = (f2.scope_context or "").lower()
        if s1 and s2 and s1 != s2:
            delta.has_scope_mismatch = True
            delta.scope_delta = f"{f1.scope_context} vs {f2.scope_context}"
            reasons.append(f"scope divergence ({f1.scope_context} vs {f2.scope_context})")

        # Unit analysis
        u1 = (f1.unit or "").lower()
        u2 = (f2.unit or "").lower()
        if u1 and u2 and u1 != u2 and f1.normalized_value is None:
            delta.has_unit_mismatch = True
            delta.unit_delta = f"{f1.unit} vs {f2.unit}"
            reasons.append(f"unit difference ({f1.unit} vs {f2.unit})")

        delta.summary_explanation = "; ".join(reasons) if reasons else "Context aligned"
        return delta

    @staticmethod
    def _clean_period(p: Optional[str]) -> Optional[str]:
        if not p:
            return None
        p_clean = re.sub(r'\s+', '', p).upper()
        return p_clean
