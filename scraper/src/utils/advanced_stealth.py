"""
Advanced stealth scripts for fingerprinting evasion
"""
ADVANCED_STEALTH_SCRIPT = """
// ============================================
// ADVANCED ANTI-DETECTION SCRIPT
// ============================================

(function() {
    'use strict';
    
    // 1. Hide webdriver property completely
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
        configurable: true
    });
    
    // 2. Override plugins to look real
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const plugins = [];
            for (let i = 0; i < 5; i++) {
                plugins.push({
                    name: `Plugin ${i}`,
                    description: 'Native plugin',
                    filename: 'internal-pdf-viewer'
                });
            }
            return plugins;
        },
        configurable: true
    });
    
    // 3. Realistic languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['es-ES', 'es', 'en-US', 'en'],
        configurable: true
    });
    
    // 4. Mock chrome object (Chrome/Edge only)
    if (navigator.userAgent.includes('Chrome') || navigator.userAgent.includes('Edg')) {
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
    }
    
    // 5. Override permissions API
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = function(parameters) {
        return parameters.name === 'notifications' 
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters);
    };
    
    // 6. Canvas Fingerprinting Evasion
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        if (type === 'image/png' || type === 'image/jpeg') {
            const context = this.getContext('2d');
            if (context) {
                const imageData = context.getImageData(0, 0, this.width, this.height);
                // Add minimal noise to canvas (undetectable to human eye)
                for (let i = 0; i < imageData.data.length; i += 4) {
                    if (Math.random() < 0.001) { // 0.1% of pixels
                        imageData.data[i] += Math.random() < 0.5 ? -1 : 1;
                    }
                }
                context.putImageData(imageData, 0, 0);
            }
        }
        return originalToDataURL.apply(this, arguments);
    };
    
    // 7. WebGL Fingerprinting Evasion
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
            return 'Intel Inc.';
        }
        if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.apply(this, arguments);
    };
    
    // 8. Audio Context Fingerprinting Evasion
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
        const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
        AudioContext.prototype.createAnalyser = function() {
            const analyser = originalCreateAnalyser.apply(this, arguments);
            const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
            analyser.getFloatFrequencyData = function(array) {
                originalGetFloatFrequencyData.apply(this, arguments);
                // Add minimal noise to audio fingerprint
                for (let i = 0; i < array.length; i++) {
                    if (Math.random() < 0.01) {
                        array[i] += (Math.random() - 0.5) * 0.0001;
                    }
                }
            };
            return analyser;
        };
    }
    
    // 9. Battery API evasion (if available)
    if (navigator.getBattery) {
        const originalGetBattery = navigator.getBattery;
        navigator.getBattery = function() {
            return originalGetBattery.apply(this, arguments).then(battery => {
                // Add small random variation to battery level
                const originalLevel = battery.level;
                Object.defineProperty(battery, 'level', {
                    get: () => {
                        const variation = (Math.random() - 0.5) * 0.01; // ±0.5%
                        return Math.max(0, Math.min(1, originalLevel + variation));
                    }
                });
                return battery;
            });
        };
    }
    
    // 10. Timezone evasion (add small random offset, but keep it consistent)
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    const timezoneOffset = originalGetTimezoneOffset.call(new Date());
    Date.prototype.getTimezoneOffset = function() {
        return timezoneOffset; // Keep consistent
    };
    
    // 11. Screen properties - make them look realistic
    Object.defineProperty(screen, 'availWidth', {
        get: () => window.innerWidth || 1920,
        configurable: true
    });
    Object.defineProperty(screen, 'availHeight', {
        get: () => window.innerHeight || 1080,
        configurable: true
    });
    
    // 12. Override toString methods to hide automation
    const originalToString = Function.prototype.toString;
    Function.prototype.toString = function() {
        if (this === navigator.webdriver) {
            return 'function webdriver() { [native code] }';
        }
        return originalToString.apply(this, arguments);
    };
    
    // 13. Hide automation indicators in window object
    Object.defineProperty(window, 'navigator', {
        value: navigator,
        writable: false,
        configurable: true
    });
    
    // 14. Override Notification permission
    if (Notification && Notification.permission === 'default') {
        Object.defineProperty(Notification, 'permission', {
            get: () => 'default',
            configurable: true
        });
    }
    
    // 15. Add realistic connection properties
    if (navigator.connection) {
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                downlink: 10,
                rtt: 50,
                saveData: false
            }),
            configurable: true
        });
    }
    
    // 16. Override deviceMemory if available
    if (navigator.deviceMemory) {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8, // Common value
            configurable: true
        });
    }
    
    // 17. Hardware concurrency - realistic values
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 4, // Common CPU core count
        configurable: true
    });
    
    // 18. Platform - ensure it matches user agent
    Object.defineProperty(navigator, 'platform', {
        get: () => {
            const ua = navigator.userAgent;
            if (ua.includes('Mac')) return 'MacIntel';
            if (ua.includes('Win')) return 'Win32';
            return 'Linux x86_64';
        },
        configurable: true
    });
    
    // 19. Override fetch to add realistic headers
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const [url, options = {}] = args;
        const headers = new Headers(options.headers || {});
        
        // Ensure realistic headers
        if (!headers.has('Accept-Language')) {
            headers.set('Accept-Language', 'es-ES,es;q=0.9,en;q=0.8');
        }
        
        options.headers = headers;
        return originalFetch.apply(this, [url, options]);
    };
    
    // 20. Override XMLHttpRequest for consistency
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
        this._url = url;
        return originalXHROpen.apply(this, [method, url, ...rest]);
    };
    
    // 21. Add realistic mouse event properties
    const originalMouseEvent = MouseEvent;
    window.MouseEvent = function(type, init) {
        if (init) {
            init.isTrusted = true;
        }
        return new originalMouseEvent(type, init);
    };
    
    // 22. Override getBoundingClientRect to prevent detection
    const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = function() {
        const rect = originalGetBoundingClientRect.apply(this, arguments);
        // Add tiny random offset (undetectable)
        return {
            ...rect,
            x: rect.x + (Math.random() - 0.5) * 0.001,
            y: rect.y + (Math.random() - 0.5) * 0.001
        };
    };
    
    // 23. Prevent detection via iframe
    Object.defineProperty(window, 'frames', {
        get: () => window,
        configurable: true
    });
    
    // 24. Override document properties
    Object.defineProperty(document, 'hidden', {
        get: () => false,
        configurable: true
    });
    
    Object.defineProperty(document, 'visibilityState', {
        get: () => 'visible',
        configurable: true
    });
    
    // 25. Add realistic touch support (for mobile user agents)
    if (navigator.userAgent.includes('Mobile')) {
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: () => 5,
            configurable: true
        });
    }
    
    // 26. Override console.debug to hide automation logs
    const originalConsoleDebug = console.debug;
    console.debug = function(...args) {
        // Filter out automation-related logs
        const message = args.join(' ');
        if (!message.includes('webdriver') && !message.includes('automation')) {
            originalConsoleDebug.apply(console, args);
        }
    };
    
    // 27. Prevent detection via performance timing
    const originalPerformanceNow = Performance.prototype.now;
    Performance.prototype.now = function() {
        return originalPerformanceNow.apply(this, arguments);
    };
    
    // 28. Override Notification constructor
    const OriginalNotification = window.Notification;
    window.Notification = function(title, options) {
        return new OriginalNotification(title, options);
    };
    window.Notification.prototype = OriginalNotification.prototype;
    window.Notification.permission = OriginalNotification.permission;
    window.Notification.requestPermission = OriginalNotification.requestPermission;
    
    // 29. Add realistic media devices
    if (navigator.mediaDevices) {
        const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
        navigator.mediaDevices.enumerateDevices = function() {
            return originalEnumerateDevices.apply(this, arguments).then(devices => {
                // Return devices with realistic properties
                return devices.map(device => ({
                    ...device,
                    deviceId: device.deviceId || 'default'
                }));
            });
        };
    }
    
    // 30. Final touch - ensure all overrides are persistent
    Object.freeze(navigator);
    Object.freeze(window.chrome || {});
    
})();
"""

def get_advanced_stealth_script() -> str:
    """Get the advanced anti-detection script"""
    return ADVANCED_STEALTH_SCRIPT


