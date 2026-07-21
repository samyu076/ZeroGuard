"""
Compliance Citation Service — Dynamic Statutory Matching over OISD, Factory Act, and DGMS Standards.
Evaluates actual permit isolation_status, zone_id, and gas_z_score.
"""

import json
import os
from typing import List, Dict, Any, Optional


class ComplianceCitationService:
    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.data_dir = os.path.join(BASE_DIR, "data")
        else:
            self.data_dir = data_dir

        self._corpus: List[Dict[str, Any]] = []
        self._load_corpus()

    def _load_corpus(self):
        for filename in ["oisd_standards.json", "factory_act.json", "dgms_regulations.json"]:
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
        Performs dynamic statutory matching over indexed OISD, Factory Act, and DGMS documents.
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

            # Determine compliance status based on real scenario signals
            status = "COMPLIANT"
            if permit_type == "HOT_WORK":
                if isolation_status != "SPECTACLE_BLIND_INSTALLED" and (gas_z_score is not None and gas_z_score >= 3.0):
                    status = "NON_COMPLIANT"

            if matched or not (permit_type or zone_id or query_text):
                res = dict(doc)
                res["relevance_score"] = round(min(relevance, 1.0), 2)
                res["compliance_status"] = status
                results.append(res)

        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results
