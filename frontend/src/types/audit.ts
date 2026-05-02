export type DocumentType = 'invoice' | 'receipt' | 'expense_report';

export type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical';

export type RoutingDecision = 'auto_approve' | 'human_review' | 'compliance_hold' | 'hard_reject';

export interface DocumentMetadata {
  document_id: string;
  tenant_id: string;
  submitted_by: string;
  declared_document_type: string;
  true_document_type: string | null;
  cost_center: string | null;
  original_filename: string;
  content_type: string | null;
  file_size_bytes: number;
  sha256: string;
  storage_path: string;
  submitted_at_utc: string;
  status: string;
}

export interface PageQuality {
  page_number: number;
  ocr_confidence: number;
  notes: string[];
}

export interface PreprocessingResult {
  document_id: string;
  text: string;
  layout_metadata: Record<string, unknown>;
  pages: PageQuality[];
  true_document_type: string;
  quality_low: boolean;
}

export interface LineItem {
  description: string | null;
  quantity: string | number | null;
  unit_price: string | number | null;
  amount: string | number | null;
  tax_rate: string | number | null;
}

export interface ExtractedInvoice {
  vendor_name: string | null;
  vendor_tax_id: string | null;
  invoice_number: string | null;
  invoice_date: string | null;
  due_date: string | null;
  currency: string | null;
  subtotal_amount: string | number | null;
  tax_amount: string | number | null;
  total_amount: string | number | null;
  purchase_order: string | null;
  cost_center: string | null;
  line_items: LineItem[];
}

export interface FieldAnnotation {
  field_name: string;
  confidence: number;
  source_quote: string | null;
  page_number: number | null;
  discrepancy: string | null;
  extraction_failure: string | null;
  hallucination_suspected: boolean;
}

export interface VerifiedExtraction {
  document_id: string;
  invoice: ExtractedInvoice;
  annotations: Record<string, FieldAnnotation>;
  raw_primary_response: string | null;
  raw_verifier_response: string | null;
}

export interface Finding {
  rule_id: string;
  rule_name: string;
  severity: Severity;
  expected_value: unknown;
  actual_value: unknown;
  explanation: string;
  field_name: string | null;
  metadata: Record<string, unknown>;
}

export interface ValidationResult {
  findings: Finding[];
}

export interface AnomalyResult {
  flags: Finding[];
  deviation_score: number;
}

export interface FieldConfidence {
  field_name: string;
  score: number;
  criticality_weight: number;
}

export interface ConfidenceResult {
  field_scores: FieldConfidence[];
  document_confidence: number;
  rule_severity_penalty: number;
  anomaly_deviation_score: number;
  routing_decision: RoutingDecision;
  routing_reason: string;
}

export interface ReportResult {
  json_report_path: string;
  markdown_report_path: string;
  summary: string;
}

export interface PipelineResult {
  metadata: DocumentMetadata;
  preprocessing: PreprocessingResult | null;
  extraction: VerifiedExtraction | null;
  validation: ValidationResult | null;
  anomaly: AnomalyResult | null;
  confidence: ConfidenceResult | null;
  report: ReportResult | null;
}

export interface UploadDocumentPayload {
  file: File;
  tenantId: string;
  submittedBy: string;
  declaredDocumentType: DocumentType;
  costCenter?: string;
}

