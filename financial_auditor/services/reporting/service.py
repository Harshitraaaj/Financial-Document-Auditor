from __future__ import annotations

import json
from pathlib import Path

from financial_auditor.core.config import Settings
from financial_auditor.core.schemas.pipeline import PipelineResult, ReportResult


class ReportGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_local_dirs()

    def render(self, result: PipelineResult) -> ReportResult:
        document_dir = self.settings.reports_dir / result.metadata.document_id
        document_dir.mkdir(parents=True, exist_ok=True)
        json_path = document_dir / "audit_report.json"
        markdown_path = document_dir / "audit_report.md"
        json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        markdown = self._markdown(result)
        markdown_path.write_text(markdown, encoding="utf-8")
        return ReportResult(
            json_report_path=str(json_path),
            markdown_report_path=str(markdown_path),
            summary=self._summary(result),
        )

    def _markdown(self, result: PipelineResult) -> str:
        metadata = result.metadata
        confidence = result.confidence
        findings = result.validation.findings if result.validation else []
        anomaly_flags = result.anomaly.flags if result.anomaly else []
        lines = [
            f"# Audit Report: {metadata.document_id}",
            "",
            f"- Tenant: {metadata.tenant_id}",
            f"- Submitted by: {metadata.submitted_by}",
            f"- File SHA-256: `{metadata.sha256}`",
            f"- Routing decision: `{confidence.routing_decision if confidence else 'unavailable'}`",
            f"- Document confidence: `{confidence.document_confidence:.3f}`" if confidence else "- Document confidence: unavailable",
            "",
            "## Findings",
        ]
        if not findings and not anomaly_flags:
            lines.append("No deterministic findings or anomaly flags were produced.")
        for finding in findings + anomaly_flags:
            lines.extend(
                [
                    f"### {finding.rule_name}",
                    f"- Severity: `{finding.severity}`",
                    f"- Expected: `{finding.expected_value}`",
                    f"- Actual: `{finding.actual_value}`",
                    f"- Explanation: {finding.explanation}",
                    "",
                ]
            )
        if result.extraction:
            lines.extend(["## Extracted Invoice", "```json"])
            lines.append(json.dumps(result.extraction.invoice.model_dump(mode="json"), indent=2))
            lines.append("```")
        return "\n".join(lines)

    @staticmethod
    def _summary(result: PipelineResult) -> str:
        if not result.confidence:
            return "Audit report generated without confidence result."
        return f"{result.confidence.routing_decision}: {result.confidence.routing_reason}"

