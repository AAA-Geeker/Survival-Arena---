// ============================================================
// MONETAG AD PROVIDER — Real Rewarded Video Ads for Web
// ============================================================
// This file sets window.__AD_PROVIDER__ before game.js loads.
// AdManager.detectEnv() picks it up and switches to web_sdk mode.
//
// Setup:
//   1. Register at https://monetag.com
//   2. Add your site, get the Site ID
//   3. Replace YOUR_SITE_ID below
//   4. Also update data-site-id in index.html <script> tag
//
// How it works:
//   - Shows the ad-modal with a 15-second countdown timer
//   - During the countdown, attempts to show Monetag ads (best-effort)
//   - Timer ALWAYS completes — anti-abuse enforcement
//   - If ads fail to load, UX is unchanged (timer still runs)
// ============================================================

const AD_CONFIG = {
  // --- REQUIRED: Replace with your Monetag Site ID ---
  siteId: 'YOUR_SITE_ID',

  // --- Ad duration in seconds (must match CFG.AD_DURATION in game.js) ---
  adDuration: 15,

  // --- Set to false to disable real ads (fallback to timer-only) ---
  monetagEnabled: true,

  // --- Show sponsor placeholder text during countdown ---
  showPlaceholder: true,
};

// ============================================================
// MonetagAdProvider
// ============================================================
const MonetagAdProvider = {
  _initialized: false,
  _interval: null,

  // --- Initialize ---
  init() {
    this._initialized = true;
    if (AD_CONFIG.monetagEnabled && typeof monetag !== 'undefined') {
      console.log('[MonetagAd] ✅ SDK detected, real ads enabled');
      console.log('[MonetagAd] Site ID:', AD_CONFIG.siteId);
    } else if (AD_CONFIG.monetagEnabled) {
      console.log('[MonetagAd] ⚠️ SDK not detected — timer-only mode (no ads)');
      console.log('[MonetagAd] Tip: Add the Monetag script tag to index.html');
    } else {
      console.log('[MonetagAd] 🔧 monetagEnabled=false — timer-only mode');
    }
  },

  // --- Always ready (timer-based approach) ---
  isReady() {
    return true;
  },

  // --- Show rewarded ad experience ---
  showRewardedVideo(callbacks) {
    const game = window._gameInstance;
    if (!game) {
      // No game instance — fallback to simple timer
      console.warn('[MonetagAd] No game instance, using simple timer');
      if (callbacks.onStart) callbacks.onStart();
      setTimeout(() => {
        if (callbacks.onComplete) callbacks.onComplete();
      }, AD_CONFIG.adDuration * 1000);
      return;
    }

    // Show the existing ad-modal UI
    game.showScreen('ad-modal');

    // Get DOM elements
    const fill = document.getElementById('ad-timer-fill');
    const text = document.getElementById('ad-timer-text');
    const placeholder = document.querySelector('.ad-placeholder');

    // Update placeholder content
    if (placeholder && AD_CONFIG.showPlaceholder) {
      placeholder.innerHTML = `
        <p style="font-size:1.5rem;margin-bottom:8px;">🎮 广告播放中...</p>
        <p style="font-size:0.85rem;color:#888;">请勿关闭此页面</p>
        <p class="small" style="margin-top:16px;">赞助商广告位</p>
      `;
    }

    // Notify game that ad experience started
    if (callbacks.onStart) callbacks.onStart();

    // --- Attempt to show Monetag ads (best-effort, non-blocking) ---
    if (AD_CONFIG.monetagEnabled) {
      this._attemptMonetagAds(placeholder);
    }

    // --- Start countdown timer (runs regardless of ad outcome) ---
    let remaining = AD_CONFIG.adDuration;
    if (text) text.textContent = '剩余 ' + remaining + ' 秒';
    if (fill) fill.style.width = '0%';

    this._interval = setInterval(() => {
      remaining--;
      const pct = ((AD_CONFIG.adDuration - remaining) / AD_CONFIG.adDuration) * 100;
      if (fill) fill.style.width = pct + '%';
      if (text) text.textContent = '剩余 ' + remaining + ' 秒';

      if (remaining <= 0) {
        clearInterval(this._interval);
        this._interval = null;

        // Hide the ad modal
        const modal = document.getElementById('ad-modal');
        if (modal) modal.classList.add('hidden');

        // Reward the user
        if (callbacks.onComplete) callbacks.onComplete();
      }
    }, 1000);
  },

  // --- Attempt Monetag ad displays (all try/catch wrapped) ---
  _attemptMonetagAds(placeholder) {
    if (typeof monetag === 'undefined') return;

    // Strategy 1: Popunder ad (opens in new window, doesn't interrupt game)
    try {
      if (typeof monetag.popunder === 'function') {
        monetag.popunder();
        console.log('[MonetagAd] 📺 Popunder ad triggered');
      } else if (typeof monetag.showPopunder === 'function') {
        monetag.showPopunder();
        console.log('[MonetagAd] 📺 Popunder ad triggered (showPopunder)');
      } else if (typeof monetag.pop === 'function') {
        monetag.pop();
        console.log('[MonetagAd] 📺 Pop ad triggered');
      }
    } catch (e) {
      console.log('[MonetagAd] Popunder ad not available:', e.message);
    }

    // Strategy 2: Native ad in placeholder area
    try {
      if (placeholder && typeof monetag.nativeAd === 'function') {
        monetag.nativeAd({
          container: placeholder,
          fallback: () => {
            console.log('[MonetagAd] Native ad no fill');
          },
        });
        console.log('[MonetagAd] 📺 Native ad requested for placeholder');
      }
    } catch (e) {
      console.log('[MonetagAd] Native ad not available:', e.message);
    }

    // Strategy 3: Push notification subscription prompt
    try {
      if (typeof monetag.pushNotification === 'function') {
        monetag.pushNotification();
        console.log('[MonetagAd] 🔔 Push notification prompt triggered');
      }
    } catch (e) {
      console.log('[MonetagAd] Push notification not available:', e.message);
    }

    // Strategy 4: Direct link / offer wall
    try {
      if (typeof monetag.directLink === 'function') {
        monetag.directLink();
        console.log('[MonetagAd] 🔗 Direct link ad triggered');
      }
    } catch (e) {
      console.log('[MonetagAd] Direct link not available:', e.message);
    }
  },

  // --- Cleanup (called if needed externally) ---
  destroy() {
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }
  },
};

// ============================================================
// Register the provider with AdManager
// AdManager.detectEnv() checks for window.__AD_PROVIDER__.showRewardedVideo
// ============================================================
window.__AD_PROVIDER__ = MonetagAdProvider;

console.log('[MonetagAd] Provider registered — AdManager will auto-detect on init');
