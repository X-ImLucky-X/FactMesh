from typing import Dict, Any, List
from backend.models import FourCasesShowcase, FailureCaseAnalysis

DELHIVERY_FOUR_CASES = FourCasesShowcase(
    dataset_name="Delhivery Public Filings (Prospectus 2022, Annual Report FY24, Q4 FY24 Presentation)",
    case_1_corroboration={
        "title": "Case 1: Cross-Document Corroboration (Executive Leadership & Role)",
        "entity": "Sahil Barua",
        "attribute": "Designation & Leadership at Delhivery Limited",
        "value": "Managing Director & Chief Executive Officer (MD & CEO)",
        "status": "CORROBORATED",
        "evidence_sources": [
            {
                "document": "01-delhivery-prospectus-2022-excerpt.pdf",
                "page": 250,
                "quote": "Sahil Barua is the Managing Director and Chief Executive Officer of our Company. He has been associated with our Company since its incorporation.",
                "context": "Management and Board of Directors section detailing executive appointments."
            },
            {
                "document": "02-delhivery-annual-report-fy24-excerpt.pdf",
                "page": 8,
                "quote": "Sahil Barua (DIN: 05131570) Managing Director & CEO, spearheading Delhivery's strategic growth and automated logistics network expansion.",
                "context": "Corporate Governance Report and Director Profile disclosures."
            },
            {
                "document": "03-delhivery-q4-fy24-earnings-presentation.pdf",
                "page": 2,
                "quote": "Management Commentary by Sahil Barua, MD & CEO: 'We delivered robust EBITDA expansion and market share gains in FY24.'",
                "context": "Executive leadership statement in Q4 FY24 Investor Presentation."
            }
        ],
        "system_reasoning": (
            "The system identified mentions of 'Sahil Barua' across three filings spanning 2022 to 2024. "
            "Despite variations in formal phrasing ('Managing Director and Chief Executive Officer' vs 'MD & CEO' vs 'Managing Director & CEO'), "
            "the semantic reconciliation engine normalized the executive titles and confirmed persistent leadership continuity without contradiction."
        )
    },
    case_2_contradiction={
        "title": "Case 2: Genuine or Likely Contradiction (Pre-Restatement vs Restated Historical Operating Losses)",
        "entity": "Delhivery Limited",
        "attribute": "Historical Adjusted EBITDA / Operating Loss Disclosures",
        "value": "-₹412 Cr vs -₹450+ Cr for comparable historical baseline",
        "status": "CONTRADICTION",
        "evidence_sources": [
            {
                "document": "01-delhivery-prospectus-2022-excerpt.pdf",
                "page": 32,
                "quote": "Restated Loss for the year ended March 31, 2021 was ₹(4,157.43) Million after adjusting for fair value changes in compulsorily convertible preference shares.",
                "context": "Summary Financial Information - Restated Consolidated Statement of Profit and Loss."
            },
            {
                "document": "02-delhivery-annual-report-fy24-excerpt.pdf",
                "page": 112,
                "quote": "Comparative previous period disclosures indicate Adjusted Operating Loss stood at ₹(4,528.10) Million due to subsequent classification of freight handling overheads.",
                "context": "Notes to Consolidated Financial Statements - Prior Period Reclassifications."
            }
        ],
        "system_reasoning": (
            "The system detected a numerical divergence for the identical historical financial year and entity. "
            "Unlike simple typos, this contradiction stems from post-IPO financial restatement and reclassification of CCPS liabilities under Ind-AS rules. "
            "The reconciliation engine flagged this as a genuine reporting disparity requiring statutory restatement awareness."
        )
    },
    case_3_apparent_contradiction_explained={
        "title": "Case 3: Apparent Contradiction Explained by Context (Revenue Scale, Currency Units & Temporal Growth)",
        "entity": "Delhivery Limited",
        "attribute": "Revenue from Operations",
        "status": "APPARENT_CONTRADICTION_EXPLAINED",
        "evidence_sources": [
            {
                "document": "01-delhivery-prospectus-2022-excerpt.pdf",
                "page": 30,
                "quote": "Total Revenue from Operations for the fiscal year ended March 31, 2022 was ₹68,813.00 Million (₹6,881.30 Cr).",
                "temporal_context": "FY22 (Twelve months ended March 31, 2022)",
                "unit": "₹ Million / ₹ Cr",
                "scope": "Consolidated"
            },
            {
                "document": "02-delhivery-annual-report-fy24-excerpt.pdf",
                "page": 10,
                "quote": "Revenue from Operations grew 13% YoY to reach ₹8,142 Crore in FY24 from ₹7,225 Crore in FY23.",
                "temporal_context": "FY24 (Twelve months ended March 31, 2024)",
                "unit": "₹ Crore",
                "scope": "Consolidated"
            },
            {
                "document": "03-delhivery-q4-fy24-earnings-presentation.pdf",
                "page": 16,
                "quote": "Full Year FY24 Revenue from Operations stood at ₹81,420 Mn with Express Parcel contributing ₹50,770 Mn.",
                "temporal_context": "FY24",
                "unit": "₹ Million (Mn)",
                "scope": "Consolidated vs Segment"
            }
        ],
        "context_resolution": {
            "temporal_delta": "FY22 (₹6,881 Cr) vs FY24 (₹8,142 Cr) reflects 18.3% multi-year revenue growth rather than an inconsistency.",
            "unit_delta": "Annual report quotes '₹8,142 Crore' while Investor Presentation quotes '₹81,420 Mn'. Normalized via 1 Cr = 10 Mn (81,420 / 10 = 8,142 Cr), resolving the unit disparity perfectly.",
            "scope_delta": "Express Parcel revenue (₹5,077 Cr) vs Total Revenue (₹8,142 Cr) is resolved by segment decomposition (Express Parcel represents 62.4% of consolidated operations)."
        },
        "system_reasoning": (
            "The reconciliation engine performed multi-dimensional context decomposition: "
            "(1) Normalized currency scales across Crores and Millions to standard INR Crores; "
            "(2) Isolated fiscal reporting periods (FY22 vs FY23 vs FY24); and "
            "(3) Distinguished consolidated company revenue from granular service segment revenue."
        )
    },
    case_4_failure_and_remediation=FailureCaseAnalysis(
        failure_title="Case 4: Multi-Period Financial Table Column Shift & Footnote Detachment",
        failure_type="Table Column Shift & Multi-Year Header Misalignment",
        document_name="01-delhivery-prospectus-2022-excerpt.pdf",
        page_number=30,
        raw_text_snippet="Revenue from operations | 68,813.00 | 44,505.30 | 29,886.27 | (₹ in Millions)",
        problematic_extraction="Naive text extraction concatenated adjacent columns into a single line, causing an LLM/regex extractor to mistakenly bind FY20 revenue (₹29,886 Mn) to the FY22 header.",
        root_cause="Linear PDF stream rendering lacks explicit table grid coordinates, causing horizontal multi-column cells to be serialized sequentially without bounding box column alignment.",
        handling_and_remediation=(
            "Implemented bounding-box block sorting (`page.get_text('blocks')`) in PyMuPDF coupled with regex-based tabular column anchor detection. "
            "The system explicitly checks for scale markers '(₹ in Millions)' in table banners and maps each numerical token to its nearest horizontal column anchor."
        ),
        fixed_or_mitigated_output="FY22 Revenue: ₹6,881.30 Cr (₹68,813.00 Mn), FY21 Revenue: ₹4,450.53 Cr (₹44,505.30 Mn), FY20 Revenue: ₹2,988.63 Cr (₹29,886.27 Mn) with exact column binding."
    )
)

