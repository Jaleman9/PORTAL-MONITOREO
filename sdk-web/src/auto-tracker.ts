import { EventProperties, EventType, RawTelemetryEvent } from './types';

const SESSION_STORAGE_KEY = '_telemetry_session';
const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutos de inactividad

export interface AutoTrackerCallbacks {
  onEvent: (type: EventType, properties: EventProperties) => void;
}

export class AutoTracker {
  private callbacks: AutoTrackerCallbacks;
  private currentSessionId: string;
  private lastActivityTime: number;

  constructor(callbacks: AutoTrackerCallbacks) {
    this.callbacks = callbacks;
    this.lastActivityTime = Date.now();
    this.currentSessionId = this.initSession();
    this.attachListeners();
  }

  public getSessionId(): string {
    return this.currentSessionId;
  }

  private initSession(): string {
    let existingSession = null;
    try {
      const stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (stored) {
        existingSession = JSON.parse(stored);
      }
    } catch {
      // Ignorar errores de storage
    }

    const now = Date.now();
    if (existingSession && (now - existingSession.lastActivity) < SESSION_TIMEOUT_MS) {
      existingSession.lastActivity = now;
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(existingSession));
      return existingSession.sessionId;
    }

    // Nueva sesión
    const newSessionId = 'sess_' + Math.random().toString(36).substring(2, 12) + '_' + Date.now().toString(36);
    const sessionData = { sessionId: newSessionId, lastActivity: now, startedAt: now };
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(sessionData));
    } catch {
      // Fallback
    }

    // Disparar evento automático de inicio de sesión
    setTimeout(() => {
      this.callbacks.onEvent('session_start', {
        referrer: typeof document !== 'undefined' ? document.referrer : '',
        user_agent: typeof navigator !== 'undefined' ? navigator.userAgent.substring(0, 250) : '',
        viewport_width: typeof window !== 'undefined' ? window.innerWidth : 0,
        viewport_height: typeof window !== 'undefined' ? window.innerHeight : 0,
      });
    }, 50);

    return newSessionId;
  }

  private updateActivity(): void {
    this.lastActivityTime = Date.now();
    try {
      const stored = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        data.lastActivity = this.lastActivityTime;
        sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(data));
      }
    } catch {
      // Ignorar
    }
  }

  private getLoadTime(): number {
    if (typeof performance === 'undefined') return 0;
    const navEntries = performance.getEntriesByType('navigation');
    if (navEntries.length > 0) {
      const nav = navEntries[0] as PerformanceNavigationTiming;
      return Math.round(nav.duration || 0);
    }
    return 0;
  }

  public triggerPageView(): void {
    if (typeof window === 'undefined') return;
    this.updateActivity();

    const sanitizedPath = window.location.pathname;
    this.callbacks.onEvent('page_view', {
      page_path: sanitizedPath,
      page_title: document.title ? document.title.substring(0, 200) : '',
      referrer: document.referrer ? document.referrer.substring(0, 500) : '',
      load_time_ms: this.getLoadTime(),
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
    });
  }

  private attachListeners(): void {
    if (typeof window === 'undefined') return;

    // 1. Detección de page_view inicial al cargar
    if (document.readyState === 'complete') {
      this.triggerPageView();
    } else {
      window.addEventListener('load', () => {
        setTimeout(() => this.triggerPageView(), 100);
      });
    }

    // 2. Instrumentación de SPA (pushState, replaceState, popstate)
    const originalPushState = history.pushState;
    if (originalPushState) {
      history.pushState = (...args) => {
        originalPushState.apply(history, args);
        setTimeout(() => this.triggerPageView(), 50);
      };
    }

    const originalReplaceState = history.replaceState;
    if (originalReplaceState) {
      history.replaceState = (...args) => {
        originalReplaceState.apply(history, args);
        setTimeout(() => this.triggerPageView(), 50);
      };
    }

    window.addEventListener('popstate', () => {
      setTimeout(() => this.triggerPageView(), 50);
    });

    // 3. Captura global de errores no capturados
    window.addEventListener('error', (event: ErrorEvent) => {
      this.updateActivity();
      this.callbacks.onEvent('error', {
        page_path: window.location.pathname,
        error_type: event.error ? event.error.name : 'UncaughtError',
        error_message: event.message ? event.message.substring(0, 250) : 'Unknown Script Error',
      });
    });

    window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
      this.updateActivity();
      const reason = event.reason;
      this.callbacks.onEvent('error', {
        page_path: window.location.pathname,
        error_type: 'UnhandledPromiseRejection',
        error_message: reason ? (reason.message || String(reason)).substring(0, 250) : 'Promise Rejected',
      });
    });

    // 4. Session end o visibilidad de página
    window.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.updateActivity();
      }
    });

    window.addEventListener('beforeunload', () => {
      this.callbacks.onEvent('session_end', {
        page_path: window.location.pathname,
      });
    });

    // 5. Captura no invasiva de interacciones y clics semánticos (sin formularios ni PII)
    if (typeof document !== 'undefined') {
      document.addEventListener('click', (event: MouseEvent) => {
        try {
          const target = event.target as HTMLElement | null;
          if (!target) return;
          const button = target.closest('button, a, [role="button"], input[type="submit"]') as HTMLElement | null;
          if (button) {
            this.updateActivity();
            const tag = button.tagName.toLowerCase();
            const elemId = button.id || '';
            const elemText = (button.innerText || button.textContent || button.getAttribute('aria-label') || '').substring(0, 50).trim();
            const href = tag === 'a' ? (button.getAttribute('href') || '').substring(0, 100) : undefined;

            this.callbacks.onEvent('custom', {
              action: 'click',
              element_tag: tag,
              element_id: elemId,
              element_text: elemText,
              link_target: href,
              page_path: window.location.pathname,
            });
          }
        } catch {
          // Ignorar silenciosamente
        }
      }, { passive: true } as any);
    }
  }
}
