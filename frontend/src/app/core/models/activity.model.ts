export interface ActivityLogResponse {
  id: number;
  actor_id?: number;
  actor_name?: string;
  action: string;
  entity_type: string;
  entity_id: number;
  metadata?: Record<string, any>;
  created_at: string;
}
