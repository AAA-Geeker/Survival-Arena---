# 广告接入指南

## 架构概览

```
AdManager (抽象层)
  ├── detectEnv()          # 自动检测运行环境
  ├── showRewardedVideo()  # 统一 API
  ├── isReady()            # 检查广告是否就绪
  └── getProviderName()    # 查看当前提供商
       │
       ├── SimulatedAdProvider   # 开发/演示（当前默认）
       ├── WeChatAdProvider      # 微信小游戏
       └── Web SDK Adapter       # Monetag / PropellerAds / 自定义
```

## 当前状态

**默认使用模拟广告**：15 秒倒计时，100% 完成率，适合开发和演示。

代码位置：`js/game.js` → `AdManager`（约 250 行）

---

## 方案一：接入微信小游戏广告（推荐）

### 适用场景
游戏部署在微信小游戏平台（微信内打开）

### 接入步骤

#### 1. 获取广告位 ID
登录 [微信公众平台](https://mp.weixin.qq.com) → 小程序管理 → 流量主 → 广告管理 → 新建激励视频广告位 → 复制广告位 ID

#### 2. 修改配置
在 `js/game.js` 中找到并替换：

```js
const AD_WECHAT_UNIT_ID = 'adunit-xxxxxxxxxxxxxxxx'; // 替换为你的真实 ID
```

#### 3. 完成
微信环境会自动检测 `wx.createRewardedVideoAd` API，无需其他改动。

### 收益参考
- 激励视频 eCPM：¥15-40
- 每次观看收入：约 ¥0.015-0.04

---

## 方案二：接入 Monetag（Web 独立站）

### 适用场景
游戏部署在独立域名（PC/手机浏览器打开）

### 接入步骤

#### 1. 注册账号
访问 [monetag.com](https://monetag.com) 注册 → 添加网站 → 获取 Site ID

#### 2. 添加 SDK
在 `index.html` 的 `<head>` 中添加 Monetag JS SDK：

```html
<script src="https://www.monetag.com/sdk.js" data-site-id="YOUR_SITE_ID"></script>
```

#### 3. 创建适配器
在 `index.html` 的 `<script>` 中添加（放在 Monetag SDK 之后）：

```html
<script>
// Monetag → AdManager adapter
window.__AD_PROVIDER__ = {
  init() {
    // Monetag auto-initializes via script tag
    console.log('[Ad] Monetag adapter ready');
  },
  isReady() { return true; },
  showRewardedVideo(callbacks) {
    // Monetag rewarded video API
    if (typeof monetag !== 'undefined' && monetag.showRewarded) {
      monetag.showRewarded({
        onComplete: function() {
          callbacks.onComplete();
        },
        onClose: function() {
          callbacks.onSkip();
        },
        onError: function(err) {
          callbacks.onError(err);
        }
      });
    } else {
      // Fallback to simulated
      callbacks.onError('Monetag SDK not loaded');
    }
  }
};
</script>
```

#### 4. 完成
`AdManager` 检测到 `window.__AD_PROVIDER__` 后自动切换。

### 收益参考
- 激励视频 eCPM：¥3-15（取决于地区）
- 每次观看收入：约 ¥0.003-0.015

---

## 方案三：接入 PropellerAds

与 Monetag 类似，注册 [propellerads.com](https://propellerads.com)，将适配器中的 API 调用替换为 PropellerAds 的对应方法即可。

---

## 方案四：自定义广告主（自建广告位）

### 适用场景
你有自己的广告主资源，想直接卖广告位

### 接入步骤

#### 1. 准备广告素材
- 视频文件（MP4，15-30 秒）
- 落地页链接

#### 2. 修改模拟广告
将 `SimulatedAdProvider.showRewardedVideo()` 中的倒计时改为真实视频播放：

```js
class SimulatedAdProvider {
  showRewardedVideo(callbacks) {
    // 播放真实广告视频
    const video = document.createElement('video');
    video.src = 'https://你的CDN/广告素材.mp4';
    video.autoplay = true;
    video.muted = false;
    video.playsInline = true;

    video.onended = () => callbacks.onComplete();
    video.onerror = () => callbacks.onError('Video load failed');

    // 显示视频在广告弹窗中
    const adContainer = document.getElementById('ad-modal');
    adContainer.querySelector('.ad-placeholder').appendChild(video);
  }
}
```

---

## 广告点位清单

| 点位 | 函数 | 类型 | 频次限制 | 优先级 |
|------|------|------|---------|--------|
| 死亡复活 | `watchAd()` | 激励视频 | 每局 1 次 | P0 已接入 |
| 每日奖励翻倍 | `watchAdForDoubleReward()` | 激励视频 | 每天 1 次 | P1 预留 |
| 死亡金币翻倍 | `watchAdForDoubleCoins()` | 激励视频 | 每局 1 次 | P2 预留 |

### 新增点位示例

在 `game.js` 中添加：

```js
// 看广告翻倍每日奖励
watchAdForDoubleReward() {
  AdManager.showRewardedVideo({
    onComplete: () => {
      const reward = this.getDailyReward();
      if (reward.coinAmount) this.coins += reward.coinAmount; // double
      if (reward.gems) this.gems += reward.gems;
      Storage.set('coins', this.coins);
      Storage.set('gems', this.gems);
      this.showToast('📺 奖励已翻倍！');
    },
    onError: () => {
      this.showToast('⚠️ 广告加载失败，请稍后再试');
    },
  });
},
```

---

## 测试方法

### 开发环境
```js
// 默认就是模拟广告，无需改动
// 15秒倒计时，100%完成率
```

### 强制切换提供商
在浏览器 Console 中：
```js
// 强制使用模拟广告
AdManager.init('simulated');

// 测试 Web SDK 模式（需要先设置 window.__AD_PROVIDER__）
AdManager.init('web_sdk');

// 查看当前提供商
AdManager.getProviderName();
```

### 模拟广告失败
```js
// 在 SimulatedAdProvider.showRewardedVideo() 开头添加：
// callbacks.onError('Test error'); return;
// 测试 fallback 逻辑是否正常
```

---

## 注意事项

1. **广告频次控制**：`CFG.MAX_REVIVES_PER_RUN = 1` 限制每局只能复活一次，广告自然受控
2. **用户体验**：`onError` 回调中给了自动复活（graceful degradation），线上可改为不奖励
3. **广告位审核**：微信/AdSense 需要应用通过审核后才能展示真实广告
4. **收益优化**：填充率低时建议同时接入多个广告平台做 waterfall
