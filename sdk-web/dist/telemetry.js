/**
 * Web Telemetry SDK - Fase 1 (MVP)
 * Librería autónoma de auto-instrumentación y recolección de eventos web
 * Cumple con principios de minimización de datos y privacidad en el borde.
 */
(function (window) {
  'use strict';

  var SESSION_STORAGE_KEY = '_telemetry_session';
  var SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutos

  function generateUUID() {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      var v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function WebAnalyticsSDK() {
    this.config = null;
    this.userContext = { role: 'guest', department: 'unknown' };
    this.buffer = [];
    this.timer = null;
    this.sessionId = null;
    this.initialized = false;
  }

  WebAnalyticsSDK.prototype.init = function (options) {
    if (this.initialized) return;
    this.config = {
      appId: options.appId,
      endpoint: (options.endpoint || '').replace(/\/$/, ''),
      flushIntervalMs: options.flushIntervalMs || 5000,
      batchSize: options.batchSize || 10,
      debug: !!options.debug
    };

    this.sessionId = this._initSession();
    this._attachListeners();
    this._startPeriodicFlush();
    this.initialized = true;

    if (this.config.debug) {
      console.log('[TelemetrySDK] Inicializado para app_id:', this.config.appId);
    }
  };

  WebAnalyticsSDK.prototype.identify = function (userId, role, department) {
    this.userContext = {
      userId: userId ? String(userId).trim() : undefined,
      role: (role || 'guest').trim().toLowerCase(),
      department: (department || 'unknown').trim().toLowerCase()
    };
    if (this.config && this.config.debug) {
      console.log('[TelemetrySDK] Usuario identificado:', { role: this.userContext.role, department: this.userContext.department });
    }
  };

  WebAnalyticsSDK.prototype.track = function (eventName, properties) {
    this._emit(eventName, properties || {});
  };

  WebAnalyticsSDK.prototype.flush = function (isSync) {
    if (this.buffer.length === 0) return;
    var eventsToSend = this.buffer.slice();
    this.buffer = [];

    var payload = JSON.stringify({ events: eventsToSend });
    var url = this.config.endpoint + '/api/v1/events';

    if (isSync && navigator.sendBeacon) {
      var blob = new Blob([payload], { type: 'application/json' });
      navigator.sendBeacon(url, blob);
      return;
    }

    var self = this;
    if (typeof fetch !== 'undefined') {
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true
      }).catch(function (err) {
        if (self.config && self.config.debug) {
          console.warn('[TelemetrySDK] Error en entrega de lote:', err);
        }
        if (self.buffer.length < 100) {
          self.buffer = eventsToSend.concat(self.buffer);
        }
      });
    }
  };

  WebAnalyticsSDK.prototype._emit = function (eventType, properties) {
    if (!this.initialized) return;

    var event = {
      event_id: generateUUID(),
      timestamp: new Date().toISOString(),
      app_id: this.config.appId,
      session_id: this.sessionId,
      user_id: this.userContext.userId,
      event_type: eventType,
      platform: 'web',
      role: this.userContext.role,
      department: this.userContext.department,
      properties: properties || {}
    };

    this.buffer.push(event);
    if (this.config.debug) {
      console.log('[TelemetrySDK] Evento capturado:', eventType, event);
    }
    if (this.buffer.length >= this.config.batchSize) {
      this.flush(false);
    }
  };

  WebAnalyticsSDK.prototype._initSession = function () {
    var stored = null;
    try {
      var raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
      if (raw) stored = JSON.parse(raw);
    } catch (e) {}

    var now = Date.now();
    if (stored && (now - stored.lastActivity) < SESSION_TIMEOUT_MS) {
      stored.lastActivity = now;
      try { sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(stored)); } catch (e) {}
      return stored.sessionId;
    }

    var newId = 'sess_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now().toString(36);
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({ sessionId: newId, lastActivity: now }));
    } catch (e) {}

    var self = this;
    setTimeout(function () {
      self._emit('session_start', {
        referrer: document.referrer || '',
        user_agent: navigator.userAgent.substring(0, 250),
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight
      });
    }, 50);

    return newId;
  };

  WebAnalyticsSDK.prototype._attachListeners = function () {
    var self = this;

    function triggerPageView() {
      var loadTime = 0;
      if (typeof performance !== 'undefined') {
        var navEntries = performance.getEntriesByType('navigation');
        if (navEntries.length > 0) {
          loadTime = Math.round(navEntries[0].duration || 0);
        }
      }

      self._emit('page_view', {
        page_path: window.location.pathname,
        page_title: (document.title || '').substring(0, 200),
        referrer: (document.referrer || '').substring(0, 500),
        load_time_ms: loadTime,
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight
      });
    }

    // 1. Page view inicial
    if (document.readyState === 'complete') {
      triggerPageView();
    } else {
      window.addEventListener('load', function () {
        setTimeout(triggerPageView, 100);
      });
    }

    // 2. Interceptación SPA (pushState, replaceState, popstate)
    var origPush = history.pushState;
    if (origPush) {
      history.pushState = function () {
        origPush.apply(history, arguments);
        setTimeout(triggerPageView, 50);
      };
    }
    var origReplace = history.replaceState;
    if (origReplace) {
      history.replaceState = function () {
        origReplace.apply(history, arguments);
        setTimeout(triggerPageView, 50);
      };
    }
    window.addEventListener('popstate', function () {
      setTimeout(triggerPageView, 50);
    });

    // 3. Captura global de errores
    window.addEventListener('error', function (evt) {
      self._emit('error', {
        page_path: window.location.pathname,
        error_type: evt.error ? evt.error.name : 'UncaughtError',
        error_message: (evt.message || 'Unknown error').substring(0, 250)
      });
    });

    window.addEventListener('unhandledrejection', function (evt) {
      var reason = evt.reason;
      self._emit('error', {
        page_path: window.location.pathname,
        error_type: 'UnhandledPromiseRejection',
        error_message: reason ? (reason.message || String(reason)).substring(0, 250) : 'Promise Rejected'
      });
    });

    // 4. Salida de página
    window.addEventListener('beforeunload', function () {
      self._emit('session_end', {
        page_path: window.location.pathname
      });
      self.flush(true);
    });

    // 5. Captura no invasiva de interacciones y clics semánticos (sin formularios ni PII)
    if (typeof document !== 'undefined') {
      document.addEventListener('click', function (evt) {
        try {
          var target = evt.target;
          if (!target) return;
          var button = target.closest('button, a, [role="button"], input[type="submit"]');
          if (button) {
            self._updateActivity();
            var tag = button.tagName.toLowerCase();
            var elemId = button.id || '';
            var elemText = (button.innerText || button.textContent || button.getAttribute('aria-label') || '').substring(0, 50).trim();
            var href = tag === 'a' ? (button.getAttribute('href') || '').substring(0, 100) : undefined;

            self._emit('custom', {
              action: 'click',
              element_tag: tag,
              element_id: elemId,
              element_text: elemText,
              link_target: href,
              page_path: window.location.pathname
            });
          }
        } catch (e) {}
      }, true);
    }
  };

  WebAnalyticsSDK.prototype._startPeriodicFlush = function () {
    var self = this;
    this.timer = setInterval(function () {
      self.flush(false);
    }, this.config.flushIntervalMs);
  };

  var instance = new WebAnalyticsSDK();
  window.Telemetry = instance;
})(window);
