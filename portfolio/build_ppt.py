"""
生成「生存竞技场 · 武器皮肤分析与创意策划案」作品集 PPT。
深色主题，与 HTML 作品集视觉一致。
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pathlib import Path
from PIL import Image

# ── 主题色（与游戏/HTML 一致）──
BG      = RGBColor(0x0A, 0x0A, 0x0F)
CARD    = RGBColor(0x16, 0x1A, 0x26)
CARD2   = RGBColor(0x1C, 0x21, 0x30)
LINE    = RGBColor(0x2A, 0x31, 0x44)
TEXT    = RGBColor(0xE8, 0xEB, 0xF2)
MUTED   = RGBColor(0x98, 0xA2, 0xB8)
DIM     = RGBColor(0x6B, 0x74, 0x88)
ACCENT  = RGBColor(0xE9, 0x45, 0x60)
ACCENT2 = RGBColor(0xFF, 0x6B, 0x8A)
GOLD    = RGBColor(0xF0, 0xC0, 0x40)
GEM     = RGBColor(0xA8, 0x55, 0xF7)
GREEN   = RGBColor(0x34, 0xD3, 0x99)
AMBER   = RGBColor(0xFB, 0xBF, 0x24)
BLUE    = RGBColor(0x60, 0xA5, 0xFA)

FONT = "微软雅黑"
BASE = Path(__file__).parent
ASSETS = BASE / "assets"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


def bg(slide, color=BG):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background(); s.shadow.inherit = False
    return s


def box(slide, l, t, w, h, fill=CARD, line=None, radius=None):
    shape = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line:
        s.line.color.rgb = line; s.line.width = Pt(0.75)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if radius:
        try: s.adjustments[0] = radius
        except Exception: pass
    return s


def text(slide, l, t, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         spacing=1.0, space_after=0):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if isinstance(runs, str):
        runs = [[(runs, 14, TEXT, False)]]
    first = True
    for line_runs in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align; p.line_spacing = spacing; p.space_after = Pt(space_after)
        for item in line_runs:
            txt, size, color, bold = item[0], item[1], item[2], item[3]
            r = p.add_run(); r.text = txt
            r.font.size = Pt(size); r.font.color.rgb = color
            r.font.bold = bold; r.font.name = FONT
    return tb


def accent_bar(slide, l, t, w=Inches(0.06), h=Inches(0.42), color=ACCENT):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background(); s.shadow.inherit = False
    return s


def header(slide, num, title, sub=None):
    accent_bar(slide, Inches(0.7), Inches(0.62))
    text(slide, Inches(0.92), Inches(0.58), Inches(11), Inches(0.3), [[(num, 12, ACCENT, True)]])
    text(slide, Inches(0.92), Inches(0.85), Inches(11.9), Inches(0.5), [[(title, 27, TEXT, True)]])
    y = Inches(1.42)
    if sub:
        text(slide, Inches(0.92), Inches(1.36), Inches(11.6), Inches(0.5),
             [[(sub, 12.5, MUTED, False)]], spacing=1.22)
        y = Inches(1.9)
    return y


def pic_fit(slide, path, l, t, max_w, max_h):
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w, h = int(iw * ratio), int(ih * ratio)
    left = l + int((max_w - w) / 2)
    top = t + int((max_h - h) / 2)
    return slide.shapes.add_picture(str(path), left, top, w, h)


def table(slide, l, t, w, col_w, heads, rows, row_h=Inches(0.5), head_h=Inches(0.42),
          colors=None, font_size=11):
    """简易表格：矩形背景 + 文本"""
    # 表头
    box(slide, l, t, w, head_h, fill=CARD2)
    cx = l + Inches(0.18)
    for h_, cw in zip(heads, col_w):
        text(slide, cx, t, Inches(cw), head_h, [[(h_, 10.5, DIM, True)]], anchor=MSO_ANCHOR.MIDDLE)
        cx += Inches(cw)
    y = t + head_h
    for i, row in enumerate(rows):
        box(slide, l, y, w, row_h, fill=(CARD if i % 2 == 0 else BG))
        cx = l + Inches(0.18)
        for j, (val, cw) in enumerate(zip(row, col_w)):
            col = TEXT if j == 0 else MUTED
            bold = (j == 0)
            if colors and colors.get(j):
                col = colors[j]
            text(slide, cx, y, Inches(cw), row_h, [[(val, font_size, col, bold)]],
                 anchor=MSO_ANCHOR.MIDDLE)
            cx += Inches(cw)
        y += row_h
    return y


# ══════════════════════════════════════════════
# 1. 封面
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
box(s, 0, 0, SW, Inches(0.05), fill=ACCENT)
text(s, Inches(1.0), Inches(1.35), Inches(6), Inches(0.3), [[("实践营课题一 · 游戏产品经理", 13, ACCENT2, True)]])
text(s, Inches(1.0), Inches(1.8), Inches(11.3), Inches(2.0),
     [[("生存竞技场 · 武器皮肤", 46, TEXT, True)],
      [("从审美洞察到商业化落地的完整链路", 25, ACCENT2, True)]],
     spacing=1.12, space_after=8)
text(s, Inches(1.0), Inches(3.85), Inches(9.9), Inches(1.2),
     [[("拆解主流射击游戏的皮肤设计方法论，再回到自己的项目《生存竞技场》，把一套「只有两个颜色的圆」", 13.5, MUTED, False)],
      [("的粗糙皮肤系统，重做成有分层结构、稀有度阶梯与商业化逻辑的皮肤体系。", 13.5, MUTED, False)],
      [("本方案包含：行业拆解报告 + 可直接落地的创意策划案 + 已上线的代码实现。", 13.5, MUTED, False)]],
     spacing=1.3)
chips = ["生存竞技场 Survival Arena", "纯 JS + Canvas 2D", "6 套皮肤 / 4 稀有度", "已实机验证"]
x = Inches(1.0)
for c in chips:
    w = Inches(0.42) + Emu(int(len(c) * 118000))
    box(s, x, Inches(5.5), w, Inches(0.42), fill=CARD, line=LINE, radius=0.35)
    text(s, x, Inches(5.5), w, Inches(0.42), [[(c, 11, MUTED, False)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    x += w + Inches(0.14)
text(s, Inches(1.0), Inches(6.5), Inches(11), Inches(0.3),
     [[("交付物：武器皮肤分析报告 + 针对本游戏的武器皮肤创意策划案", 12, MUTED, False)]])

# ══════════════════════════════════════════════
# 2. 起点：问题诊断
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
y = header(s, "01 / 起点", "皮肤系统为什么「粗糙」", "先定义问题，再谈方案——否则容易做成「好看但与商业无关」的美术练习")

box(s, Inches(0.92), Inches(2.05), Inches(11.5), Inches(1.85), fill=CARD, line=LINE, radius=0.04)
box(s, Inches(0.92), Inches(2.05), Inches(0.05), Inches(1.85), fill=ACCENT)
text(s, Inches(1.25), Inches(2.25), Inches(10.9), Inches(0.3),
     [[("改造前：一个皮肤 = 两个十六进制颜色", 15, TEXT, True)]])
text(s, Inches(1.25), Inches(2.68), Inches(10.9), Inches(0.4),
     [[("{ id:'flame', name:'烈焰使者', color:'#e74c3c', outline:'#c0392b', price:50 }", 12, ACCENT2, False)]])
text(s, Inches(1.25), Inches(3.12), Inches(10.9), Inches(0.7),
     [[("这两个值只被用在三处：圆的填充色、圆的描边色、中心小圆点的颜色。", 12, MUTED, False)],
      [("也就是说——六套皮肤，本质上是同一个圆换了六种颜色。", 12, TEXT, True)]],
     spacing=1.3)

stats = [("2 个", "每套皮肤的全部视觉变量", "填充色 + 描边色"),
         ("0 套", "有独立视觉概念的皮肤", "名字承诺了主题，视觉零兑现"),
         ("1 档", "定价梯度", "全部 50–150 钻，无价值分层")]
cw = Inches(3.71); gap = Inches(0.19); x0 = Inches(0.92)
for i, (num, lab, sub) in enumerate(stats):
    x = x0 + i * (cw + gap)
    box(s, x, Inches(4.15), cw, Inches(1.7), fill=CARD, line=LINE, radius=0.06)
    box(s, x, Inches(4.15), cw, Inches(0.045), fill=ACCENT)
    text(s, x + Inches(0.26), Inches(4.45), cw - Inches(0.5), Inches(0.55), [[(num, 27, TEXT, True)]])
    text(s, x + Inches(0.26), Inches(5.05), cw - Inches(0.5), Inches(0.3), [[(lab, 11.5, MUTED, False)]])
    text(s, x + Inches(0.26), Inches(5.35), cw - Inches(0.5), Inches(0.4), [[(sub, 10, DIM, False)]], spacing=1.15)

text(s, Inches(0.92), Inches(6.15), Inches(11.5), Inches(0.9),
     [[("本质不是「不好看」，而是三件事同时缺失：", 12.5, ACCENT2, True)],
      [("① 缺视觉识别（「暗影刺客」做成近黑色，而背景本身就是近黑，玩家看不见自己）", 12, MUTED, False)],
      [("② 缺价值阶梯（都只是换色，贵的凭什么贵？）    ③ 缺拥有感（买到的是色值，不是「额外投入」）", 12, MUTED, False)]],
     spacing=1.32)

# ══════════════════════════════════════════════
# 3. 前后对比
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "01 / 起点", "改造前后对比", "同样四套皮肤：左列是纯色圆，右列是分层渲染")

box(s, Inches(0.92), Inches(1.95), Inches(5.6), Inches(4.9), fill=CARD2, line=LINE, radius=0.03)
pic_fit(s, ASSETS / "before-after.png", Inches(1.04), Inches(2.07), Inches(5.36), Inches(4.2))
text(s, Inches(1.15), Inches(6.14), Inches(5.2), Inches(0.5),
     [[("改造前（纯色圆）", 12, MUTED, False)]], spacing=1.2)

text(s, Inches(7.0), Inches(2.05), Inches(5.4), Inches(0.4),
     [[("差别不是「画得更细」", 18, TEXT, True)]])
text(s, Inches(7.0), Inches(2.6), Inches(5.4), Inches(4.0),
     [[("改造前：", 12.5, ACCENT2, True),
       ("一个皮肤 = 两个色值。渲染时只有一个填充圆 + 一个描边圆 + 中心一个小点。", 12, MUTED, False)],
      [("", 8, MUTED, False)],
      [("改造后：", 12.5, GREEN, True),
       ("同一个半径内，由六层结构组成——可读性底衬、渐变底盘、脉动内核、发光描边、结构装饰、光效环饰。", 12, MUTED, False)],
      [("", 8, MUTED, False)],
      [("本质变化：", 12.5, GOLD, True),
       ("从「一个色值」变成了「一套设计」。这不只是更好看，而是让「稀有度」和「定价」第一次有了可以挂靠的物理载体——因为现在「更贵」可以意味着「多了几层」。", 12, MUTED, False)]],
     spacing=1.32, space_after=3)

# ══════════════════════════════════════════════
# 4. 行业拆解 - 稀有度
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "02 / 审美洞察", "拆解主流射击游戏的皮肤分级", "规律一：稀有度不只是颜色，而是一套「价值语言」")

rows = [("CS2", "7 档稀有度 × 5 档磨损 + StatTrak/Souvenir", "无官方定价，玩家市场成交", "三层正交叠加，制造可交易资产市场"),
        ("VALORANT", "Select/Deluxe/Premium/Exclusive/Ultra", "约 875 → 2,475 VP/件", "明码标价，档位决定解锁多少设计组件"),
        ("Fortnite", "Uncommon/Rare/Epic/Legendary", "约 800 → 2,000 V-Bucks", "颜色即稀有度，形成「越亮越贵」直觉"),
        ("Overwatch 2", "Common/Rare/Epic/Legendary", "约 1,000 → 1,900 Coins", "OW2 取消开箱，改为明码直售"),
        ("Apex Legends", "Common → Legendary + Mythic 传家宝", "传家宝需约 500 箱保底", "极端高客单道具拉高 ARPPU")]
table(s, Inches(0.92), Inches(1.95), Inches(11.5), [1.5, 3.5, 2.9, 3.6],
      ["游戏", "分级方式", "价格带", "核心机制"], rows,
      row_h=Inches(0.5), font_size=10.5)

box(s, Inches(0.92), Inches(5.05), Inches(11.5), Inches(1.35), fill=CARD, line=GEM, radius=0.05)
text(s, Inches(1.25), Inches(5.2), Inches(10.9), Inches(1.1),
     [[("可复用结论：", 12.5, GEM, True),
       ("稀有度的作用不是「分类」，而是让玩家一眼判断「这东西值多少钱」。CS2 用颜色（蓝→紫→粉→红→金）、", 11.5, MUTED, False)],
      [("VALORANT 用颜色+档位名，本质都是建立一套不看价格就能感知价值的符号系统。", 11.5, MUTED, False)],
      [("→ 所以自己的皮肤体系里，稀有度必须有独立视觉色，并贯穿卡片配色、描边强度、动效密度三层。", 11.5, GREEN, True)],
      [("数据来源：CS2 档位与色值经公开数据集 ByMykel/CSGO-API（2,126 条）实测核验；其余游戏价格带为行业公开常识，浮动，引用前请核对当日商店。", 9.5, DIM, False)]],
     spacing=1.28, space_after=2)

# ══════════════════════════════════════════════
# 5. 行业拆解 - 组件分层
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "02 / 审美洞察", "一款「完整皮肤」是可拆组件的集合", "规律二：档位 = 解锁层数。低档卖好看 → 中档卖手感 → 高档卖炫耀")

rows = [("基础材质 / 涂装", "让枪「好看」", "所有皮肤都有"),
        ("换弹 / 检视动画", "让枪「有手感」", "Premium 起"),
        ("配色变体 Colorway", "让玩家「能自定义」", "Premium 起（需额外解锁）"),
        ("专属音效 SFX", "听感差异化", "Deluxe 起"),
        ("特效 VFX（枪口/命中/弹道）", "战场存在感", "Premium / Exclusive 完整"),
        ("击杀横幅 / 终结技", "让对手看见 → 炫耀", "Exclusive 起"),
        ("等级进化 Reactive", "随击杀成长，绑定战绩", "Premium 起"),
        ("专属检视 / 唯一动画", "顶级身份象征", "Ultra 专属")]
table(s, Inches(0.92), Inches(1.95), Inches(11.5), [4.6, 3.7, 3.2],
      ["组件", "作用", "从哪档开始有"], rows, row_h=Inches(0.46), font_size=10.5)

box(s, Inches(0.92), Inches(5.9), Inches(11.5), Inches(1.1), fill=CARD, line=GREEN, radius=0.05)
text(s, Inches(1.25), Inches(6.05), Inches(10.9), Inches(0.85),
     [[("可复用结论：", 12.5, GREEN, True),
       ("分层逻辑是「低档卖好看 → 中档卖手感 → 高档卖炫耀」，每档对应一种心理需求。", 11.5, MUTED, False)],
      [("本项目无 3D 骨骼动画、无音效资产，能落地的「层」是：底盘质感 / 内核发光 / 结构装饰 / 能量光晕 / 环绕元素 / 动效密度。", 11.5, MUTED, False)]],
     spacing=1.3, space_after=2)

# ══════════════════════════════════════════════
# 6. 行业拆解 - 反应型皮肤 = 留存
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "02 / 审美洞察", "让皮肤「随你变强」——这是留存问题，不是审美问题",
       "规律三：把玩家的使用行为，外化成永久可见的视觉资产")

box(s, Inches(0.92), Inches(1.95), Inches(5.6), Inches(2.3), fill=CARD, line=LINE, radius=0.05)
box(s, Inches(0.92), Inches(1.95), Inches(0.05), Inches(2.3), fill=ACCENT)
text(s, Inches(1.22), Inches(2.15), Inches(5.0), Inches(0.35), [[("CS2 · StatTrak™", 15, TEXT, True)]])
text(s, Inches(1.22), Inches(2.6), Inches(5.0), Inches(1.5),
     [[("把击杀数永久刻在枪身上，只增不减。", 11.5, MUTED, False)],
      [("", 7, MUTED, False)],
      [("实测：2,126 条 CS2 皮肤中 1,274 条支持 StatTrak、1,456 条支持 Souvenir。", 11.5, MUTED, False)],
      [("", 7, MUTED, False)],
      [("玩家舍不得丢掉一把累积了 5,000 杀的枪——因为绑定了他的战绩。", 11.5, ACCENT2, False)]],
     spacing=1.3, space_after=2)

box(s, Inches(6.82), Inches(1.95), Inches(5.6), Inches(2.3), fill=CARD, line=LINE, radius=0.05)
box(s, Inches(6.82), Inches(1.95), Inches(0.05), Inches(2.3), fill=GEM)
text(s, Inches(7.12), Inches(2.15), Inches(5.0), Inches(0.35), [[("VALORANT · 反应型皮肤", 15, TEXT, True)]])
text(s, Inches(7.12), Inches(2.6), Inches(5.0), Inches(1.5),
     [[("Elderflame（Ultra）：击杀后巨龙张嘴，特效逐级增强。", 11.5, MUTED, False)],
      [("", 7, MUTED, False)],
      [("Reaver（Exclusive）：紫色能量随击杀累积增强。", 11.5, MUTED, False)],
      [("", 7, MUTED, False)],
      [("皮肤从「装饰品」变成了绑定使用历史的收藏品。", 11.5, ACCENT2, False)]],
     spacing=1.3, space_after=2)

box(s, Inches(0.92), Inches(4.5), Inches(11.5), Inches(2.2), fill=CARD, line=AMBER, radius=0.05)
text(s, Inches(1.25), Inches(4.75), Inches(10.9), Inches(1.8),
     [[("为什么这比「好看」更值钱", 14, AMBER, True)],
      [("", 8, MUTED, False)],
      [("纯静态皮肤带来的粘性是有限的——买完就结束了。真正能提升留存的，是让皮肤", 12, MUTED, False)],
      [("随玩家的行为而变化", 12, ACCENT2, True),
       ("：击杀数、存活时长、使用场次，都可以成为皮肤进化的输入。", 12, MUTED, False)],
      [("", 8, MUTED, False)],
      [("本项目原本完全没有这类机制，皮肤买完即是终点——这是它在留存设计上最大的空缺，也是我认为下一步最该补的。", 12, MUTED, False)]],
     spacing=1.32, space_after=2)

# ══════════════════════════════════════════════
# 7. 设计骨架：六层结构
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "03 / 创意策划案", "设计骨架：六层渲染结构", "所有皮肤共用同一套结构，按稀有度增减层的丰富度")

rows = [("L0 可读性底衬", "玩家身下的一圈半透明深色垫底", "敌人贴身围攻时，玩家剪影不被淹没（剪影优先）"),
        ("L1 底盘", "中心偏光源的径向渐变，而非纯色", "产生球体体积感，脱离「扁平圆」"),
        ("L2 内核", "高亮能核 + 呼吸脉动", "视觉焦点，让角色「像活的」"),
        ("L3 描边", "亮色/双色描边 + 发光", "暗色皮肤在暗背景上的可读性"),
        ("L4 结构装饰", "旋转六边盾徽 / 装甲分片 / 扫描线 / 电路环", "赋予主题，让皮肤「有内容」而非「有色块」"),
        ("L5 光效与环饰", "外围光晕、吸积盘旋臂、环绕碎片（加法混合）", "高级感与存在感，稀有度越高越丰富")]
table(s, Inches(0.92), Inches(1.95), Inches(11.5), [2.5, 4.4, 4.4],
      ["层", "内容", "解决的问题"], rows, row_h=Inches(0.63), font_size=10.5)

text(s, Inches(0.92), Inches(6.1), Inches(11.5), Inches(0.7),
     [[("这套结构的关键价值：", 12.5, GREEN, True),
       ("它让「第 7 套皮肤」的开发成本远低于「第 1 套」——因为规则可复用、可机械执行，", 11.5, MUTED, False)],
      [("「稀有度 = 层数」这样的商业规则也能被直接翻译成代码，不需要每次重新做美术决策。", 11.5, MUTED, False)]],
     spacing=1.3)

# ══════════════════════════════════════════════
# 8. 六套皮肤总览
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "03 / 创意策划案", "六套皮肤 · 真实游戏内渲染", "以下均为实机渲染截图，非设计稿；每套皮肤对应一个明确的视觉概念")

skins = [("skin-1-default.png", "制式战士", "普通", "#8FA3B8", "克制 / 基准款"),
         ("skin-2-flame.png", "烈焰使者", "稀有", "#4FC3F7", "高温与狂暴"),
         ("skin-3-shadow.png", "暗影刺客", "稀有", "#4FC3F7", "黑暗中的目光"),
         ("skin-4-neon.png", "霓虹战士", "史诗", "#C77DFF", "赛博能量体"),
         ("skin-5-gold.png", "黄金骑士", "史诗", "#C77DFF", "金属质感"),
         ("skin-6-void.png", "虚空领主", "传说", "#FFB703", "体量与压迫感")]
cw = Inches(1.83); gap = Inches(0.14); x0 = Inches(0.92)
for i, (fn, name, rar, color, concept) in enumerate(skins):
    x = x0 + i * (cw + gap)
    box(s, x, Inches(1.95), cw, Inches(3.4), fill=CARD, line=LINE, radius=0.05)
    # 稀有度顶部色条
    hx = color.lstrip('#')
    rc = RGBColor(int(hx[0:2],16), int(hx[2:4],16), int(hx[4:6],16))
    box(s, x, Inches(1.95), cw, Inches(0.05), fill=rc)
    pic_fit(s, ASSETS / fn, x + Inches(0.12), Inches(2.15), cw - Inches(0.24), Inches(2.1))
    text(s, x + Inches(0.14), Inches(4.4), cw - Inches(0.28), Inches(0.3), [[(name, 13, TEXT, True)]])
    text(s, x + Inches(0.14), Inches(4.72), cw - Inches(0.28), Inches(0.28), [[(rar, 10.5, rc, True)]])
    text(s, x + Inches(0.14), Inches(4.98), cw - Inches(0.28), Inches(0.32), [[(concept, 9.5, MUTED, False)]], spacing=1.15)

text(s, Inches(0.92), Inches(5.6), Inches(11.5), Inches(1.0),
     [[("设计原则：剪影优先 → 明度对比 → 内部细节 → 颜色", 13, ACCENT2, True)],
      [("在暗背景（#0b0d14）下，玩家真正感知的是「轮廓 + 亮度差」，色相只有约三成的辨识贡献。", 11.5, MUTED, False)],
      [("所以每套皮肤都先保证「一眼能认出自己」，再叠加主题装饰与发光——顺序颠倒就会做出「好看但认不出」的皮肤。", 11.5, MUTED, False)]],
     spacing=1.3)

# ══════════════════════════════════════════════
# 9. 单套精讲：暗影刺客（最难的取舍）
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "03 / 创意策划案", "最难的一套：暗影刺客怎么被看见", "当「名字要求它暗」与「背景本身就是暗的」正面冲突")

box(s, Inches(0.92), Inches(1.95), Inches(4.6), Inches(4.6), fill=CARD2, line=LINE, radius=0.03)
pic_fit(s, ASSETS / "preview-shadow.png", Inches(1.05), Inches(2.08), Inches(4.34), Inches(4.34))

text(s, Inches(6.0), Inches(2.0), Inches(6.4), Inches(0.4), [[("矛盾", 14, ACCENT, True)]])
text(s, Inches(6.0), Inches(2.4), Inches(6.4), Inches(1.1),
     [[("「暗影刺客」这个名字承诺的是「藏于黑暗」；但游戏的战场背景本身已经是 #0b0d14 的近黑色。", 12, MUTED, False)],
      [("做得越暗越贴合设定，就越看不见自己——这是可读性事故，不是审美问题。", 12, MUTED, False)]],
     spacing=1.3)

text(s, Inches(6.0), Inches(3.7), Inches(6.4), Inches(0.4), [[("解法：换一个维度，而不是把暗色调亮", 14, GREEN, True)]])
text(s, Inches(6.0), Inches(4.1), Inches(6.4), Inches(2.4),
     [[("· 放弃用「填充色」表达存在感，改用「光」：", 11.5, MUTED, False)],
      [("   冷紫发光描边（#c77dff）+ 三道缓慢流动的残影", 11.5, MUTED, False)],
      [("· 用「面罩下两个浮动光点」制造「有人在黑暗里盯着你」的叙事感", 11.5, MUTED, False)],
      [("· 底盘仍保留深紫渐变，不破坏「暗影」的设定", 11.5, MUTED, False)],
      [("", 8, MUTED, False)],
      [("→ 名字承诺「暗影」，视觉给的是「黑暗中盯着你的眼睛」——设定没丢，可读性拿到了。", 12, GREEN, True)]],
     spacing=1.3, space_after=2)

# ══════════════════════════════════════════════
# 10. 单套精讲：黄金骑士（金属的做法）
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "03 / 创意策划案", "一次真实的返工：金属感到底怎么做", "初版做成了「黄色的饼」，因为搞错了金属的本质")

box(s, Inches(0.92), Inches(1.95), Inches(4.6), Inches(4.6), fill=CARD2, line=LINE, radius=0.03)
pic_fit(s, ASSETS / "preview-gold.png", Inches(1.05), Inches(2.08), Inches(4.34), Inches(4.34))

text(s, Inches(6.0), Inches(2.0), Inches(6.4), Inches(0.4), [[("初版为什么失败", 14, ACCENT, True)]])
text(s, Inches(6.0), Inches(2.4), Inches(6.4), Inches(0.95),
     [[("第一版用径向渐变做「上亮下暗」，结果得到的是一个扁平、哑光、像塑料饼的圆。", 12, MUTED, False)],
      [("原因：金属的关键不是「颜色是金色」，而是「沿圆周交替出现的明暗反射带」。", 12, MUTED, False)]],
     spacing=1.3)

text(s, Inches(6.0), Inches(3.55), Inches(6.4), Inches(0.4), [[("第二版的做法", 14, GREEN, True)]])
text(s, Inches(6.0), Inches(3.95), Inches(6.4), Inches(2.6),
     [[("· Canvas 没有原生锥形渐变（conic gradient），用 24 个扇形拼接逼近", 11.5, MUTED, False)],
      [("· 用余弦函数模拟 2 条主反射带 + 2 条副反射带，形成明暗交替", 11.5, MUTED, False)],
      [("· 叠加一层自上而下的整体光照，保证光源方向一致", 11.5, MUTED, False)],
      [("· 加四片护甲分片与缝隙高光，把「圆」变成「甲」", 11.5, MUTED, False)],
      [("· 中央六边形盾徽 + 宝石作为视觉焦点", 11.5, MUTED, False)],
      [("", 8, MUTED, False)],
      [("→ 这套做法可复用到任何「需要金属感」的皮肤，是本次沉淀下来的技术资产。", 12, GREEN, True)]],
     spacing=1.3, space_after=2)

# ══════════════════════════════════════════════
# 11. 真实用户数据看板
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "03.5 / 数据验证", "真实用户数据看板",
       "关键行为全部客户端埋点 → Supabase 落库 → 看板实时聚合；以下取自生产环境实际数据")

stats = [("79 人", "累计独立玩家", "去重 player_id"),
         ("133 局", "累计开局对局", "真实对局数"),
         ("1,996 条", "累计埋点事件", "覆盖 24 个活跃日"),
         ("56 次", "复活次数", "复活率 42%"),
         ("31 笔", "商店购买", "付费意愿验证"),
         ("37%", "移动端事件占比", "双端适配验证")]
cw = Inches(1.83); gap = Inches(0.14); x0 = Inches(0.92)
for i, (num, lab, sub) in enumerate(stats):
    # 两行三列
    col, row = i % 3, i // 3
    x = x0 + col * (cw + gap)
    y = Inches(1.85) + row * Inches(1.15)
    box(s, x, y, cw, Inches(1.0), fill=CARD, line=LINE, radius=0.06)
    box(s, x, y, cw, Inches(0.045), fill=ACCENT)
    text(s, x + Inches(0.22), y + Inches(0.16), cw - Inches(0.4), Inches(0.4), [[(num, 24, TEXT, True)]])
    text(s, x + Inches(0.22), y + Inches(0.56), cw - Inches(0.4), Inches(0.22), [[(lab, 10.5, MUTED, False)]])

box(s, Inches(6.82), Inches(1.85), Inches(5.6), Inches(2.15), fill=CARD2, line=LINE, radius=0.03)
pic_fit(s, ASSETS / "dashboard.png", Inches(6.95), Inches(1.95), Inches(5.34), Inches(1.95),)

box(s, Inches(0.92), Inches(4.2), Inches(11.5), Inches(2.6), fill=CARD, line=LINE, radius=0.04)
text(s, Inches(1.25), Inches(4.4), Inches(10.9), Inches(2.3),
     [[("从数据里读到的三件事", 14, ACCENT2, True)],
      [("", 7, MUTED, False)],
      [("① 双端适配真的有人在用 ", 12, TEXT, True),
       ("— 移动端 UA 产生 275 条事件、桌面端 725 条，「手机+电脑都能玩」不是宣传语。", 11.5, MUTED, False)],
      [("② 复活机制是被真实使用的核心循环 ", 12, TEXT, True),
       ("— 56 次复活中，看广告 38% / 花钻石 25% / 用令牌 21% / 好友助力 16%，四条路径都有人走。", 11.5, MUTED, False)],
      [("③ 武器使用率 81% 集中在手枪 ", 12, TEXT, True),
       ("— 最有价值的负面发现：手枪是免费初始武器，说明多数玩家没走到解锁新武器的波次就阵亡了。", 11.5, MUTED, False)],
      [("", 7, MUTED, False)],
      [("数据诚实性：", 10.5, AMBER, True),
       ("死亡波次分布中「第 1 波 109 次」包含开发与自动化测试数据，不能当作真实难度曲线；场均时长同受测试会话影响。", 10.5, DIM, False)],
      [("玩家数 / 开局数 / 复活数 / 购买数均为按事件去重的真实累计值；比率类指标仅作趋势参考。", 10.5, DIM, False)]],
     spacing=1.3, space_after=2)

# ══════════════════════════════════════════════
# 12. 商店 UI 改造
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "03 / 创意策划案", "商店界面：让玩家在买之前就看到「动起来的样子」",
       "每张卡片用独立 canvas 实时渲染真实皮肤，而不是一张静态截图")

box(s, Inches(0.92), Inches(1.95), Inches(4.5), Inches(4.7), fill=CARD2, line=LINE, radius=0.03)
pic_fit(s, ASSETS / "skins-shop.png", Inches(1.03), Inches(2.05), Inches(4.28), Inches(4.5))

text(s, Inches(5.9), Inches(2.0), Inches(6.5), Inches(0.4), [[("这次改造做了四件事", 14, ACCENT2, True)]])
text(s, Inches(5.9), Inches(2.45), Inches(6.5), Inches(4.2),
     [[("① 实时动效预览", 12.5, TEXT, True)],
      [("每张卡片挂一个独立 canvas，跑同一套渲染逻辑。静态格子立刻变成「活的」，玩家买前就能预判效果。", 11.5, MUTED, False)],
      [("", 8, MUTED, False)],
      [("② 稀有度视觉化", 12.5, TEXT, True)],
      [("稀有度不只写在名字里：卡片顶部有稀有度色条、角标、以及史诗/传说专属的底纹晕光，形成「稀有物品」的价值暗示。", 11.5, MUTED, False)],
      [("", 8, MUTED, False)],
      [("③ 主题文案", 12.5, TEXT, True)],
      [("每套皮肤配一句人话描述（如「你只会看到它的眼睛」），把「参数」翻译成「想象」，提升点击意愿。", 11.5, MUTED, False)],
      [("", 8, MUTED, False)],
      [("④ 明确的装备状态", 12.5, TEXT, True)],
      [("「✓ 使用中 / 点击装备 / 💎 价格」三态清晰，并给出「钻石不足，还差 N 颗」的精确提示，减少无效点击。", 11.5, MUTED, False)]],
     spacing=1.25, space_after=2)

# ══════════════════════════════════════════════
# 12. 定价重构
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "04 / 商业化落地", "定价重构：从「无梯度」到「四档阶梯」",
       "核心逻辑：价格严格对齐动效密度——多花一档的钱，确实多买到一层动态")

rows = [("普通", "制式战士", "免费", "静态", "基准锚点，让所有付费皮肤显得「有理由贵」"),
        ("稀有", "烈焰使者 / 暗影刺客", "60 💎", "1 项动效", "首充档：小额即可获得的第一个「升级感」"),
        ("史诗", "霓虹战士 / 黄金骑士", "90–120 💎", "2–3 项动效", "主力档：品质明显跃升，承接大部分付费"),
        ("传说", "虚空领主", "200 💎", "全套动效 + 最大视觉半径", "向往型顶点：制造「看到别人拥有」的落差")]
table(s, Inches(0.92), Inches(2.0), Inches(11.5), [1.2, 3.3, 1.7, 2.5, 2.8],
      ["稀有度", "皮肤", "价格", "动效密度", "定价意图"], rows,
      row_h=Inches(0.72), font_size=10.5)

box(s, Inches(0.92), Inches(5.35), Inches(11.5), Inches(1.55), fill=CARD, line=GOLD, radius=0.05)
text(s, Inches(1.25), Inches(5.55), Inches(10.9), Inches(1.25),
     [[("为什么这样定价", 13, GOLD, True)],
      [("原方案 50/50/75/100/150 的梯度太平缓，且与视觉质量无关，玩家无法判断「贵在哪」。", 11.5, MUTED, False)],
      [("重构后，价格严格对齐动效密度——这让加价变得可解释，也给了玩家升级的理由。", 11.5, MUTED, False)],
      [("→ 这既是定价策略，也是定价诚信：如果高稀有皮肤和低稀有在体验上没区别，高价就是在收智商税，短期能赚、长期摧毁信任。", 11.5, ACCENT2, True)]],
     spacing=1.3, space_after=2)

# ══════════════════════════════════════════════
# 13. 技术实现与验证
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "04 / 商业化落地", "技术实现与实机验证")

box(s, Inches(0.92), Inches(1.9), Inches(5.6), Inches(4.9), fill=CARD, line=LINE, radius=0.05)
text(s, Inches(1.22), Inches(2.1), Inches(5.0), Inches(0.35), [[("技术实现要点", 15, TEXT, True)]])
text(s, Inches(1.22), Inches(2.6), Inches(5.0), Inches(4.0),
     [[("零美术资源", 12, ACCENT2, True)],
      [("全部用 Canvas 2D 程序化绘制。项目没有图片资源管线，程序化是唯一可行路径，且天然适配任意分辨率与移动端。", 11, MUTED, False)],
      [("", 7, MUTED, False)],
      [("渐变对象缓存", 12, ACCENT2, True)],
      [("每帧 createRadialGradient 会触发 GC 抖动，改为按皮肤 key 缓存。", 11, MUTED, False)],
      [("", 7, MUTED, False)],
      [("移动端降级", 12, ACCENT2, True)],
      [("小屏自动关闭最贵的 shadowBlur 发光，只保留基础分层。", 11, MUTED, False)],
      [("", 7, MUTED, False)],
      [("状态不泄漏", 12, ACCENT2, True)],
      [("整体 save/restore 包裹，globalCompositeOperation 改后必还原，避免污染后续绘制。", 11, MUTED, False)],
      [("", 7, MUTED, False)],
      [("可读性底衬", 12, ACCENT2, True)],
      [("皮肤下层加半透明深色垫底，解决「敌人围攻时玩家被淹没」。", 11, MUTED, False)]],
     spacing=1.25, space_after=2)

box(s, Inches(6.82), Inches(1.9), Inches(5.6), Inches(4.9), fill=CARD, line=GREEN, radius=0.05)
text(s, Inches(7.12), Inches(2.1), Inches(5.0), Inches(0.35), [[("实机验证结果", 15, GREEN, True)]])
text(s, Inches(7.12), Inches(2.6), Inches(5.0), Inches(4.0),
     [[("六套皮肤全部渲染正确", 12, GREEN, True)],
      [("逐一读取玩家中心像素验证，中心色分别为蓝/橙/紫/绿/金/紫罗兰，与设计一致，无一套渲染空白。", 11, MUTED, False)],
      [("", 7, MUTED, False)],
      [("可读性修复生效", 12, GREEN, True)],
      [("引入底衬后，敌人贴身围攻时玩家中心区域的敌方红色像素由「淹没」降至 0。", 11, MUTED, False)],
      [("", 7, MUTED, False)],
      [("帧率达标", 12, GREEN, True)],
      [("最重的「虚空领主」在无头浏览器纯 CPU 渲染下实测 58–60 FPS，真机 GPU 更宽裕。", 11, MUTED, False)],
      [("", 7, MUTED, False)],
      [("旧存档兼容", 12, GREEN, True)],
      [("增加字段回填逻辑，老玩家的皮肤存档不会因数据结构升级而失效。", 11, MUTED, False)]],
     spacing=1.25, space_after=2)

# ══════════════════════════════════════════════
# 14. 观点 1-2
# ══════════════════════════════════════════════
def viewpoint_slide(label, q, title, arg, infer, result):
    sl = prs.slides.add_slide(BLANK); bg(sl)
    header(sl, label, "我的观点", "什么样的皮肤设计能吸引用户、增加粘性")
    box(sl, Inches(0.92), Inches(1.95), Inches(11.5), Inches(4.85), fill=CARD, line=LINE, radius=0.04)
    box(sl, Inches(0.92), Inches(1.95), Inches(0.05), Inches(4.85), fill=ACCENT)
    text(sl, Inches(1.35), Inches(2.15), Inches(10.7), Inches(0.35), [[(q, 12.5, ACCENT2, True)]])
    text(sl, Inches(1.35), Inches(2.55), Inches(10.7), Inches(0.5), [[(title, 22, TEXT, True)]])
    text(sl, Inches(1.35), Inches(3.2), Inches(10.7), Inches(3.4),
         [[("论据", 12, BLUE, True)], [(arg, 12, MUTED, False)],
          [("", 9, MUTED, False)],
          [("推论", 12, BLUE, True)], [(infer, 12, MUTED, False)],
          [("", 9, MUTED, False)],
          [("→ " + result, 12, GREEN, True)]],
         spacing=1.33, space_after=4)
    return sl

viewpoint_slide(
    "05 / 我的观点 · 观点一", "皮肤卖的不是美术，是「可被看见的自我」",
    "可见性决定价值，而不是精细度",
    "CS2 的 AWP | Dragon Lore 能拍到数万美元，不是因为它画得比别的枪细致十倍，而是因为它稀有、可交易、且能被别人看到。VALORANT 把最贵的皮肤做了「击杀横幅」——因为击杀瞬间是全场注意力最集中的时刻，是炫耀半径最大的设计点位。",
    "设计皮肤前要先问「谁会看到它」。对俯视角游戏，别人看到你的方式只有一处：你的角色在战场上长什么样。所以我优先投入的是「角色剪影的辨识度」，而不是细节堆砌。反过来，一款皮肤做得再精致，但混战中认不出来，它的社交价值就是零。",
    "落地：把「剪影优先」作为第一原则，专门为解决可读性写了底衬层，而不是先加光效。")

viewpoint_slide(
    "05 / 我的观点 · 观点二", "稀有度的本质是「可解释的价值差」",
    "玩家愿意为「看得见的额外投入」付费",
    "行业里所有成熟的皮肤分级（CS2 的颜色七档、VALORANT 的五档）都有共同点：高稀有皮肤确实多了东西——更多动画、更多特效、更独特的音效。稀有度是对「产品方多投入了成本」的诚实兑现，玩家感受到的不是「你收我更多钱」，而是「这套确实更用心」。",
    "如果高稀有和低稀有在体验上没有本质区别，高价就是在收智商税，短期能赚、长期摧毁玩家对定价的信任。所以我把价格严格绑定动效密度：多花 30 钻石，一定多看到一层动态。这不是美术偏好，是定价诚信。",
    "落地：稀有度同时驱动卡片配色、描边强度、动效数量三个维度，让「贵」在视觉上可被验证。")

viewpoint_slide(
    "05 / 我的观点 · 观点三", "真正的粘性来自「皮肤绑定战绩」，而不是皮肤好看",
    "把使用行为外化成资产，才能制造沉没成本",
    "CS2 的 StatTrak 计数器是最聪明的留存设计之一——它让「枪」与「我的击杀历史」绑定，只增不减。玩家舍不得丢弃的不是那层涂装，而是倾注在里面的时间。同理，战斗通行证进度、收藏完成度，都是在把「玩过」变成「不舍得离开」。",
    "纯静态皮肤带来的粘性是有限的——买完就结束。真正能提升留存的，是让皮肤随玩家的行为而改变。这个项目原本完全没有这类机制，皮肤买完即是终点，这是它在留存设计上最大的空缺。",
    "建议下一步：为皮肤增加「击杀数进化」（如虚空领主随累计击杀增加环绕碎片数量），把皮肤从装饰品升级为战绩容器。")

# ══════════════════════════════════════════════
# 17. 观点 4
# ══════════════════════════════════════════════
viewpoint_slide(
    "05 / 我的观点 · 观点四", "在低资源项目里，约束应该成为设计语言，而不是借口",
    "「没有美术资源」反而逼出了更清晰的设计纪律",
    "这个项目没有美术，没有图片资源，皮肤只能靠代码画。常规思路会觉得「那只能做得很简陋」。但恰恰相反——正因为只能用几何图形，我被迫把皮肤拆解成「底盘/内核/描边/结构/光效」这种可复用的结构层。",
    "这种结构化的思路，比「凭感觉画一套图」更接近可规模化的设计系统。它让第 7 套皮肤的开发成本远低于第 1 套，也让「稀有度 = 层数」这种商业规则可以被机械地执行，而不依赖某个人当天的审美状态。",
    "结论：把约束转化为规范（分层结构 + 稀有度规则），是低资源项目做设计系统的正确姿势。")

# ══════════════════════════════════════════════
# 18. 边界
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "06 / 边界与反思", "哪些做了，哪些还没做",
       "说清楚「没做成什么」，比只列成绩更有价值")

rows = [("六套皮肤分层渲染", "已上线", True),
        ("稀有度四档体系", "已上线", True),
        ("商店实时动效预览", "已上线", True),
        ("可读性底衬（剪影保障）", "已上线", True),
        ("移动端性能降级", "已上线", True),
        ("皮肤进化 / 战绩绑定", "未落地 · 最能提升留存的方向，尚未接入击杀数驱动的进化", False),
        ("手绘级插画质感", "不具备 · 程序化几何渲染的能力边界", False),
        ("真实支付接入", "规划中 · 皮肤购买仍为模拟流程", False),
        ("真实用户数据", "已有 · 79 名独立玩家 / 133 局 / 1,996 条事件（部分均值受测试数据影响）", True)]
y = Inches(1.95)
for name, status, live in rows:
    box(s, Inches(0.92), y, Inches(11.5), Inches(0.54), fill=CARD, line=LINE, radius=0.09)
    text(s, Inches(1.25), y, Inches(3.6), Inches(0.54), [[(name, 12, TEXT, True)]], anchor=MSO_ANCHOR.MIDDLE)
    dot = GREEN if live else DIM
    text(s, Inches(5.1), y, Inches(7.1), Inches(0.54), [[(status, 11, dot, not live)]], anchor=MSO_ANCHOR.MIDDLE)
    y += Inches(0.63)

# ══════════════════════════════════════════════
# 19. 反思
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
header(s, "06 / 边界与反思", "做完之后的反思")
reflects = [
    ("1. 我一开始差点把它做成「美术练习」",
     "最初接到「美化皮肤」的需求，我的第一反应是「怎么画得更好看」。但想清楚之后发现，这个系统的病根不是审美，而是皮肤在商业结构里没有位置——没有稀有度、没有价值差、没有拥有感。如果我只把六个圆画得更漂亮，问题一个都没解决。产品经理的价值在于识别「这是结构问题还是表现问题」，而这次是前者。"),
    ("2. 最难的设计决策是「暗影刺客怎么被看见」",
     "这套皮肤逼我做了一次真正的取舍：名字要求它「暗」，但游戏背景本身就是暗的，做得越暗越不可玩。最后我的解法是放弃用填充色表达存在感，改用发光描边与光点来「在黑暗里制造存在」。这让我理解了一个更普遍的道理——当需求和约束正面冲突时，不要在同一个维度上死磕（把暗色调亮一点），而要换一个维度解决（用光而不是色）。"),
    ("3. 我验证自己工作的方式，比结果更值得说",
     "中途我一度以为「虚空领主」没渲染出来——因为截图里角色所在位置是一团红色。后来我直接读取 canvas 的像素数据，才发现是敌人贴身围攻覆盖了角色，皮肤其实正常渲染。这让我意识到：凭截图和直觉判断会得出错误结论，产品判断要建立在可测量的证据上。这个习惯最后反过来让我发现了真正的可读性问题，并做了针对性修复。"),
]
y = Inches(1.7)
for t, d in reflects:
    box(s, Inches(0.92), y, Inches(11.5), Inches(1.62), fill=CARD, line=AMBER, radius=0.05)
    text(s, Inches(1.25), y + Inches(0.16), Inches(10.9), Inches(0.35), [[(t, 13.5, AMBER, True)]])
    text(s, Inches(1.25), y + Inches(0.58), Inches(10.9), Inches(0.95), [[(d, 10.8, MUTED, False)]], spacing=1.28)
    y += Inches(1.78)

# ══════════════════════════════════════════════
# 20. 结尾
# ══════════════════════════════════════════════
s = prs.slides.add_slide(BLANK); bg(s)
box(s, 0, 0, SW, Inches(0.05), fill=ACCENT)
text(s, Inches(1.0), Inches(2.35), Inches(11.3), Inches(1.2), [[("谢谢观看", 42, TEXT, True)]], align=PP_ALIGN.CENTER)
text(s, Inches(1.0), Inches(3.45), Inches(11.3), Inches(0.5),
     [[("生存竞技场 · 武器皮肤分析与创意策划案", 16, ACCENT2, False)]], align=PP_ALIGN.CENTER)
text(s, Inches(1.0), Inches(4.2), Inches(11.3), Inches(1.2),
     [[("交付物：武器皮肤分析报告 + 针对本游戏的武器皮肤创意策划案", 13, MUTED, False)],
      [("实践营课题一 ｜ 游戏产品经理方向", 13, MUTED, False)],
      [("皮肤体系已实机落地：6 套皮肤 / 4 档稀有度 / 全程序化 Canvas 渲染", 13, GREEN, False)]],
     align=PP_ALIGN.CENTER, spacing=1.5)

out = BASE / "生存竞技场-武器皮肤分析与创意策划案.pptx"
prs.save(str(out))
tmp = BASE / "_tmp.pptx"
if tmp.exists(): tmp.unlink()
print(f"OK saved: {out}")
print(f"slides: {len(prs.slides._sldIdLst)}")




