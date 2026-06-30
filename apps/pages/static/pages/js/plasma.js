(function () {
  var canvas = document.getElementById('plasma-canvas');
  if (!canvas) return;

  var ctx = canvas.getContext('2d');
  var W, H;
  var time = 0;
  var centerHue = 200;

  var titleEl = document.querySelector('.hero-title');
  var subEl = document.querySelector('.hero-sub');

  function resize() {
    W = canvas.width = window.innerWidth * window.devicePixelRatio;
    H = canvas.height = window.innerHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
  }

  resize();
  window.addEventListener('resize', resize);

  function hslToRgb(h, s, l) {
    h /= 360;
    s /= 100;
    l /= 100;
    if (s === 0) return [Math.round(l * 255), Math.round(l * 255), Math.round(l * 255)];
    var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    var p = 2 * l - q;
    function hue2rgb(t) {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    }
    return [
      Math.round(hue2rgb(h + 1 / 3) * 255),
      Math.round(hue2rgb(h) * 255),
      Math.round(hue2rgb(h - 1 / 3) * 255)
    ];
  }

  function rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(function (c) {
      return Math.min(255, Math.max(0, Math.round(c))).toString(16).padStart(2, '0');
    }).join('');
  }

  function draw() {
    var w = window.innerWidth;
    var h = window.innerHeight;
    var imageData = ctx.createImageData(W, H);
    var data = imageData.data;
    var hueSum = 0;
    var pixelCount = 0;

    for (var py = 0; py < H; py++) {
      var y = py / window.devicePixelRatio;
      for (var px = 0; px < W; px++) {
        var x = px / window.devicePixelRatio;
        var i = (py * W + px) * 4;

        // 8-wave plasma for rich organic detail
        var v1 = Math.sin(x * 0.004 + time * 0.25);
        var v2 = Math.sin(y * 0.006 + time * 0.20);
        var v3 = Math.sin((x + y) * 0.003 + time * 0.35);
        var v4 = Math.sin(Math.sqrt(x * x + y * y) * 0.010 + time * 0.15);
        var v5 = Math.sin((x * 0.6 - y * 0.4) * 0.005 + time * 0.30);
        var v6 = Math.sin(x * 0.010 + y * 0.015 + time * 0.22);
        var v7 = Math.sin((x * 0.3 + y * 0.7) * 0.007 + time * 0.18);
        var v8 = Math.sin(Math.pow(x * y, 0.3) * 0.002 + time * 0.28);

        var plasma = (v1 + v2 + v3 + v4 + v5 + v6 + v7 + v8) / 8;

        // Full spectral range: hue sweeps through all colors
        var hue = (plasma * 180 + time * 20) % 360;
        var sat = 80 + plasma * 15;
        var lit = 50 + plasma * 20;

        var rgb = hslToRgb(hue, sat, lit);
        data[i] = rgb[0];
        data[i + 1] = rgb[1];
        data[i + 2] = rgb[2];
        data[i + 3] = 230;

        // Sample center region for text glow color
        if (x > w * 0.4 && x < w * 0.6 && y > h * 0.4 && y < h * 0.6) {
          hueSum += hue;
          pixelCount++;
        }
      }
    }

    ctx.putImageData(imageData, 0, 0);

    // Update text glow based on center plasma hue
    if (pixelCount > 0) {
      centerHue = (hueSum / pixelCount) % 360;
    }

    var glowRgb = hslToRgb(centerHue, 90, 65);
    var compRgb = hslToRgb((centerHue + 180) % 360, 80, 55);
    var glowHex1 = rgbToHex(glowRgb[0], glowRgb[1], glowRgb[2]);
    var glowHex2 = rgbToHex(compRgb[0], compRgb[1], compRgb[2]);

    if (titleEl) {
      var spread1 = 40 + Math.sin(time * 0.5) * 20;
      var spread2 = 80 + Math.sin(time * 0.3) * 30;
      var spread3 = 120 + Math.sin(time * 0.4) * 40;
      titleEl.style.textShadow =
        '0 0 ' + spread1 + 'px ' + glowHex1 +
        ', 0 0 ' + spread2 + 'px ' + glowHex2 +
        ', 0 0 ' + spread3 + 'px rgba(255,255,255,0.08)';
    }

    if (subEl) {
      subEl.style.color = 'rgba(255, 255, 255, ' + (0.4 + Math.sin(time * 0.2) * 0.15) + ')';
    }

    time += 0.006;
    requestAnimationFrame(draw);
  }

  draw();
})();
