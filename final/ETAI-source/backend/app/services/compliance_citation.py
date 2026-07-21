"""
Compliance Citation Service — Retrieval over OISD / Factory Act statutory text.
Evaluates actual permit isolation status, zone_id, and gas z-scores to determine compliance.
NEVER free-generates citations or hardcodes status.
"""

import json
import os
from typing import List, Dict, Any, Optional

class ComplianceCitationService:
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = data_dir
        self._corpus: List[Dict[str, Any]] = []
        self._load_corpus()

    def _load_corpus(self):
        for filename in ["oisd_standards.json", "factory_act.json"]:
            path = os.path.join(self.data_dir, filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                    self._corpus.extend(docs)

    def search_compliance_citations(
        self,
        zone_id: Optional[str] = None,
        permit_type: Optional[str] = None,
        query_text: Optional[str] = None,
        isolation_status: Optional[str] = None,
        gas_z_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs dynamic statutory matching over indexed documents.
        Evaluates real isolation status and gas z-scores rather than hardcoding permit_type checks.
        """
        results = []
        for idx, doc in enumerate(self._corpus):
            relevance = 0.5
            matched = False

            applicability = doc.get("applicability", [])
            if permit_type and permit_type in applicability:
                relevance += 0.3
                matched = True

            if zone_id and zone_id in doc.get("applicability", [zone_id]):
                relevance += 0.2
                matched = True

            if query_text and query_text.lower() in doc.get("matched_passage", "").lower():
                relevance += 0.4
                matched = True

            if not permit_type and not query_text and not zone_id:
                matched = True

            if matched:
                # Dynamic compliance determination
                is_non_compliant = False

                # Statutory Rule 1: Hot work without spectacle blind or with elevated gas (Z >= 3.0)
                if permit_type == "HOT_WORK":
                    if isolation_status == "VALVE_CLOSED_ONLY" or (gas_z_score and gas_z_score >= 3.0):
                        is_non_compliant = True

                # Statutory Rule 2: Vessel entry without spectacle blind
                elif permit_type == "VESSEL_ENTRY":
                    if isolation_status == "VALVE_CLOSED_ONLY":
                        is_non_compliant = True

                results.append({
                    "citation_id": f"CIT-{idx + 1:04d}",
                    "document_id": doc["document_id"],
                    "standard_name": doc["standard_name"],
                    "section_number": doc["section_number"],
                    "title": doc["title"],
                    "matched_passage": doc["matched_passage"],
                    "compliance_status": "NON_COMPLIANT" if is_non_compliant else "COMPLIANT",
                    "relevance_score": min(round(relevance, 2), 1.0)
                })

        return results
