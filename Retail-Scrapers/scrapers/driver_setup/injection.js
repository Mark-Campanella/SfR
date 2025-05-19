// --- Full Stealth Patch for Chrome 135+ ---

// 1. navigator.webdriver
try {
  Object.defineProperty(Navigator.prototype, 'webdriver', {
    get: () => undefined,
    configurable: true
  });
  
  } catch (e) {
  console.warn('Could not redefine navigator.webdriver');
}


// 2. window.chrome.runtime
window.chrome = {
  runtime: {},
  loadTimes: () => ({}),
  csi: () => ({}),
};

// 3. navigator.languages
Object.defineProperty(navigator, 'languages', {
  get: () => ['pt-BR', 'pt'],
  configurable: true
});

// 4. navigator.plugins
navigator.__defineGetter__('plugins', function () {
  const fakePluginArray = {
    length: 3,
    0: { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
    1: { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
    2: { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
    item: function(index) { return this[index]; },
    namedItem: function(name) {
      return [...this].find(p => p.name === name);
    },
    [Symbol.iterator]: function* () {
      for (let i = 0; i < this.length; i++) yield this[i];
    }
  };
  Object.defineProperty(navigator, 'plugins', {
    get: () => fakePluginArray
  });
  Object.setPrototypeOf(fakePluginArray, PluginArray.prototype); // 🧠 key line
  
  return new Proxy([
    {
      name: 'Chrome PDF Plugin',
      filename: 'internal-pdf-viewer',
      description: 'Portable Document Format'
    },
    {
      name: 'Chrome PDF Viewer',
      filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
      description: ''
    },
    {
      name: 'Native Client',
      filename: 'internal-nacl-plugin',
      description: ''
    }
  ], {
    get(target, prop) {
      return Reflect.get(target, prop);
    }
  });
});

// 5. WebGL spoof
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(param) {
  const spoofed = {
    37445: 'Google Inc.',
    37446: 'ANGLE (Intel, Intel(R) UHD Graphics 620, D3D11)',
    7936: 'WebGL',
    7937: 'WebGL 2.0 (OpenGL ES 3.0 Chromium)',
  };
  return spoofed[param] || getParameter.call(this, param);
};

// 6. WebGL2 spoof
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

// 7. Canvas Fingerprint Noise (with randomness)
const getContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(type, ...args) {
  const ctx = getContext.call(this, type, ...args);
  if (!ctx) return ctx;
  const getImageData = ctx.getImageData;
  ctx.getImageData = function(...args) {
    const imageData = getImageData.apply(this, args);
    for (let i = 0; i < imageData.data.length; i += 4) {
      imageData.data[i] += Math.floor(Math.random() * 3);       // R
      imageData.data[i + 1] += Math.floor(Math.random() * 3);   // G
      imageData.data[i + 2] += Math.floor(Math.random() * 3);   // B
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

// 9. Hardware & Memory
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
Object.defineProperty(navigator, 'deviceMemory', { get: () => 4 });

// 10. userAgentData spoof
if (navigator.userAgentData) {
  try {
    Object.defineProperty(navigator, 'userAgentData', {
      get: () => ({
        brands: [
          { brand: "Chromium", version: "135" },
          { brand: "Google Chrome", version: "135" }
        ].sort((a, b) => a.brand.localeCompare(b.brand)),
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
  } catch (e) {
    console.warn('Could not redefine navigator.userAgentData');
  }
}

// 11. eval.toString() stealth
window.eval = new Proxy(window.eval, {
  apply: function(target, thisArg, args) {
    return Reflect.apply(...arguments);
  }
});
window.eval.toString = () => 'function eval() { [native code] }';

// 12. AudioContext fingerprint noise (adjusted)
const origGetChannelData = AudioBuffer.prototype.getChannelData;
AudioBuffer.prototype.getChannelData = function() {
  const results = origGetChannelData.apply(this, arguments);
  const noise = new Float32Array(results.length);
  for (let i = 0; i < results.length; i++) {
    noise[i] = results[i] + (Math.random() * 0.00001 - 0.000005);
  }
  return noise;
};

// 13. Timezone spoofing (extended)
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
Date.prototype.toString = new Proxy(Date.prototype.toString, {
  apply: function(target, thisArg, args) {
    return new Date(thisArg).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
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

// 15. Permissions spoof (extended)
const originalQuery = navigator.permissions.query;
navigator.permissions.query = function(parameters) {
  const name = parameters && parameters.name;
  if (['notifications', 'camera', 'microphone', 'geolocation', 'clipboard-read', 'clipboard-write', 'background-sync'].includes(name)) {
    return Promise.resolve({
      state: 'granted',
      onchange: null
    });
  }
  return originalQuery(parameters);
};

// Block detection of cdc_ objects
for (const key of Object.keys(window)) {
  if (key.match(/.+_+.+/g) && key.includes("cdc")) {
    try {
      delete window[key];
    } catch (e) {}
  }
}

// Fake React DevTools Hook
Object.defineProperty(window, '__REACT_DEVTOOLS_GLOBAL_HOOK__', {
  value: {},
  configurable: true
});



console.debug('✅ Full stealth patch injected and improved');
