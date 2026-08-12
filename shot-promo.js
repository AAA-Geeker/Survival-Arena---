// Social media promo screenshots for Survival Arena.
// Drives the real game, logs in, walks through every screen & feature, screenshots each step.
'use strict';
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUT = path.join(__dirname, 'screenshots');
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

const URL = 'https://survival-arena.com/';
const EMAIL = 'social-demo-' + Date.now().toString(36) + '@survival-arena.com';
const PASS = 'demo123456';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: { width: 900, height: 506 },  // landscape (16:9) so battle screen renders properly, not the "rotate" hint
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
  });
  const page = await ctx.newPage();

  const shot = async (name) => {
    const p = path.join(OUT, name + '.png');
    await page.screenshot({ path: p, fullPage: false });
    console.log('saved:', p);
  };

  // Tolerate network errors from game's Supabase polling quietly
  page.on('pageerror', (e) => console.log('[pageerror]', e.message));

  await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 }).catch(()=>{});
  await page.waitForTimeout(1500);
  // Login screen
  await shot('01-登录界面');

  // Switch to email login
  await page.click('button[data-type="email"]').catch(async ()=>{
    // fallback: click the email type button by text
    await page.click('.type-btn:has-text("邮箱")').catch(()=>console.log('no email type btn'));
  });
  await page.waitForTimeout(400);
  // Fill email + password
  try { await page.fill('#login-identifier', EMAIL); } catch(e){}
  try { await page.fill('#login-password', PASS); } catch(e){}
  try {
    await page.click('#btn-login-submit');
    console.log('submitted login');
  } catch(e){ console.log('login submit err', e.message); }

  // Wait for main menu
  await page.waitForSelector('#main-menu:not(.hidden)', { timeout: 15000 }).catch((e)=>console.log('no main menu:', e.message));
  await page.waitForTimeout(800);
  await shot('02-主菜单');

  // Shop / equipment & upgrades
  await page.click('#btn-shop-menu').catch(()=>{});
  await page.waitForTimeout(1200);
  await shot('03-装备与升级商店');

  // WeChat/QQ share won't exist shop; go back to menu then other tabs
  await page.click('#btn-shop-back').catch(()=>{});
  await page.waitForTimeout(500);

  // Daily rewards
  await page.click('#btn-daily').catch(()=>{});
  await page.waitForTimeout(900);
  await shot('04-每日奖励');
  await page.click('#btn-daily-back').catch(()=>{});
  await page.waitForTimeout(500);

  // Skins
  await page.click('#btn-skins').catch(()=>{});
  await page.waitForTimeout(900);
  await shot('05-皮肤系统');
  await page.click('#btn-skins-back').catch(()=>{});
  await page.waitForTimeout(500);

  // Leaderboard
  await page.click('#btn-leaderboard').catch(()=>{});
  await page.waitForTimeout(900);
  await shot('06-排行榜');
  await page.click('#btn-leaderboard-back').catch(()=>{});
  await page.waitForTimeout(500);

  // Start battle (landscape now — real battlefield renders)
  await page.click('#btn-play').catch(()=>{});
  await page.waitForTimeout(1200);
  // Demo mode: keep player invincible so the run lasts long enough to photograph
  // the real battlefield WITHOUT faking it — enemies still spawn & attack normally.
  await page.evaluate(() => { try { game.player.iframeTimer = 3600000; } catch(e){} });
  // Let enemies spawn in
  await page.waitForTimeout(6000);
  await shot('07-战斗画面WASD');
  await page.waitForTimeout(2000);

  // Pause menu — weapons tab active by default
  await page.keyboard.press('Escape').catch(()=>{});
  await page.waitForTimeout(700);
  await shot('08-暂停菜单装备');
  // Switch to upgrades tab
  await page.click('.pause-tab[data-pause-tab="upgrades"]').catch(()=>{});
  await page.waitForTimeout(500);
  await shot('09-暂停菜单升级');
  // Resume battle
  await page.click('.btn-resume, #btn-resume').catch(()=>{});
  await page.waitForTimeout(500);

  // Live battle in progress (more enemies have spawned)
  await page.waitForTimeout(8000);
  await shot('10-战斗进行中');

  // Friend revive modal (share to revive) — game is a top-level lexical binding, not window.game
  const hasGame = await page.evaluate(() => typeof game !== 'undefined');
  if (hasGame) {
    await page.evaluate(() => { try { game.showFriendModal(); } catch(e){ console.log('showFriendModal err', e.message); } });
    await page.waitForTimeout(900);
    await shot('11-好友复活分享');
  } else {
    console.log('game not exposed globally; skipping friend modal shot');
  }

  // Done.
  await browser.close();
  console.log('DONE. Screenshots in', OUT);
})().catch((e) => { console.error('FATAL', e); process.exit(1); });
