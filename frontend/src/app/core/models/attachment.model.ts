export interface AttachmentResponse {
  id: number;
  original_name: string;
  stored_name: string;
  file_path: string;
  content_type: string;
  file_size: number;
  issue_id: number;
  uploaded_by: number;
  created_at: string;
}
