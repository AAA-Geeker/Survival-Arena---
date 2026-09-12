// 最终验收：模拟真实玩家路径（登录 → 皮肤商店 → 购买 → 装备 → 战斗）
'use strict';
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const OUT = path.join(__dirname, 'skin-preview');
const URL = 'http://127.0.0.1:8899/index.html';
const EMAIL = 'accept-' + Date.now().toString(36) + '@test.com';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1000, height: 720 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push('[pageerror] ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/ServiceWorker|SW registration/.test(m.text())) errs.push('[cerr] ' + m.text()); });

  console.log('1. 打开游戏');
  await page.goto(URL, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1200);

  console.log('2. 登录');
  await page.click('button[data-type="email"]').catch(()=>{});
  await page.waitForTimeout(200);
  await page.fill('#login-identifier', EMAIL).catch(()=>{});
  await page.fill('#login-password', 'demo123456').catch(()=>{});
  await page.click('#btn-login-submit').catch(()=>{});
  await page.waitForSelector('#main-menu:not(.hidden)', { timeout: 20000 }).catch(()=>{});
  await page.waitForTimeout(500);

  console.log('3. 给足钻石，测试购买流程');
  await page.evaluate(() => { try { game.gems = 1000; Storage.set('gems', 1000); } catch(e){} });

  console.log('4. 进入皮肤商店');
  await page.click('#btn-skins').catch(()=>{});
  await page.waitForTimeout(1500);

  // 检查卡片数量与稀有度
  const cardInfo = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('.skin-card'));
    return cards.map(c => ({
      skin: c.dataset.skin,
      rarity: Array.from(c.classList).find(x => x.startsWith('rarity-')),
      hasCanvas: !!c.querySelector('canvas'),
      price: c.querySelector('.skin-price')?.textContent?.trim(),
      tagline: c.querySelector('.skin-tagline')?.textContent?.trim(),
    }));
  });
  console.log('   卡片数:', cardInfo.length);
  cardInfo.forEach(c => console.log(`   ${c.skin.padEnd(8)} ${c.rarity.padEnd(16)} canvas=${c.hasCanvas} ${c.price}`));

  console.log('5. 购买烈焰使者（模拟确认）');
  page.once('dialog', d => { console.log('   确认框:', d.message().replace(/\n/g,' ')); d.accept(); });
  await page.click('[data-skin="flame"]').catch(()=>{});
  await page.waitForTimeout(900);
  const afterBuy = await page.evaluate(() => {
    const s = game.skins.find(x => x.id === 'flame');
    return { owned: s.owned, gems: game.gems };
  });
  console.log('   购买后 owned=', afterBuy.owned, 'gems=', afterBuy.gems);

  console.log('6. 装备霓虹战士');
  await page.click('[data-skin="neon"]').catch(()=>{});
  await page.waitForTimeout(900);
  const equipped = await page.evaluate(() => game.equippedSkin);
  console.log('   当前装备:', equipped);

  console.log('7. 开局战斗，验证皮肤渲染');
  await page.click('#btn-skins-back').catch(()=>{});
  await page.waitForTimeout(400);
  await page.click('#btn-play').catch(()=>{});
  await page.waitForTimeout(3500);

  const renderCheck = await page.evaluate(() => new Promise(res => {
    // 清空敌人，稳定帧，读玩家中心像素
    let n = 0;
    const iv = setInterval(() => {
      try {
        game.player.hp = game.player.maxHp; game.player.iframeTimer = 0; game.player.alive = true;
        game.player.x = canvas.width/2; game.player.y = canvas.height/2;
        game.shakeIntensity = 0; enemies.length = 0; projectiles.length = 0;
      } catch(e){}
      if (++n > 90) {
        clearInterval(iv);
        const g = canvas.getContext('2d');
        const px = Math.round(canvas.width/2), py = Math.round(canvas.height/2);
        const d = g.getImageData(px-10, py-10, 20, 20).data;
        let nonBg = 0;
        for (let i = 0; i < d.length; i += 4) {
          if (!(d[i] < 40 && d[i+1] < 45 && d[i+2] < 60)) nonBg++;
        }
        res({ skin: game.equippedSkin, nonBgPixels: nonBg, total: d.length/4, center: [d[0],d[1],d[2]] });
      }
    }, 16);
  }));
  console.log('   渲染验证:', JSON.stringify(renderCheck));

  console.log('8. 帧率');
  const fps = await page.evaluate(() => new Promise(res => {
    let n = 0; const t0 = performance.now();
    const tick = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(tick); else res(Math.round(n/((performance.now()-t0)/1000))); };
    requestAnimationFrame(tick);
  }));
  console.log('   FPS:', fps);

  console.log('\n=== 错误 ===');
  console.log(errs.length ? errs.slice(0,10).join('\n') : '无');

  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
