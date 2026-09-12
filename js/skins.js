// ============================================================
// SURVIVAL ARENA — Skin Rendering Engine (v1)
// ============================================================
// 程序化皮肤绘制引擎：零美术资源，全部用 Canvas 2D 绘制。
//
// 设计原则（对应皮肤策划案）：
//   1) 剪影优先 —— 先保证"一眼可辨认"，再谈好看
//   2) 分层构成 —— 每套皮肤由 底盘 / 描边 / 内核 / 发光 / 环饰 / 粒子 六层叠加
//   3) 稀有度用"动效密度"表达 —— 越贵动得越多，而不是单纯换个颜色
//   4) 性能预算 —— 玩家只有 1 个实体，可以给足特效；手机端自动降级
//
// 每套皮肤的绘制入口统一为 drawSkin(ctx, skin, t, radius)
// ============================================================

const SkinFX = {
  // 移动端降级：像素密度低 / 小屏时减少重特效
  get lowPower() {
    return window.innerWidth < 768;
  },
};

// ---------- 工具 ----------

// 缓存渐变对象，避免每帧创建（性能关键）
const _gradCache = new Map();
function radialGrad(ctx, key, x0, y0, r0, x1, y1, r1, stops) {
  if (SkinFX.lowPower) {
    // 低性能模式直接返回纯色（第一站）
    return stops[stops.length - 1][1];
  }
  const ck = key + '|' + r1.toFixed(1);
  let g = _gradCache.get(ck);
  if (!g) {
    g = ctx.createRadialGradient(x0, y0, r0, x1, y1, r1);
    stops.forEach(([p, c]) => g.addColorStop(p, c));
    _gradCache.set(ck, g);
  }
  return g;
}

