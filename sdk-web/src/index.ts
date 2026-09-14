import { AutoTracker } from './auto-tracker';
import { Transport } from './transport';
import { EventProperties, EventType, RawTelemetryEvent, SDKConfig, UserContext } from './types';

function generateUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export class WebAnalyticsSDK {
  private config: Required<SDKConfig> | null = null;
  private userContext: UserContext = { role: 'guest', department: 'unknown' };
  private transport: Transport | null = null;
  private autoTracker: AutoTracker | null = null;
  private initialized = false;

  public init(config: SDKConfig): void {
    if (this.initialized) {
      console.warn('[TelemetrySDK] SDK ya fue inicializado previamente.');
      return;
    }

    this.config = {
      appId: config.appId,
      endpoint: config.endpoint.replace(/\/$/, ''),
      flushIntervalMs: config.flushIntervalMs || 5000,
      batchSize: config.batchSize || 10,
      debug: config.debug || false,
    };

    this.transport = new Transport(this.config);

    this.autoTracker = new AutoTracker({
      onEvent: (type: EventType, properties: EventProperties) => {
        this.emit(type, properties);
      },
    });

    this.initialized = true;
    if (this.config.debug) {
      console.log(`[TelemetrySDK] Inicializado para app_id: ${this.config.appId}`);
    }
  }

  public identify(userId: string, role?: string, department?: string): void {
    this.userContext = {
      userId: userId.trim(),
      role: (role || 'guest').trim().toLowerCase(),
      department: (department || 'unknown').trim().toLowerCase(),
    };
    if (this.config?.debug) {
      console.log('[TelemetrySDK] Usuario identificado:', { role: this.userContext.role, department: this.userContext.department });
    }
  }

  public track(eventName: string, properties: EventProperties = {}): void {
    this.emit(eventName as EventType, properties);
  }

  public flush(): void {
    this.transport?.flush();
  }

  private emit(eventType: EventType, properties: EventProperties): void {
    if (!this.initialized || !this.config || !this.transport || !this.autoTracker) {
      if (this.config?.debug) {
        console.warn('[TelemetrySDK] Intento de evento antes de inicializar.');
      }
      return;
    }

    const event: RawTelemetryEvent = {
      event_id: generateUUID(),
      timestamp: new Date().toISOString(),
      app_id: this.config.appId,
      session_id: this.autoTracker.getSessionId(),
      user_id: this.userContext.userId,
      event_type: eventType,
      platform: 'web',
      role: this.userContext.role || 'guest',
      department: this.userContext.department || 'unknown',
      properties: properties,
    };

    this.transport.enqueue(event);
  }
}

// Instancia singleton para uso en navegador
export const Telemetry = new WebAnalyticsSDK();

// Exponer en window para integración mediante tag <script>
if (typeof window !== 'undefined') {
  (window as any).Telemetry = Telemetry;
}

export default Telemetry;
