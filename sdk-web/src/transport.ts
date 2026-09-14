import { RawTelemetryEvent, SDKConfig } from './types';

export class Transport {
  private buffer: RawTelemetryEvent[] = [];
  private config: Required<SDKConfig>;
  private timer: number | null = null;

  constructor(config: Required<SDKConfig>) {
    this.config = config;
    this.startPeriodicFlush();
  }

  public enqueue(event: RawTelemetryEvent): void {
    this.buffer.push(event);
    if (this.config.debug) {
      console.log('[TelemetrySDK] Event enqueued:', event.event_type, event);
    }
    if (this.buffer.length >= this.config.batchSize) {
      this.flush();
    }
  }

  private startPeriodicFlush(): void {
    if (typeof window !== 'undefined') {
      this.timer = window.setInterval(() => {
        this.flush();
      }, this.config.flushIntervalMs);
    }
  }

  public flush(isSync: boolean = false): void {
    if (this.buffer.length === 0) return;

    const eventsToSend = [...this.buffer];
    this.buffer = [];

    const payload = JSON.stringify({ events: eventsToSend });
    const url = `${this.config.endpoint}/api/v1/events`;

    if (isSync && typeof navigator !== 'undefined' && navigator.sendBeacon) {
      const blob = new Blob([payload], { type: 'application/json' });
      navigator.sendBeacon(url, blob);
      return;
    }

    if (typeof fetch !== 'undefined') {
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true,
      }).catch((err) => {
        if (this.config.debug) {
          console.warn('[TelemetrySDK] Failed to deliver event batch:', err);
        }
        // Re-encolar si la red falló temporalmente (máximo 100 eventos)
        if (this.buffer.length < 100) {
          this.buffer.unshift(...eventsToSend);
        }
      });
    }
  }

  public destroy(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.flush(true);
  }
}
