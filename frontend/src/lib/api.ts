import axios from 'axios';
import type { PipelineResult, UploadDocumentPayload } from '../types/audit';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 180_000,
});

export async function uploadDocument(payload: UploadDocumentPayload): Promise<PipelineResult> {
  const formData = new FormData();
  formData.append('file', payload.file);
  formData.append('tenant_id', payload.tenantId);
  formData.append('submitted_by', payload.submittedBy);
  formData.append('declared_document_type', payload.declaredDocumentType);
  if (payload.costCenter) {
    formData.append('cost_center', payload.costCenter);
  }

  const response = await api.post<PipelineResult>('/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg ?? JSON.stringify(item)).join(', ');
    }
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unexpected error while processing the document.';
}