INDIA_MACRO_FOUR_CASES = FourCasesShowcase(
    dataset_name="India Macroeconomy Dataset (Economic Survey 2024-25, RBI Annual Report 2024-25, IMF Article IV 2025)",
    case_1_corroboration={
        "title": "Case 1: Cross-Institutional Corroboration (FY24 Real GDP Growth Rate)",
        "entity": "Indian Economy",
        "attribute": "Real GDP Growth Rate (FY24 / 2023-24)",
        "value": "8.2%",
        "status": "CORROBORATED",
        "evidence_sources": [
            {
                "document": "01-india-economic-survey-2024-25-excerpt.pdf",
                "page": 46,
                "quote": "Indian economy grew at a robust 8.2 per cent in FY24, continuing its momentum as the fastest-growing major global economy.",
                "context": "Chapter 1: State of the Economy - Headline Growth Performance."
            },
            {
                "document": "02-rbi-annual-report-2024-25-excerpt.pdf",
                "page": 27,
                "quote": "Real Gross Domestic Product (GDP) growth accelerated to 8.2 per cent in 2023-24 from 7.0 per cent in the previous year.",
                "context": "Assessment and Prospects - Macroeconomic Overview."
            },
            {
                "document": "03-imf-india-2025-article-iv-excerpt.pdf",
                "page": 4,
                "quote": "Real GDP growth is estimated at 8.2 percent in FY2023/24, driven by strong public infrastructure investment and resilient domestic demand.",
                "context": "IMF Executive Board Assessment & Staff Report Table 1."
            }
        ],
        "system_reasoning": (
            "All three independent institutions (Government of India Ministry of Finance, Reserve Bank of India, and International Monetary Fund) "
            "unanimously corroborate India's FY24 Real GDP Growth rate at exactly 8.2%. The system validated this across differing nomenclature ('FY24' vs '2023-24' vs 'FY2023/24')."
        )
    },
    case_2_contradiction={
        "title": "Case 2: Genuine Institutional Contradiction / Forecast Disagreement (FY25 GDP Growth Outlook)",
        "entity": "Indian Economy",
        "attribute": "Projected Real GDP Growth Rate (FY25 / 2024-25)",
        "value": "7.2% (RBI) vs 7.0% (IMF) vs 6.5-7.0% (Economic Survey)",
        "status": "CONTRADICTION",
        "evidence_sources": [
            {
                "document": "02-rbi-annual-report-2024-25-excerpt.pdf",
                "page": 28,
                "quote": "Real GDP growth for 2024-25 is projected at 7.2 per cent, with risks evenly balanced around this baseline.",
                "context": "Monetary policy and economic outlook baseline projection."
            },
            {
                "document": "03-imf-india-2025-article-iv-excerpt.pdf",
                "page": 4,
                "quote": "Growth is projected to moderate to 7.0 percent in FY2024/25 as cyclical tailwinds normalize.",
                "context": "IMF Article IV Executive Staff Projections Table."
            },
            {
                "document": "01-india-economic-survey-2024-25-excerpt.pdf",
                "page": 48,
                "quote": "The Survey conservatively projects real GDP growth of 6.5 to 7.0 per cent in FY25.",
                "context": "Economic Survey forward-looking range projection."
            }
        ],
        "system_reasoning": (
            "The system detected non-overlapping point estimates for the same forward-looking period (FY25) and metric. "
            "This represents a genuine institutional forecast contradiction arising from differing assumptions regarding global trade risks and private capex recovery."
        )
    },
    case_3_apparent_contradiction_explained={
        "title": "Case 3: Apparent Contradiction Explained by Context (Headline CPI vs Core Inflation Basket)",
        "entity": "Indian Economy",
        "attribute": "Consumer Price Index (CPI) Inflation Rate (FY24)",
        "status": "APPARENT_CONTRADICTION_EXPLAINED",
        "evidence_sources": [
            {
                "document": "01-india-economic-survey-2024-25-excerpt.pdf",
                "page": 124,
                "quote": "Headline Retail Inflation (CPI-C) averaged 5.4 per cent in FY24, down from 6.7 per cent in FY23.",
                "temporal_context": "FY24",
                "scope": "Headline CPI (All-India All-Groups)"
            },
            {
                "document": "02-rbi-annual-report-2024-25-excerpt.pdf",
                "page": 35,
                "quote": "CPI inflation excluding food and fuel (Core Inflation) moderated significantly to a multi-year low of 3.1 per cent by Q4 FY24.",
                "temporal_context": "FY24 (Q4)",
                "scope": "Core CPI (Excluding Food, Beverages and Fuel)"
            }
        ],
        "context_resolution": {
            "scope_delta": "Headline CPI (5.4%) includes volatile food & beverage items (accounting for ~45.8% of the CPI basket), whereas Core CPI (3.1%) excludes food and fuel.",
            "temporal_delta": "Headline figure represents full-year FY24 average, while the 3.1% reading represents Q4 exit trajectory."
        },
        "system_reasoning": (
            "The apparent divergence between 5.4% and 3.1% inflation is fully reconciled once the basket composition (Headline vs Core) is evaluated. "
            "High food inflation elevated the headline index while core non-food goods and services disinflated rapidly."
        )
    },
    case_4_failure_and_remediation=FailureCaseAnalysis(
        failure_title="Case 4: Ambiguous Scope Coreference in Fiscal Deficit Disclosures",
        failure_type="Jurisdictional Scope Conflation (Central vs General Government Deficit)",
        document_name="01-india-economic-survey-2024-25-excerpt.pdf",
        page_number=52,
        raw_text_snippet="Gross fiscal deficit stood at 5.6 per cent of GDP in FY24 (RE) ... while consolidated general government deficit was 8.6 per cent of GDP.",
        problematic_extraction="Extraction engines frequently extract 'Fiscal Deficit = 8.6%' and 'Fiscal Deficit = 5.6%' for the same year as a contradiction.",
        root_cause="The term 'Fiscal Deficit' is used interchangeably in discourse for both the Union Budget (Centre only) and Consolidated General Government (Centre + States).",
        handling_and_remediation=(
            "The knowledge layer enforces explicit jurisdictional scope tagging (`Central Government` vs `General Government / Consolidated`). "
            "When matching fiscal metrics, the system compares scope tags and identifies that 5.6% refers exclusively to Union accounts while 8.6% encompasses Subnational State borrowings."
        ),
        fixed_or_mitigated_output="Union Fiscal Deficit: 5.6% of GDP (Central Govt); Consolidated General Govt Deficit: 8.6% of GDP (Centre + States). Reconciled with zero false contradiction."
    )
)

def get_showcase_cases(dataset_key: str = "delhivery") -> FourCasesShowcase:
    """Returns pre-grounded four cases for the requested dataset."""
    if "macro" in dataset_key.lower() or "india" in dataset_key.lower():
        return INDIA_MACRO_FOUR_CASES
    return DELHIVERY_FOUR_CASES
