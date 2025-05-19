(function () {
    'use strict';
  
    const defineGetter = (target, prop, getter) => {
      Object.defineProperty(target, prop, {
        get: getter,
        configurable: true
      });
    };
  
    const patchFunctionToString = () => {
      const nativeToString = Function.prototype.toString;
      const cache = new WeakMap();
  
      const safeToString = function () {
        if (cache.has(this)) return cache.get(this);
        if (typeof this === 'function' && this.name === '') {
          const str = `function () { [native code] }`;
          cache.set(this, str);
          return str;
        }
        return nativeToString.call(this);
      };
  
      Function.prototype.toString = new Proxy(nativeToString, {
        apply: (target, thisArg) => safeToString.call(thisArg),
        get: (target, prop) => Reflect.get(nativeToString, prop),
      });
    };
  
    const spoofWebGL = () => {
      const patch = (context, values) => {
        const original = context.prototype.getParameter;
        context.prototype.getParameter = function (param) {
          if (values.hasOwnProperty(param)) return values[param];
          return original.call(this, param);
        };
      };
  
      patch(WebGLRenderingContext, {
        37445: 'Google Inc.',               // UNMASKED_VENDOR_WEBGL
        37446: 'ANGLE (NVIDIA, ...)',       // UNMASKED_RENDERER_WEBGL
      });
  
      if (typeof WebGL2RenderingContext !== 'undefined') {
        patch(WebGL2RenderingContext, {
          37445: 'Google Inc.',
          37446: 'ANGLE (NVIDIA, ...)',
        });
      }
    };
  
    const spoofCanvas = () => {
      const originalGetContext = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (type, ...args) {
        const ctx = originalGetContext.call(this, type, ...args);
        if (!ctx || type !== '2d') return ctx;
  
        const originalGetImageData = ctx.getImageData;
        ctx.getImageData = function (...args) {
          const imageData = originalGetImageData.apply(this, args);
          for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] += Math.floor(Math.random() * 3);     // R
            imageData.data[i + 1] += Math.floor(Math.random() * 3); // G
            imageData.data[i + 2] += Math.floor(Math.random() * 3); // B
          }
          return imageData;
        };
  
        return ctx;
      };
    };
  
    const spoofAudio = () => {
      const orig = AudioBuffer.prototype.getChannelData;
      AudioBuffer.prototype.getChannelData = function () {
        const data = orig.apply(this, arguments);
        const noise = new Float32Array(data.length);
        for (let i = 0; i < data.length; i++) {
          noise[i] = data[i] + (Math.random() * 0.00001 - 0.000005);
        }
        return noise;
      };
    };
  
    const spoofNavigator = () => {
      defineGetter(Navigator.prototype, 'webdriver', () => undefined);
      defineGetter(navigator, 'languages', () => ['pt-BR', 'pt']);
      defineGetter(navigator, 'hardwareConcurrency', () => 4);
      defineGetter(navigator, 'deviceMemory', () => 4);
      defineGetter(navigator, 'maxTouchPoints', () => 1);
  
      // Fake plugins
      defineGetter(navigator, 'plugins', () => {
        const fakePlugins = [
          { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
          { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
          { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
        ];
        return Object.assign(fakePlugins, {
          length: 3,
          item: i => fakePlugins[i],
          namedItem: name => fakePlugins.find(p => p.name === name),
          [Symbol.iterator]: function* () {
            yield* fakePlugins;
          }
        });
      });
    };
  
    const spoofScreen = () => {
      defineGetter(window, 'screen', () => ({
        width: 1920,
        height: 1080,
        availWidth: 1920,
        availHeight: 1040,
        colorDepth: 24,
        pixelDepth: 24
      }));
      defineGetter(window, 'outerWidth', () => 1920);
      defineGetter(window, 'outerHeight', () => 1080);
      defineGetter(window, 'devicePixelRatio', () => 1);
    };
  
    const spoofUserAgentData = () => {
      if (!navigator.userAgentData) return;
      try {
        defineGetter(navigator, 'userAgentData', () => ({
          brands: [
            { brand: 'Chromium', version: '135' },
            { brand: 'Google Chrome', version: '135' }
          ],
          mobile: false,
          getHighEntropyValues: () => Promise.resolve({
            architecture: 'x86',
            model: '',
            platform: 'Windows',
            platformVersion: '10.0',
            uaFullVersion: '135.0.0.0',
            fullVersionList: [
              { brand: 'Chromium', version: '135.0.0.0' },
              { brand: 'Google Chrome', version: '135.0.0.0' }
            ]
          })
        }));
      } catch (e) {
        console.warn('userAgentData spoof failed');
      }
    };
  
    const spoofDateAndIntl = () => {
      Intl.DateTimeFormat = new Proxy(Intl.DateTimeFormat, {
        construct(target, args) {
          if (args[0] && typeof args[0] === 'object') {
            args[0].timeZone = 'America/Sao_Paulo';
          }
          return Reflect.construct(target, args);
        }
      });
  
      Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
        value: () => ({
          timeZone: 'America/Sao_Paulo',
          calendar: 'gregory',
          numberingSystem: 'latn',
          locale: 'pt-BR'
        })
      });
  
      Date.prototype.toString = new Proxy(Date.prototype.toString, {
        apply: (target, thisArg, args) => {
          return new Date(thisArg).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
        }
      });
    };
  
    const spoofPermissions = () => {
      const originalQuery = navigator.permissions.query;
      navigator.permissions.query = function (params) {
        const name = params?.name;
        if ([
          'notifications', 'camera', 'microphone',
          'geolocation', 'clipboard-read', 'clipboard-write'
        ].includes(name)) {
          return Promise.resolve({ state: 'granted', onchange: null });
        }
        return originalQuery.call(this, params);
      };
    };
  
    const patchCDC = () => {
      for (const key of Object.keys(window)) {
        if (/^.+_.+_.+/.test(key) && key.includes('cdc')) {
          try { delete window[key]; } catch (_) {}
        }
      }
    };
  
    const patchWorkers = () => {
      // NOTE: This is a placeholder — in real use, inject into Workers via blob rewriting.
      const originalWorker = window.Worker;
      window.Worker = new Proxy(Worker, {
        construct(target, args) {
          if (args.length && typeof args[0] === 'string') {
            const url = args[0];
            const patchedURL = URL.createObjectURL(new Blob([`
              (${arguments.callee.toString()})(); // reinject
            `], { type: 'application/javascript' }));
            return new target(patchedURL);
          }
          return new target(...args);
        }
      });
    };
  
    // Apply patches
    patchFunctionToString();
    spoofNavigator();
    spoofWebGL();
    spoofCanvas();
    spoofAudio();
    spoofScreen();
    spoofUserAgentData();
    spoofDateAndIntl();
    spoofPermissions();
    patchCDC();
    patchWorkers();
  
    console.debug('[🛡️] Full stealth injection loaded');
  
  })();
  