function hexToRgba(hex, a) {
  const h = hex.replace('#', '');
  const n = parseInt(h.length === 3 ? h.split('').map(c => c + c).join('') : h, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}

// 正多边形路径（用于六边形、三角等"形状语言"）
function polyPath(ctx, sides, radius, rot = 0) {
  ctx.beginPath();
  for (let i = 0; i < sides; i++) {
    const a = rot + (i / sides) * Math.PI * 2 - Math.PI / 2;
    const x = Math.cos(a) * radius, y = Math.sin(a) * radius;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  }
  ctx.closePath();
}

// ============================================================
// 六套皮肤的绘制实现
// ============================================================
const SkinRenderers = {

  // ---------------------------------------------------------
  // 1. 默认战士 —— 干净的军事风，克制、清晰
  //    设计意图：不炫技，但要有"精良制式装备"的质感
  // ---------------------------------------------------------
  default(ctx, skin, t, r) {
    // 底盘：轻微的球体感（上亮下暗），避免死板的纯色圆
    ctx.fillStyle = radialGrad(ctx, 'def-base', -r * 0.3, -r * 0.35, r * 0.1, 0, 0, r, [
      [0, '#7ec8f0'], [0.55, skin.color], [1, '#1b5e8a'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();

    // 护甲环：一圈内嵌的暗色装甲线，让"战士"有装备感
    ctx.strokeStyle = hexToRgba('#0d1b2a', 0.55);
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.72, 0, Math.PI * 2); ctx.stroke();

    // 描边
    ctx.strokeStyle = skin.outline;
    ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();

    // 高光点：左上角一道弧，制造光源一致性
    ctx.strokeStyle = 'rgba(255,255,255,0.5)';
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.82, Math.PI * 1.05, Math.PI * 1.45); ctx.stroke();

    // 内核
    ctx.fillStyle = '#0d1b2a';
    ctx.beginPath(); ctx.arc(0, 0, r * 0.3, 0, Math.PI * 2); ctx.fill();
  },

  // ---------------------------------------------------------
  // 2. 烈焰使者 —— 火焰 / 熔岩主题
  //    设计意图：暖色 + 持续燃烧的粒子，表达"高温、狂暴"
  // ---------------------------------------------------------
  flame(ctx, skin, t, r) {
    const pulse = 1 + Math.sin(t * 0.006) * 0.05;

    // 外焰光晕（呼吸感）
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = radialGrad(ctx, 'flm-glow', 0, 0, r * 0.6, 0, 0, r * 1.9 * pulse, [
      [0, 'rgba(255,140,0,0.5)'], [0.5, 'rgba(255,70,0,0.18)'], [1, 'rgba(255,0,0,0)'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r * 1.9 * pulse, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // 底盘
    ctx.fillStyle = radialGrad(ctx, 'flm-base', -r * 0.25, -r * 0.3, r * 0.1, 0, 0, r, [
      [0, '#ffd166'], [0.45, skin.color], [1, '#7a1a00'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();

    // 熔岩裂纹：几条固定角度的"裂痕"，用亮橙色模拟熔岩渗出
    ctx.save();
    ctx.strokeStyle = '#ffca3a';
    ctx.lineWidth = 1.8;
    ctx.lineCap = 'round';
    ctx.shadowColor = '#ff6b00';
    ctx.shadowBlur = SkinFX.lowPower ? 0 : 8;
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 + t * 0.0006;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * r * 0.28, Math.sin(a) * r * 0.28);
      ctx.lineTo(Math.cos(a + 0.15) * r * 0.72, Math.sin(a + 0.15) * r * 0.72);
      ctx.stroke();
    }
    ctx.restore();

    // 描边
    ctx.strokeStyle = '#ff9e00';
    ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();

    // 核心：明亮的熔岩核
    ctx.fillStyle = radialGrad(ctx, 'flm-core', 0, 0, 0, 0, 0, r * 0.42, [
      [0, '#fff8e1'], [0.5, '#ffb703'], [1, '#ff6b00'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r * 0.42 * pulse, 0, Math.PI * 2); ctx.fill();
  },

  // ---------------------------------------------------------
  // 3. 暗影刺客 —— 潜行 / 虚空主题
  //    设计意图：关键难点是"暗色在暗背景上要看得见"。
  //    解法：不靠填充色，靠一圈冷紫描边 + 漂浮残影表达存在感。
  // ---------------------------------------------------------
  shadow(ctx, skin, t, r) {
    // 残影：三层不同透明度的暗影环，缓慢反向旋转（像影子在流动）
    ctx.save();
    for (let i = 0; i < 3; i++) {
      const a = t * 0.0012 * (i + 1);
      const rr = r * (1.35 + i * 0.22);
      ctx.strokeStyle = hexToRgba('#9d4edd', 0.28 - i * 0.08);
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.arc(0, 0, rr, a, a + Math.PI * 1.1);
      ctx.stroke();
    }
    ctx.restore();

    // 底盘：深色但带一点冷紫渐变，避免"糊成一团黑"
    ctx.fillStyle = radialGrad(ctx, 'shd-base', -r * 0.2, -r * 0.3, r * 0.1, 0, 0, r, [
      [0, '#4a3b6b'], [0.5, '#241a35'], [1, '#0d0716'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();

    // 描边：亮紫，这是它能在暗背景上被看见的关键
    ctx.save();
    ctx.strokeStyle = '#c77dff';
    ctx.lineWidth = 2.2;
    ctx.shadowColor = '#9d4edd';
    ctx.shadowBlur = SkinFX.lowPower ? 0 : 10;
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();

    // 面罩：一道横向的暗色切口，像刺客的眼罩，赋予"人形"暗示
    ctx.save();
    ctx.beginPath(); ctx.arc(0, 0, r * 0.98, 0, Math.PI * 2); ctx.clip();
    ctx.fillStyle = 'rgba(8,4,16,0.85)';
    ctx.fillRect(-r, -r * 0.22, r * 2, r * 0.44);
    // 面罩里两只会发光的眼睛
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = '#e0aaff';
    ctx.shadowColor = '#c77dff';
    ctx.shadowBlur = SkinFX.lowPower ? 0 : 12;
    const eyeA = t * 0.003;
    const ex = Math.cos(eyeA) * 0.5;
    ctx.beginPath(); ctx.arc(-r * 0.3 + ex, 0, r * 0.1, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(r * 0.3 + ex, 0, r * 0.1, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
    ctx.restore();
  },

  // ---------------------------------------------------------
  // 4. 黄金骑士 —— 尊贵 / 金属主题
  //    设计意图：用多段渐变模拟金属反射，而不是"黄色圆"
  //    金属感 = 明暗交替的环带（chrome 反射的简化表达）
  // ---------------------------------------------------------
  gold(ctx, skin, t, r) {
    // 外圈光晕（低强度的金色氤氲）
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = radialGrad(ctx, 'gld-glow', 0, 0, r * 0.8, 0, 0, r * 1.6, [
      [0, 'rgba(255,215,0,0.28)'], [1, 'rgba(255,215,0,0)'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r * 1.6, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // 金属感的核心：旋转的锥形渐变（conic gradient）
    // 真实金属 = 沿圆周交替的明暗反射带，而不是径向渐变。
    // Canvas 无原生 conic，用 24 个扇形逼近。
    ctx.save();
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.clip();
    const SEG = 24;
    const rot = (t * 0.00035) % (Math.PI * 2);
    for (let i = 0; i < SEG; i++) {
      const a0 = rot + (i / SEG) * Math.PI * 2;
      const a1 = rot + ((i + 1) / SEG) * Math.PI * 2;
      // 用余弦模拟 2 条主反射带 + 2 条副反射带
      const mid = (i + 0.5) / SEG * Math.PI * 2;
      const spec = Math.pow(Math.abs(Math.cos(mid * 2)), 2.2);        // 主反射
      const spec2 = Math.pow(Math.abs(Math.cos(mid * 4 + 0.6)), 6) * 0.5; // 副反射
      const l = Math.min(1, spec * 0.85 + spec2);
      // 从暗金到近白高光插值
      const cr = Math.round(120 + l * 135);
      const cg = Math.round(92 + l * 140);
      const cb = Math.round(24 + l * 130);
      ctx.fillStyle = `rgb(${cr},${cg},${cb})`;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, r, a0, a1);
      ctx.closePath();
      ctx.fill();
    }
    // 顶部方向的整体光照（让上亮下暗，光源一致）
    const lg = ctx.createLinearGradient(0, -r, 0, r);
    lg.addColorStop(0, 'rgba(255,246,210,0.34)');
    lg.addColorStop(0.5, 'rgba(255,255,255,0)');
    lg.addColorStop(1, 'rgba(60,40,0,0.42)');
    ctx.fillStyle = lg;
    ctx.fillRect(-r, -r, r * 2, r * 2);
    ctx.restore();

    // 骑士盔甲：护甲分片（4 块弧形甲板 + 缝隙），比"放射线"更像装备
    ctx.save();
    ctx.beginPath(); ctx.arc(0, 0, r * 0.88, 0, Math.PI * 2); ctx.clip();
    ctx.strokeStyle = 'rgba(74,54,10,0.9)';
    ctx.lineWidth = 2.4;
    for (let i = 0; i < 4; i++) {
      const a = rot * 1.4 + (i / 4) * Math.PI * 2 + Math.PI / 4;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
      ctx.stroke();
    }
    // 甲板边缘高光（每条缝隙旁一道亮边 = 立体凹槽）
    ctx.strokeStyle = 'rgba(255,240,190,0.5)';
    ctx.lineWidth = 1.1;
    for (let i = 0; i < 4; i++) {
      const a = rot * 1.4 + (i / 4) * Math.PI * 2 + Math.PI / 4 + 0.055;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(a) * r, Math.sin(a) * r);
      ctx.stroke();
    }
    ctx.restore();

    // 描边：双层（外圈亮金 + 内圈暗金）—— 边缘层次是"贵重"感的关键
    ctx.strokeStyle = '#7a5f1c';
    ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = '#fff3c4';
    ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.arc(0, 0, r - 1.2, 0, Math.PI * 2); ctx.stroke();

    // 核心：金色盾徽（六边形，形状语言 = 坚固/正面），带斜向明暗
    const hg = ctx.createLinearGradient(-r * 0.4, -r * 0.4, r * 0.4, r * 0.4);
    hg.addColorStop(0, '#fffbe8');
    hg.addColorStop(0.48, '#ffd85e');
    hg.addColorStop(0.52, '#c9992a');
    hg.addColorStop(1, '#8a6d1f');
    ctx.fillStyle = hg;
    polyPath(ctx, 6, r * 0.42, t * 0.0004);
    ctx.fill();
    ctx.strokeStyle = '#6b5217';
    ctx.lineWidth = 1.6;
    ctx.stroke();
    // 盾徽中心一颗宝石（红点 = 视觉焦点）
    ctx.fillStyle = '#d81b60';
    ctx.beginPath(); ctx.arc(0, 0, r * 0.1, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.beginPath(); ctx.arc(-r * 0.03, -r * 0.03, r * 0.035, 0, Math.PI * 2); ctx.fill();
  },

  // ---------------------------------------------------------
  // 5. 霓虹战士 —— 赛博 / 电子主题
  //    设计意图：最高对比度的一套，用 additive 混合做"发光体"
  //    这是"在 2D 里表达未来感"最有效的手法
  // ---------------------------------------------------------
  neon(ctx, skin, t, r) {
    // 底部能量光晕
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = radialGrad(ctx, 'neo-glow', 0, 0, r * 0.5, 0, 0, r * 2.0, [
      [0, 'rgba(0,255,136,0.42)'], [0.45, 'rgba(0,255,200,0.14)'], [1, 'rgba(0,255,136,0)'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r * 2.0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // 底盘：深色科技底
    ctx.fillStyle = '#04170f';
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();

    // 扫描线：横向细线向上流动，经典的"全息/CRT"语言
    ctx.save();
    ctx.beginPath(); ctx.arc(0, 0, r * 0.97, 0, Math.PI * 2); ctx.clip();
    ctx.globalCompositeOperation = 'lighter';
    const scanOffset = (t * 0.03) % 6;
    for (let y = -r; y < r; y += 6) {
      ctx.fillStyle = 'rgba(0,255,170,0.18)';
      ctx.fillRect(-r, y + scanOffset, r * 2, 1.5);
    }
    ctx.restore();

    // 电路环：两圈旋转的虚线环
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 5]);
    ctx.lineDashOffset = -t * 0.05;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.78, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([3, 7]);
    ctx.lineDashOffset = t * 0.06;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.55, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();

    // 描边：霓虹主色 + 发光
    ctx.save();
    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth = 2.4;
    ctx.shadowColor = '#00ff88';
    ctx.shadowBlur = SkinFX.lowPower ? 0 : 14;
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();

    // 核心：脉冲的能量核
    const coreS = r * (0.3 + Math.sin(t * 0.008) * 0.06);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = radialGrad(ctx, 'neo-core', 0, 0, 0, 0, 0, coreS, [
      [0, '#ffffff'], [0.4, '#7dffc4'], [1, 'rgba(0,255,136,0.1)'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, coreS, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  },

  // ---------------------------------------------------------
  // 6. 虚空领主 —— 终极皮肤（最高稀有度）
  //    设计意图：集大成 —— 紫黑虚空底 + 环绕的虚空碎片 + 吸积盘环
  //    "领主"要有压迫感和体量感，所以用最大的外延造型
  // ---------------------------------------------------------
  void(ctx, skin, t, r) {
    // 虚空吸积盘：三层旋臂，逆向旋转，营造"引力场"
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 3; i++) {
      const a0 = t * 0.0009 * (i % 2 === 0 ? 1 : -1.3) + i * 2.1;
      const rr = r * (1.45 + i * 0.3);
      ctx.strokeStyle = hexToRgba('#b388ff', 0.32 - i * 0.08);
      ctx.lineWidth = 2 - i * 0.4;
      ctx.beginPath();
      ctx.arc(0, 0, rr, a0, a0 + Math.PI * 0.7);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, rr, a0 + Math.PI, a0 + Math.PI * 1.7);
      ctx.stroke();
    }
    ctx.restore();

    // 虚空光晕
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = radialGrad(ctx, 'vod-glow', 0, 0, r * 0.6, 0, 0, r * 2.1, [
      [0, 'rgba(140,80,255,0.42)'], [0.5, 'rgba(90,20,180,0.16)'], [1, 'rgba(60,0,120,0)'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r * 2.1, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // 底盘：深紫到黑的虚空渐变
    ctx.fillStyle = radialGrad(ctx, 'vod-base', -r * 0.2, -r * 0.3, r * 0.1, 0, 0, r, [
      [0, '#6a3fb5'], [0.45, '#2a1245'], [1, '#08040f'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();

    // 虚空碎片：环绕的三角形碎片（形状语言 = 破碎/危险）
    ctx.save();
    for (let i = 0; i < 5; i++) {
      const a = t * 0.0016 + (i / 5) * Math.PI * 2;
      const dist = r * (1.1 + Math.sin(t * 0.004 + i) * 0.12);
      ctx.save();
      ctx.translate(Math.cos(a) * dist, Math.sin(a) * dist);
      ctx.rotate(a * 2 + t * 0.004);
      ctx.fillStyle = hexToRgba('#d0aaff', 0.85);
      ctx.shadowColor = '#b388ff';
      ctx.shadowBlur = SkinFX.lowPower ? 0 : 10;
      polyPath(ctx, 3, r * 0.15);
      ctx.fill();
      ctx.restore();
    }
    ctx.restore();

    // 描边：双色描边（外紫内粉），最厚重
    ctx.save();
    ctx.strokeStyle = '#d0aaff';
    ctx.lineWidth = 3;
    ctx.shadowColor = '#8c50ff';
    ctx.shadowBlur = SkinFX.lowPower ? 0 : 16;
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();
    ctx.strokeStyle = 'rgba(255,140,255,0.9)';
    ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.86, 0, Math.PI * 2); ctx.stroke();

    // 核心：奇点（会脉动的黑紫色核心）
    const coreR = r * (0.34 + Math.sin(t * 0.01) * 0.05);
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    ctx.fillStyle = radialGrad(ctx, 'vod-core', 0, 0, 0, 0, 0, coreR * 1.6, [
      [0, 'rgba(255,255,255,0.95)'], [0.35, 'rgba(200,140,255,0.7)'], [1, 'rgba(140,80,255,0)'],
    ]);
    ctx.beginPath(); ctx.arc(0, 0, coreR * 1.6, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  },
};

// ============================================================
// 统一入口
// ============================================================
function drawSkin(ctx, skin, t, radius) {
  const fn = SkinRenderers[skin.render] || SkinRenderers.default;
  ctx.save();
  fn(ctx, skin, t, radius);
  ctx.restore();
}

// 皮肤卡片的预览绘制（在小 canvas 上画，供商店使用）
function drawSkinPreview(canvasEl, skin, t) {
  const ctx = canvasEl.getContext('2d');
  const w = canvasEl.width, h = canvasEl.height;
  ctx.clearRect(0, 0, w, h);
  ctx.save();
  ctx.translate(w / 2, h / 2);
  const r = Math.min(w, h) * 0.30;
  const fn = SkinRenderers[skin.render] || SkinRenderers.default;
  fn(ctx, skin, t, r);
  ctx.restore();
}
