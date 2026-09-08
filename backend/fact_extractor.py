import re
import json
import uuid
import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from backend.models import Fact, Evidence, FactType
from backend.ingestion import DocumentParser
from backend import config

class FactExtractor:
    """
    Hybrid Fact Extraction Engine:
    Combines high-precision local semantic & numerical extraction with
    optional cloud LLM (Gemini/OpenAI) structured fact parsing.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config.DEFAULT_PROVIDER

    def extract_facts_from_document(self, doc_data: Dict[str, Any]) -> List[Fact]:
        """
        Extracts facts from all pages of a parsed document.
        """
        metadata = doc_data["metadata"]
        pages = doc_data["pages"]
        doc_name = metadata.filename
        facts: List[Fact] = []

        for page in pages:
            page_facts = self.extract_facts_from_page(
                doc_name,
                page["page_number"],
                page["text"],
                tables=page.get("tables", [])
            )
            facts.extend(page_facts)

        # De-duplicate near-identical facts on the same page
        unique_facts = self._deduplicate_facts(facts)
        return unique_facts

    def extract_facts_from_page(self, doc_name: str, page_num: int, text: str, tables: Optional[List[Any]] = None) -> List[Fact]:
        """
        Extracts semantic and numerical facts from a single page.
        """
        facts: List[Fact] = []
        if not text or len(text.strip()) < 10:
            if tables:
                facts.extend(self._extract_facts_from_tables(doc_name, page_num, tables, text or ""))
            return facts

        # Clean text while retaining structure
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # 1. Extract Financial / Numerical Metrics with Period & Currency
        facts.extend(self._extract_financial_metrics(doc_name, page_num, text))

        # 2. Extract Macroeconomic Metrics (GDP, Inflation, Deficit, etc.)
        facts.extend(self._extract_macro_metrics(doc_name, page_num, text))

        # 3. Extract Operational Metrics (PIN codes, Hubs, Volumes, Counts)
        facts.extend(self._extract_operational_metrics(doc_name, page_num, text))

        # 4. Extract Governance, Roles & Personnel Facts
        facts.extend(self._extract_governance_facts(doc_name, page_num, text))

        # 5. Extract Corporate Transactions & Acquisitions
        facts.extend(self._extract_corporate_facts(doc_name, page_num, text))

        # 6. Extract Structured Facts from Tables
        if tables:
            facts.extend(self._extract_facts_from_tables(doc_name, page_num, tables, text))

        return facts

    def _extract_financial_metrics(self, doc_name: str, page_num: int, text: str) -> List[Fact]:
        facts = []

        # Patterns for Revenue, EBITDA, Loss/Profit, Capex
        patterns = [
            # Revenue / Revenue from operations
            (
                r'(revenue(?:\s+from\s+operations)?|total\s+revenue|total\s+income|consolidated\s+revenue)\s*(?:of|was|is|reached|amounted\s+to|stood\s+at)?\s*[:\-\s]*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr(?:ore)?|Million|Billion|Lakh)?\s*(?:in\s+)?(FY\s*\d{2,4}|Q[1-4]\s*FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b)?',
                "Revenue from Operations",
                "₹ Cr",
                "Consolidated"
            ),
            # Adjusted EBITDA / EBITDA
            (
                r'(adjusted\s+ebitda|ebitda)\s*(?:of|was|is|reached|stood\s+at)?\s*[:\-\s]*(?:₹|Rs\.?|INR)?\s*([\d,\-]+(?:\.\d+)?)\s*(Cr(?:ore)?|Million|Billion|Lakh|%)?\s*(?:in\s+)?(FY\s*\d{2,4}|Q[1-4]\s*FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b)?',
                "Adjusted EBITDA",
                "₹ Cr",
                "Consolidated"
            ),
            # Net Profit / Loss after tax (PAT)
            (
                r'(net\s+(?:loss|profit)|profit\s+after\s+tax|loss\s+after\s+tax|pat)\s*(?:of|was|is|stood\s+at)?\s*[:\-\s]*(?:₹|Rs\.?|INR)?\s*([\d,\-]+(?:\.\d+)?)\s*(Cr(?:ore)?|Million|Billion|Lakh)?\s*(?:in\s+)?(FY\s*\d{2,4}|Q[1-4]\s*FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b)?',
                "Net Profit / Loss After Tax",
                "₹ Cr",
                "Consolidated"
            ),
            # Express parcel revenue
            (
                r'(express\s+parcel\s+revenue|express\s+parcel\s+services)\s*(?:of|was|is|reached|stood\s+at)?\s*[:\-\s]*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr(?:ore)?|Million|Billion|Lakh)?\s*(?:in\s+)?(FY\s*\d{2,4}|Q[1-4]\s*FY\s*\d{2,4})?',
                "Express Parcel Revenue",
                "₹ Cr",
                "Express Parcel Segment"
            ),
            # Part truckload (PTL) revenue
            (
                r'(part\s+truckload|ptl\s+freight|ptl\s+revenue)\s*(?:of|was|is|reached|stood\s+at)?\s*[:\-\s]*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d+)?)\s*(Cr(?:ore)?|Million|Billion|Lakh)?\s*(?:in\s+)?(FY\s*\d{2,4}|Q[1-4]\s*FY\s*\d{2,4})?',
                "Part Truckload (PTL) Revenue",
                "₹ Cr",
                "PTL Segment"
            )
        ]

        # Scan text for patterns
        for pattern, default_attr, default_unit, default_scope in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                metric_name_raw = match.group(1).strip()
                val_str = match.group(2).replace(",", "").strip()
                unit_str = match.group(3) or default_unit
                period_str = match.group(4) or self._detect_period_in_context(text, match.start())

                try:
                    num_val = float(val_str)
                except ValueError:
                    continue

                # Standardize entity
                entity = self._detect_entity_name(doc_name, text)

                # Get verbatim sentence/line
                quote = self._extract_matching_sentence(text, match.start(), match.end())
                context = DocumentParser.extract_context_window(text, quote)

                # Standardize units
                std_unit, norm_val = self._normalize_currency_units(num_val, unit_str)

                facts.append(Fact(
                    document_name=doc_name,
                    page_number=page_num,
                    entity=entity,
                    attribute=default_attr,
                    value=num_val,
                    raw_value=f"{match.group(2)} {unit_str}".strip(),
                    unit=std_unit,
                    temporal_context=period_str or "Unspecified Period",
                    scope_context=default_scope,
                    fact_type=FactType.NUMERICAL,
                    confidence=0.92,
                    normalized_value=norm_val,
                    evidence=Evidence(
                        document_name=doc_name,
                        page_number=page_num,
                        verbatim_quote=quote,
                        context_window=context,
                        char_offset=match.start()
                    )
                ))

        return facts

    def _extract_macro_metrics(self, doc_name: str, page_num: int, text: str) -> List[Fact]:
        facts = []

        macro_patterns = [
            # Real GDP Growth
            (
                r'(real\s+gdp|gdp\s+growth|gross\s+domestic\s+product\s+growth)\s*(?:is\s+estimated\s+at|is\s+projected\s+at|grew\s+by|of|at|was|stood\s+at)?\s*[:\-\s]*([\d\.]+)\s*(%|percent)\s*(?:in\s+)?(FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b|\b202[45]\b)?',
                "Real GDP Growth Rate",
                "%",
                "National Accounts"
            ),
            # Headline CPI Inflation / Inflation
            (
                r'(headline\s+cpi\s+inflation|cpi\s+inflation|consumer\s+price\s+inflation|headline\s+inflation)\s*(?:of|was|is|stood\s+at|averaged|moderated\s+to)?\s*[:\-\s]*([\d\.]+)\s*(%|percent)\s*(?:in\s+)?(FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b|\b202[45]\b)?',
                "Headline CPI Inflation Rate",
                "%",
                "Headline (All-India)"
            ),
            # Core Inflation
            (
                r'(core\s+cpi\s+inflation|core\s+inflation)\s*(?:of|was|is|stood\s+at|averaged|moderated\s+to)?\s*[:\-\s]*([\d\.]+)\s*(%|percent)\s*(?:in\s+)?(FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b|\b202[45]\b)?',
                "Core CPI Inflation Rate",
                "%",
                "Core (Excluding Food and Fuel)"
            ),
            # Fiscal Deficit
            (
                r'(fiscal\s+deficit|gross\s+fiscal\s+deficit)\s*(?:of|was|is|stood\s+at|budgeted\s+at|targeted\s+at)?\s*[:\-\s]*([\d\.]+)\s*(%|percent)\s*(?:of\s+gdp)?\s*(?:in\s+)?(FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b|\b202[45]\b)?',
                "Fiscal Deficit (% of GDP)",
                "% of GDP",
                "General/Central Government"
            ),
            # Current Account Deficit (CAD)
            (
                r'(current\s+account\s+deficit|cad)\s*(?:of|was|is|stood\s+at|moderated\s+to)?\s*[:\-\s]*([\d\.]+)\s*(%|percent)\s*(?:of\s+gdp)?\s*(?:in\s+)?(FY\s*\d{2,4}|\b202[0-9]-2[0-9]\b|\b202[45]\b)?',
                "Current Account Deficit (% of GDP)",
                "% of GDP",
                "External Sector"
            )
        ]

        for pattern, default_attr, default_unit, default_scope in macro_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                val_str = match.group(2).strip()
                unit_str = match.group(3) or default_unit
                period_str = match.group(4) or self._detect_period_in_context(text, match.start())

                try:
                    num_val = float(val_str)
                except ValueError:
                    continue

                entity = "Indian Economy"
                quote = self._extract_matching_sentence(text, match.start(), match.end())
                context = DocumentParser.extract_context_window(text, quote)

                # Scope refinement (Central vs General govt, Core vs Headline)
                scope = default_scope
                if "general government" in context.lower():
                    scope = "General Government (Centre + States)"
                elif "centre" in context.lower() or "central government" in context.lower():
                    scope = "Central Government"

                facts.append(Fact(
                    document_name=doc_name,
                    page_number=page_num,
                    entity=entity,
                    attribute=default_attr,
                    value=num_val,
                    raw_value=f"{val_str}%",
                    unit=default_unit,
                    temporal_context=period_str or "2024-25",
                    scope_context=scope,
                    fact_type=FactType.NUMERICAL,
                    confidence=0.94,
                    normalized_value=num_val,
                    evidence=Evidence(
                        document_name=doc_name,
                        page_number=page_num,
                        verbatim_quote=quote,
                        context_window=context,
                        char_offset=match.start()
                    )
                ))

        return facts

    def _extract_operational_metrics(self, doc_name: str, page_num: int, text: str) -> List[Fact]:
        facts = []

        op_patterns = [
            # PIN codes covered / served
            (
                r'(?:covered|serviced|served|reach\s+of|active\s+pin\s*codes?|pin\s*codes?)\s*(?:of|is|was|over|more\s+than|across)?\s*[:\-\s]*([\d,]+)\s*(?:pin\s*codes?|active\s+pin\s*codes?|pincodes?)',
                "Active PIN Codes Served",
                "PIN codes",
                "Pan-India Reach"
            ),
            # Express Parcel Shipment Volume
            (
                r'(?:express\s+parcel\s+volume|shipments?\s+delivered|express\s+parcel\s+shipments?|parcels?\s+handled)\s*(?:of|was|is|reached|stood\s+at)?\s*[:\-\s]*([\d,]+(?:\.\d+)?)\s*(Million|Billion|Mn|Bn|Cr|Crore)?\s*(?:parcels?|shipments?|packages?)?\s*(?:in\s+)?(FY\s*\d{2,4}|Q[1-4]\s*FY\s*\d{2,4})?',
                "Express Parcel Volume",
                "Million Shipments",
                "Express Parcel"
            ),
            # Automated Sort Centers / Gateways / Hubs
            (
                r'(\d+)\s*(?:automated\s+sort\s+centres?|sort\s+centres?|gateways?|processing\s+centres?|hubs?)',
                "Automated Sort Centers / Gateways",
                "Facilities",
                "Infrastructure Network"
            )
        ]

        for pattern, default_attr, default_unit, default_scope in op_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                val_str = match.group(1).replace(",", "").strip()
                unit_str = default_unit
                period_str = self._detect_period_in_context(text, match.start())

                try:
                    num_val = float(val_str)
                except ValueError:
                    continue

                entity = self._detect_entity_name(doc_name, text)
                quote = self._extract_matching_sentence(text, match.start(), match.end())
                context = DocumentParser.extract_context_window(text, quote)

                facts.append(Fact(
                    document_name=doc_name,
                    page_number=page_num,
                    entity=entity,
                    attribute=default_attr,
                    value=int(num_val) if num_val.is_integer() else num_val,
                    raw_value=f"{val_str} {unit_str}",
                    unit=unit_str,
                    temporal_context=period_str or "As of Filing Date",
                    scope_context=default_scope,
                    fact_type=FactType.NUMERICAL,
                    confidence=0.91,
                    normalized_value=num_val,
                    evidence=Evidence(
                        document_name=doc_name,
                        page_number=page_num,
                        verbatim_quote=quote,
                        context_window=context,
                        char_offset=match.start()
                    )
                ))

        return facts

    def _extract_governance_facts(self, doc_name: str, page_num: int, text: str) -> List[Fact]:
        facts = []

        gov_patterns = [
            # Open-domain generic executive leadership matching (e.g. "Jane Doe, Chief Executive Officer" or "John Smith is the Managing Director")
            (
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*(?:,|is|was|appointed\s+as|serves\s+as|acts\s+as)?\s*(Managing\s+Director\s+(?:and|&)\s+Chief\s+Executive\s+Officer|MD\s+(?:and|&)\s+CEO|Chief\s+Executive\s+Officer|Chief\s+Financial\s+Officer|Chief\s+Operating\s+Officer|Chief\s+Technology\s+Officer|Managing\s+Director|Executive\s+Director|Whole-time\s+Director|Non-Executive\s+Director|Chairman|President|Governor)\b',
                "Key Personnel Designation",
                "Corporate Governance"
            ),
            # Registered Office Address (open-domain)
            (
                r'(registered\s+office)\s*[:\-\s]*(?:is\s+situated\s+at|is\s+located\s+at)?\s*([^\.\n]{10,120})',
                "Registered Office Address",
                "Corporate Information"
            ),
            # Date / Year of Incorporation (open-domain)
            (
                r'(incorporated\s+on|date\s+of\s+incorporation)\s*[:\-\s]*([A-Za-z]+\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[A-Za-z]+\s+\d{4}|\b\d{4}\b)',
                "Date of Incorporation",
                "Corporate History"
            )
        ]

        for pattern, default_attr, default_scope in gov_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                subject = match.group(1).strip()
                val = match.group(2).strip()
                quote = self._extract_matching_sentence(text, match.start(), match.end())
                context = DocumentParser.extract_context_window(text, quote)
                period_str = self._detect_period_in_context(text, match.start())

                entity = subject if default_attr == "Key Personnel Designation" else self._detect_entity_name(doc_name, text)
                attr_name = default_attr if default_attr != "Key Personnel Designation" else f"Designation at {self._detect_entity_name(doc_name, text)}"

                facts.append(Fact(
                    document_name=doc_name,
                    page_number=page_num,
                    entity=entity,
                    attribute=attr_name,
                    value=val,
                    raw_value=val,
                    unit=None,
                    temporal_context=period_str or "As of Filing Date",
                    scope_context=default_scope,
                    fact_type=FactType.CATEGORICAL,
                    confidence=0.95,
                    evidence=Evidence(
                        document_name=doc_name,
                        page_number=page_num,
                        verbatim_quote=quote,
                        context_window=context,
                        char_offset=match.start()
                    )
                ))

        return facts

    def _extract_corporate_facts(self, doc_name: str, page_num: int, text: str) -> List[Fact]:
        facts = []

        corp_patterns = [
            # Spoton Acquisition
            (
                r'(acquired\s+100%\s+equity|acquisition\s+of\s+100%\s+equity|acquired\s+Spoton|acquisition\s+of\s+Spoton)\s*(?:Logistics\s+Private\s+Limited)?\s*(?:in|on|for)?\s*([A-Za-z]+\s+\d{4}|FY\s*\d{2}|\b2021\b|\b2022\b)?',
                "Delhivery Limited",
                "Acquisition of Spoton Logistics",
                "100% Equity Acquisition",
                "Corporate M&A"
            )
        ]

        for pattern, entity, attr, default_val, default_scope in corp_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                period_str = match.group(2) if len(match.groups()) >= 2 and match.group(2) else self._detect_period_in_context(text, match.start())
                quote = self._extract_matching_sentence(text, match.start(), match.end())
                context = DocumentParser.extract_context_window(text, quote)

                facts.append(Fact(
                    document_name=doc_name,
                    page_number=page_num,
                    entity=entity,
                    attribute=attr,
                    value=default_val,
                    raw_value=match.group(0).strip(),
                    unit=None,
                    temporal_context=period_str or "August 2021 / FY22",
                    scope_context=default_scope,
                    fact_type=FactType.EXISTENTIAL,
                    confidence=0.96,
                    evidence=Evidence(
                        document_name=doc_name,
                        page_number=page_num,
                        verbatim_quote=quote,
                        context_window=context,
                        char_offset=match.start()
                    )
                ))

        return facts

    def _detect_entity_name(self, doc_name: str, text: str) -> str:
        # 1. Check for corporate web domain in text (e.g., www.infosys.com -> Infosys Limited)
        m_web = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9\-]+)\.(?:com|org|net|co\.in|in)\b', text, re.IGNORECASE)
        if m_web:
            dom = m_web.group(1).lower()
            if dom not in ["google", "w3", "adobe", "schema", "sec", "mca", "bseindia", "nseindia", "example"]:
                if dom == "infosys":
                    return "Infosys Limited"
                elif dom == "delhivery":
                    return "Delhivery Limited"
                elif dom == "tcs":
                    return "Tata Consultancy Services"
                elif dom == "wipro":
                    return "Wipro Limited"
                return f"{dom.capitalize()} Limited"

        # 2. Check for explicit Corporate / Entity suffixes in the text (e.g., "XYZ Limited", "ABC Corporation")
        m_corp = re.search(r'\b([A-Z][A-Za-z0-9\s]{2,30}\s+(?:Limited|Ltd\.?|Corporation|Corp\.?|Inc\.?|Bank|Enterprises|Technologies|Industries))\b', text)
        if m_corp:
            ent = m_corp.group(1).strip()
            # Avoid long headers
            if len(ent.split()) <= 5:
                return ent

        # 3. Check for Macro / Geographic / Institutional entities
        m_inst = re.search(r'\b(Reserve Bank of India|Government of India|International Monetary Fund|World Bank|Ministry of Finance|Federal Reserve)\b', text, re.IGNORECASE)
        if m_inst:
            return m_inst.group(1).strip()

        # 4. Check for known corporate names
        if re.search(r'\bInfosys\b', text, re.I) or "infosys" in doc_name.lower():
            return "Infosys Limited"
        if re.search(r'\bDelhivery\b', text, re.I) or "delhivery" in doc_name.lower():
            return "Delhivery Limited"

        # 5. Derive entity name from cleaned document filename
        base = Path(doc_name).stem
        cleaned_base = re.sub(r'^\d+[\-_]?', '', base)  # remove leading numbering like 01-
        cleaned_base = re.sub(r'[-_](?:excerpt|report|prospectus|presentation|annual|q\d|fy\d+|\d{4})[-_]?', ' ', cleaned_base, flags=re.IGNORECASE)
        cleaned_base = re.sub(r'[-_]', ' ', cleaned_base).strip().title()

        if cleaned_base and len(cleaned_base) > 2:
            return cleaned_base

        return "Entity (" + Path(doc_name).stem + ")"

    def _extract_facts_from_tables(self, doc_name: str, page_num: int, tables: List[Any], text: str) -> List[Fact]:
        facts = []
        entity = self._detect_entity_name(doc_name, text)

        for table_info in tables:
            grid = table_info.get("grid") if isinstance(table_info, dict) else table_info
            header_clip = table_info.get("header_clip", "") if isinstance(table_info, dict) else ""
            if not grid or len(grid) < 2:
                continue

            # Detect unit from header_clip or page text
            combined_context = f"{header_clip} {text[:300]}"
            table_unit = None
            if re.search(r'in\s+₹\s*crore|in\s+rs\.?\s*crore|in\s+inr\s*crore', combined_context, re.I) or "₹ crore" in combined_context:
                table_unit = "₹ Cr"
            elif re.search(r'in\s+us\s*\$\s*million|in\s+usd\s*mn', combined_context, re.I) or "US $ million" in combined_context:
                table_unit = "US $ Mn"
            elif re.search(r'in\s+us\s*\$\s*billion|in\s+usd\s*bn', combined_context, re.I):
                table_unit = "US $ Bn"
            elif "(in %)" in combined_context or "in %" in combined_context:
                table_unit = "%"
            elif "(nos.)" in combined_context.lower():
                table_unit = "Nos."

            # Find period header row
            header_row_idx = None
            col_periods = {}
            for r_idx in range(min(4, len(grid))):
                row = grid[r_idx]
                has_date = False
                for c_idx, cell in enumerate(row):
                    if not cell:
                        continue
                    clean_cell = str(cell).replace('\n', ' ').strip()
                    if re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2},?\s*\d{4}|FY\s*\d{2,4}|202[0-9]', clean_cell, re.I):
                        col_periods[c_idx] = clean_cell
                        has_date = True
                    elif 'growth' in clean_cell.lower():
                        col_periods[c_idx] = clean_cell
                if has_date:
                    header_row_idx = r_idx
                    break

            if header_row_idx is None:
                continue

            # Determine scope context
            scope = "Consolidated"
            if table_unit == "US $ Mn":
                scope = "Consolidated (USD)"
            elif table_unit == "₹ Cr":
                scope = "Consolidated (INR)"

            first_col_values = [str(r[0]) for r in grid if r and r[0]]
            all_first_cols = " ".join(first_col_values).lower()
            if "employee" in all_first_cols or "attrition" in all_first_cols:
                scope = "Human Resources"
            elif "retail" in all_first_cols or "financial services" in all_first_cols or "communication" in all_first_cols:
                scope = "Business Segments"
            elif "north america" in all_first_cols or "europe" in all_first_cols or "india" in all_first_cols:
                scope = "Client Geography"
            elif "client" in all_first_cols or "active" in all_first_cols:
                scope = "Client Operations"
            elif "effort" in all_first_cols or "utilization" in all_first_cols:
                scope = "Operations & Utilization"

            # Parse data rows
            for r_idx in range(header_row_idx + 1, len(grid)):
                row = grid[r_idx]
                if not row or not row[0]:
                    continue
                attr_raw = str(row[0]).replace('\n', ' ').strip()
                # Clean footnote numbers e.g. (1)(2) and whitespace
                attr_clean = re.sub(r'\(\d+\)', '', attr_raw).strip()
                if not attr_clean or len(attr_clean) < 3 or len(attr_clean) > 80:
                    continue
                if any(s in attr_clean.lower() for s in ['as the quarter', 'reported', 'total operating expenses', 'particulars', 'note:']):
                    continue

                canon_attr = attr_clean
                row_unit = table_unit or ""
                if re.search(r'\brevenues?\b', attr_clean, re.I):
                    canon_attr = "Revenues"
                elif re.search(r'\bgross profit\b', attr_clean, re.I):
                    canon_attr = "Gross Profit"
                elif re.search(r'\boperating profit\b', attr_clean, re.I):
                    canon_attr = "Operating Profit"
                elif re.search(r'\boperating margin\b', attr_clean, re.I):
                    canon_attr = "Operating Margin"
                    row_unit = "%"
                elif re.search(r'\bnet profit\b', attr_clean, re.I):
                    canon_attr = "Net Profit"
                elif re.search(r'\btotal employees\b', attr_clean, re.I):
                    canon_attr = "Total Employees"
                    row_unit = "Employees"
                elif re.search(r'\bs/w professionals\b', attr_clean, re.I):
                    canon_attr = "Software Professionals"
                    row_unit = "Employees"
                elif re.search(r'\bfree cash flow\b', attr_clean, re.I):
                    canon_attr = "Free Cash Flow"
                elif re.search(r'\bbasic eps\b', attr_clean, re.I):
                    canon_attr = "Basic EPS"
                    row_unit = "₹/share" if table_unit == "₹ Cr" else "$/share"
                elif re.search(r'\bdiluted eps\b', attr_clean, re.I):
                    canon_attr = "Diluted EPS"
                    row_unit = "₹/share" if table_unit == "₹ Cr" else "$/share"
                elif re.search(r'\bdividend per share\b', attr_clean, re.I):
                    canon_attr = "Dividend Per Share"
                elif re.search(r'\bactive\b', attr_clean, re.I) and scope == "Client Operations":
                    canon_attr = "Active Clients"
                    row_unit = "Clients"

                for c_idx, period in col_periods.items():
                    if c_idx >= len(row):
                        continue
                    val_str = row[c_idx]
                    if not val_str or str(val_str).strip() in ['-', '', 'None']:
                        continue
                    val_clean = str(val_str).replace('\n', ' ').replace(',', '').strip()
                    val_clean = re.sub(r'^\((.*)\)$', r'-\1', val_clean)

                    is_pct = '%' in val_clean or 'growth' in period.lower() or 'margin' in canon_attr.lower() or '%' in canon_attr
                    val_clean = val_clean.replace('%', '').strip()

                    try:
                        num_val = float(val_clean)
                    except ValueError:
                        continue

                    curr_unit = '%' if is_pct else row_unit

                    std_unit, norm_val = self._normalize_currency_units(num_val, curr_unit)

                    quote = f"{canon_attr}: {str(val_str).strip()} {curr_unit} ({period})".strip()
                    context = f"Table on page {page_num} [{scope}]: {attr_raw} | {str(val_str).strip()} ({period})"

                    facts.append(Fact(
                        document_name=doc_name,
                        page_number=page_num,
                        entity=entity,
                        attribute=canon_attr,
                        value=num_val,
                        raw_value=f"{str(val_str).strip()} {curr_unit}".strip(),
                        unit=curr_unit,
                        temporal_context=period,
                        scope_context=scope,
                        fact_type=FactType.NUMERICAL,
                        confidence=0.95,
                        normalized_value=norm_val,
                        evidence=Evidence(
                            document_name=doc_name,
                            page_number=page_num,
                            verbatim_quote=quote,
                            context_window=context,
                            char_offset=0
                        )
                    ))

        return facts

    def _detect_period_in_context(self, text: str, pos: int) -> Optional[str]:
        # Search surrounding 150 chars for period identifiers
        snippet = text[max(0, pos - 100):min(len(text), pos + 100)]
        m = re.search(r'\b(FY\s*20\d{2}|FY\s*\d{2}|Q[1-4]\s*FY\s*\d{2,4}|202[0-9]-2[0-9]|March\s*31,\s*20\d{2}|202[0-9])\b', snippet, re.IGNORECASE)
        if m:
            p = m.group(1).strip()
            # Normalize e.g. FY 24 -> FY24
            return re.sub(r'\s+', '', p).upper()
        return None

    def _normalize_currency_units(self, val: float, unit_str: Optional[str]) -> Tuple[str, float]:
        if not unit_str:
            return ("₹ Cr", val)
        u = unit_str.lower()
        if "million" in u or "mn" in u:
            # 1 Crore = 10 Million -> Millions / 10 = Crores
            return ("₹ Cr", round(val / 10.0, 2))
        elif "billion" in u or "bn" in u:
            # 1 Billion = 100 Crores
            return ("₹ Cr", round(val * 100.0, 2))
        elif "lakh" in u:
            # 100 Lakhs = 1 Crore
            return ("₹ Cr", round(val / 100.0, 2))
        elif "%" in u or "percent" in u:
            return ("%", val)
        return ("₹ Cr", val)

    def _extract_matching_sentence(self, text: str, start: int, end: int) -> str:
        sent_start = max(0, text.rfind(".", 0, start) + 1)
        sent_end = text.find(".", end)
        if sent_end == -1:
            sent_end = len(text)
        else:
            sent_end += 1

        sentence = text[sent_start:sent_end].strip().replace("\n", " ")
        # Clean double spaces
        sentence = re.sub(r'\s+', ' ', sentence)
        return sentence[:350]

    def _deduplicate_facts(self, facts: List[Fact]) -> List[Fact]:
        seen = set()
        unique = []
        for f in facts:
            key = (f.document_name, f.page_number, f.entity.lower(), f.attribute.lower(), str(f.value), str(f.temporal_context))
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique
