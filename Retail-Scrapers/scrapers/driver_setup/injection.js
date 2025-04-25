// --- Full Stealth Patch for Chrome 135+ ---

// 1. navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// 2. window.chrome.runtime
window.chrome = { runtime: {} };

// 3. navigator.languages
Object.defineProperty(navigator, 'languages', {
  get: () => ['pt-BR', 'pt']
});

// 4. navigator.plugins (fake plugin stubs)
Object.defineProperty(navigator, 'plugins', {
  get: () => [{
    name: 'Chrome PDF Plugin',
    filename: 'internal-pdf-viewer',
    description: 'Portable Document Format'
  }, {
    name: 'Chrome PDF Viewer',
    filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
    description: ''
  }, {
    name: 'Native Client',
    filename: 'internal-nacl-plugin',
    description: ''
  }]
});

// 5. WebGL
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(param) {
  const spoofed = {
    37445: 'Intel Inc.',
    37446: 'Intel Iris OpenGL Engine',
  };
  return spoofed[param] || getParameter.call(this, param);
};

// 6. WebGL2
if (typeof WebGL2RenderingContext !== 'undefined') {
  const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
  WebGL2RenderingContext.prototype.getParameter = function(param) {
    const spoofed = {
      37445: 'Intel Inc.',
      37446: 'Intel Iris OpenGL Engine',
    };
    return spoofed[param] || getParameter2.call(this, param);
  };
}

// 7. Canvas Fingerprint Noise
const getContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(type, ...args) {
  const ctx = getContext.call(this, type, ...args);
  if (!ctx) return ctx;
  const getImageData = ctx.getImageData;
  ctx.getImageData = function(...args) {
    const imageData = getImageData.apply(this, args);
    for (let i = 0; i < imageData.data.length; i += 4) {
      imageData.data[i] += 2;
      imageData.data[i + 1] += 2;
      imageData.data[i + 2] += 2;
    }
    return imageData;
  };
  return ctx;
};

// 8. TextMetrics / DOMRect Spoof
CanvasRenderingContext2D.prototype.measureText = new Proxy(CanvasRenderingContext2D.prototype.measureText, {
  apply: function(target, thisArg, args) {
    const metrics = Reflect.apply(target, thisArg, args);
    metrics.actualBoundingBoxAscent += 0.1;
    metrics.actualBoundingBoxDescent += 0.1;
    return metrics;
  }
});
Element.prototype.getBoundingClientRect = new Proxy(Element.prototype.getBoundingClientRect, {
  apply: function(target, thisArg, args) {
    const rect = Reflect.apply(target, thisArg, args);
    rect.x += 0.1;
    rect.y += 0.1;
    return rect;
  }
});

// 9. Hardware Concurrency & Device Memory
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
Object.defineProperty(navigator, 'deviceMemory', { get: () => 4 });

// 10. userAgentData spoof
if (navigator.userAgentData) {
  Object.defineProperty(navigator, 'userAgentData', {
    get: () => ({
      brands: [
        { brand: "Chromium", version: "135" },
        { brand: "Google Chrome", version: "135" }
      ],
      mobile: false,
      getHighEntropyValues: () => Promise.resolve({
        architecture: "x86",
        model: "",
        platform: "Windows",
        platformVersion: "10.0",
        uaFullVersion: "135.0.0.0",
        fullVersionList: [
          { brand: "Chromium", version: "135.0.0.0" },
          { brand: "Google Chrome", version: "135.0.0.0" }
        ]
      })
    })
  });
}

// 11. eval.toString() stealth
window.eval = new Proxy(window.eval, {
  apply: function(target, thisArg, args) {
    return Reflect.apply(...arguments);
  }
});
window.eval.toString = () => 'function eval() { [native code] }';

// 12. AudioContext fingerprint noise
const origGetChannelData = AudioBuffer.prototype.getChannelData;
AudioBuffer.prototype.getChannelData = function() {
  const results = origGetChannelData.apply(this, arguments);
  const noise = new Float32Array(results.length);
  for (let i = 0; i < results.length; i++) {
    noise[i] = results[i] + (Math.random() * 0.00001);
  }
  return noise;
};

// 13. Timezone & Intl spoofing
Intl.DateTimeFormat = new Proxy(Intl.DateTimeFormat, {
  construct: function(target, args) {
    if (args.length > 0 && args[0].timeZone) args[0].timeZone = 'America/Sao_Paulo';
    return new target(...args);
  }
});
Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
  value: function() {
    return {
      timeZone: 'America/Sao_Paulo',
      calendar: 'gregory',
      numberingSystem: 'latn',
      locale: 'pt-BR'
    };
  }
});

// 14. Screen / Touch spoofing
Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 });
Object.defineProperty(window, 'screen', {
  get: () => ({
    width: 1920,
    height: 1080,
    availWidth: 1920,
    availHeight: 1040,
    colorDepth: 24,
    pixelDepth: 24
  })
});
Object.defineProperty(window, 'outerWidth', { get: () => 1920 });
Object.defineProperty(window, 'outerHeight', { get: () => 1080 });
Object.defineProperty(window, 'devicePixelRatio', { get: () => 1 });

// ✅ Done
console.debug('✅ Full stealth patch injected');
