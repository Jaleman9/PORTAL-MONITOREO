export type EventType = 'session_start' | 'session_end' | 'page_view' | 'error' | 'custom';

export interface SDKConfig {
  appId: string;
  endpoint: string;
  flushIntervalMs?: number;
  batchSize?: number;
  debug?: boolean;
}

export interface UserContext {
  userId?: string;
  role?: string;
  department?: string;
}

export interface EventProperties {
  page_path?: string;
  page_title?: string;
  referrer?: string;
  load_time_ms?: number;
  error_message?: string;
  error_type?: string;
  user_agent?: string;
  viewport_width?: number;
  viewport_height?: number;
  [key: string]: string | number | boolean | undefined;
}

export interface RawTelemetryEvent {
  event_id: string;
  timestamp: string;
  app_id: string;
  session_id: string;
  user_id?: string;
  event_type: EventType;
  platform: 'web';
  role: string;
  department: string;
  properties: EventProperties;
}
