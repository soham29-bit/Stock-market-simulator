import random, warnings
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, matplotlib.patches as patches
from matplotlib.widgets import Button, TextBox
from matplotlib.animation import FuncAnimation
warnings.filterwarnings('ignore')

# ── DATA ──────────────────────────────────────────────────────────────
SYM = ["AAPL","TSLA","GOOG","AMZN"]
px  = {"AAPL":150.,"TSLA":200.,"GOOG":180.,"AMZN":170.}
pp  = px.copy()
bal = 10000.
qty = {s:0   for s in SYM}
avg = {s:0.  for s in SYM}
his = {s:[px[s]] for s in SYM}
scr = "home"
_ax, _wr = [], []

# ── LOGIC ─────────────────────────────────────────────────────────────
def tick():
    global pp
    pp = px.copy()
    for s in SYM:
        px[s] = max(1., px[s] + random.uniform(-5, 5))
        his[s].append(px[s])

def upl():
    return sum((px[s]-avg[s])*qty[s] for s in SYM if qty[s]>0)

def trade(sym_t, qt_t, mode):
    global bal
    s = sym_t.strip().upper()
    if s not in px: return False, f"⚠  Unknown symbol '{s or '?'}'"
    try:
        q = int(qt_t.strip()); assert q > 0
    except: return False, "⚠  Enter a valid positive quantity"
    if mode == "buy":
        cost = px[s]*q
        if cost > bal: return False, f"⚠  Need ₹{cost:,.0f} — only ₹{bal:,.0f}"
        old = qty[s]; bal -= cost
        avg[s] = (avg[s]*old + px[s]*q)/(old+q)
        qty[s] += q
        return True, f"✔  Bought {q} × {s}  @  ₹{px[s]:.2f}"
    else:
        if qty[s] < q: return False, f"⚠  Only {qty[s]} shares held"
        bal += px[s]*q; qty[s] -= q
        return True, f"✔  Sold {q} × {s}  @  ₹{px[s]:.2f}"

# ── THEME ─────────────────────────────────────────────────────────────
BG,PANEL,CARD2 = '#07070f','#0b0b18','#141430'
BORDER,BLUE    = '#1e1e44','#4ab8f5'
GREEN,RED      = '#10e8a0','#ff3358'
PURPLE,GOLD    = '#c050f8','#ffcc44'
CYAN,TEXT      = '#00e5ff','#c8ccee'
MUTED,WHITE    = '#42427a','#eeeeff'
SC = {'AAPL':BLUE,'TSLA':RED,'GOOG':GREEN,'AMZN':GOLD}

plt.rcParams.update({
    'figure.facecolor':BG,'text.color':TEXT,'font.family':'monospace',
    'axes.facecolor':BG,'axes.edgecolor':BORDER,
    'grid.color':BORDER,'grid.alpha':0.45,
    'xtick.color':MUTED,'ytick.color':MUTED,
    'xtick.labelsize':7,'ytick.labelsize':7,
})

# ── FIGURE ────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16,9), facecolor=BG)
try: fig.canvas.manager.set_window_title("◈  SYS STOCKS  —  Trading Terminal")
except: pass

# Top bar
ax_top = fig.add_axes([0,0.93,1,0.07]); ax_top.set_facecolor('#030309'); ax_top.axis('off')
for xi in np.linspace(0,1,500):
    ax_top.axvline(x=xi, ymin=0.0, ymax=0.12, color=plt.cm.plasma(xi*0.75+0.1), lw=2.2, alpha=0.95)
ax_top.text(0.017,0.57,'◈  SYS STOCKS',transform=ax_top.transAxes,fontsize=20,color=WHITE,va='center',fontweight='bold')
ax_top.text(0.215,0.57,'│  LIVE TRADING TERMINAL',transform=ax_top.transAxes,fontsize=10,color=MUTED,va='center')
bal_lbl = ax_top.text(0.978,0.57,f'BALANCE   ₹{bal:,.0f}',transform=ax_top.transAxes,
                       fontsize=13,fontweight='bold',color=GOLD,va='center',ha='right')

# Sidebar
ax_side = fig.add_axes([0,0,0.135,0.93]); ax_side.set_facecolor(PANEL); ax_side.axis('off')
for yi in np.linspace(0,1,200):
    ax_side.plot([1.0,1.0],[yi,yi+0.006],color=plt.cm.plasma(yi*0.6+0.1),
                 lw=2,alpha=0.7,transform=ax_side.transAxes)
ax_side.text(0.5,0.975,'─  MENU  ─',transform=ax_side.transAxes,fontsize=8,color=MUTED,ha='center',va='top')

# Main canvas
L,B,W,H = 0.145,0.01,0.845,0.91
ax = fig.add_axes([L,B,W,H]); ax.set_facecolor(BG); ax.axis('off')
ax.set_xlim(0,10); ax.set_ylim(0,6.2)

# Nav buttons
NAV = [('home','⌂   HOME',BLUE,0.840),('buy','▲   BUY',GREEN,0.745),
       ('sell','▼   SELL',RED,0.650),('portfolio','◈   PORTFOLIO',CYAN,0.555),
       ('charts','◉   CHARTS',PURPLE,0.460),('exit','✕   EXIT',MUTED,0.035)]
nav = {}
for name,lbl,col,yp in NAV:
    ab = fig.add_axes([0.007,yp,0.121,0.072]); ab.set_facecolor(CARD2)
    for sp in ab.spines.values(): sp.set_edgecolor(col); sp.set_linewidth(1.8)
    b = Button(ab,lbl,color=CARD2,hovercolor='#1c1c40')
    b.label.set_color(col); b.label.set_fontsize(10.5)
    b.label.set_fontweight('bold'); b.label.set_fontfamily('monospace')
    nav[name] = b

# ── HELPERS ───────────────────────────────────────────────────────────
def clr():
    global _ax,_wr
    for a in _ax:
        try: a.remove()
        except: pass
    _ax.clear(); _wr.clear()

def upd_bal(): bal_lbl.set_text(f'BALANCE   ₹{bal:,.0f}')

def card(x,y,w,h,ec=BORDER,fc=CARD2,lw=1.2):
    ax.add_patch(patches.FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.04",
        lw=lw,edgecolor=ec,facecolor=fc,alpha=0.97,zorder=2))

def hln(y,x0=0.08,x1=9.92):
    ax.plot([x0,x1],[y,y],color=BORDER,lw=0.8,alpha=0.55,zorder=1)

def hdr(title,sub,col):
    ax.text(5,5.9,title,ha='center',fontsize=22,fontweight='bold',color=col,zorder=3)
    ax.text(5,5.52,sub,ha='center',fontsize=9,color=MUTED,zorder=3); hln(5.35)

def spark(sym,cx,cy,cw,sy0,sy1,col):
    d = np.array(his[sym][-50:],float)
    if len(d)<2: return
    xs = np.linspace(cx+0.18,cx+cw-0.18,len(d))
    mn,mx = d.min(),d.max()
    ys = (d-mn)/(mx-mn)*(sy1-sy0)+sy0 if mx>mn else np.full_like(d,sy0+0.1)
    ax.fill_between(xs,sy0,ys,color=col,alpha=0.13,zorder=3)
    ax.plot(xs,ys,color=col,lw=1.8,alpha=0.85,zorder=3)
    ax.scatter([xs[-1]],[ys[-1]],color=col,s=30,zorder=5)

def mk_tb(ax_tb, col):
    # Lighter background so the text cursor line is visible
    ax_tb.set_facecolor('#1e1e3e')
    for sp in ax_tb.spines.values(): sp.set_edgecolor(col); sp.set_linewidth(2)
    tb = TextBox(ax_tb,'',initial='',color='#1e1e3e',hovercolor='#26264e')
    tb.text_disp.set_color(WHITE); tb.text_disp.set_fontsize(13)
    tb.text_disp.set_fontfamily('monospace')
    try:                                   # make the blinking cursor white
        tb.cursor.set_color(WHITE)
        tb.cursor.set_linewidth(2)
    except: pass
    return tb

# ── SCREENS ───────────────────────────────────────────────────────────
def show_home():
    global scr; scr="home"; clr()
    ax.clear(); ax.set_facecolor(BG); ax.axis('off')
    ax.set_xlim(0,10); ax.set_ylim(0,6.2)
    hdr('MARKET OVERVIEW','LIVE PRICES  ·  AUTO REFRESH: 3s  ·  4 SYMBOLS',BLUE)

    CW,CH = 4.65,2.25
    GRID = [("AAPL",0.20,2.88),("TSLA",5.15,2.88),
            ("GOOG",0.20,0.40),("AMZN",5.15,0.40)]

    for sym,cx,cy in GRID:
        p,pv = px[sym],pp[sym]
        ch   = p-pv; pct=(ch/pv*100) if pv else 0.
        col  = GREEN if ch>=0 else RED
        arr  = '▲' if ch>0 else ('▼' if ch<0 else '─')
        sgn  = '+' if ch>=0 else ''

        # glow halo
        ax.add_patch(patches.FancyBboxPatch((cx-0.10,cy-0.10),CW+0.20,CH+0.20,
            boxstyle="round,pad=0.06",lw=5,edgecolor=col,facecolor='none',alpha=0.08,zorder=1))
        card(cx,cy,CW,CH,ec=col,fc=CARD2,lw=1.8)
        # top colour strip
        ax.add_patch(patches.FancyBboxPatch((cx,cy+CH-0.50),CW,0.50,
            boxstyle="round,pad=0.0",facecolor=col,alpha=0.17,lw=0,zorder=3))
        # pulse dot
        ax.add_patch(plt.Circle((cx+CW-0.28,cy+CH-0.26),0.11,color=col,zorder=5,alpha=0.9))
        ax.add_patch(plt.Circle((cx+CW-0.28,cy+CH-0.26),0.20,color=col,zorder=4,alpha=0.18))

        ax.text(cx+0.22,cy+CH-0.265,sym,fontsize=15,fontweight='bold',color=WHITE,va='center',zorder=4)
        ax.text(cx+CW/2,cy+1.22,f'₹ {p:,.2f}',ha='center',fontsize=22,fontweight='bold',color=col,zorder=4)
        ax.text(cx+CW/2,cy+0.68,f'{arr}  {sgn}{ch:.2f}    ({sgn}{pct:.1f}%)',
                ha='center',fontsize=10,color=col,zorder=4)
        spark(sym,cx,cy,CW,cy+0.12,cy+0.52,col)
    fig.canvas.draw_idle()

def show_trade(mode):
    global scr; scr=mode; clr()
    ax.clear(); ax.set_facecolor(BG); ax.axis('off')
    ax.set_xlim(0,10); ax.set_ylim(0,6.2)
    col = GREEN if mode=="buy" else RED
    hdr('BUY STOCKS' if mode=="buy" else 'SELL STOCKS',
        'LONG POSITION  ·  MARKET ORDER' if mode=="buy" else 'CLOSE POSITION  ·  MARKET ORDER', col)

    # Left info card
    card(0.28,2.45,3.85,2.75,ec=BORDER,lw=1)
    ax.text(2.2,5.02,'LIVE PRICES' if mode=="buy" else 'YOUR HOLDINGS',
            ha='center',fontsize=10,color=MUTED)
    ax.plot([0.38,4.03],[4.82,4.82],color=BORDER,lw=0.8,alpha=0.55)
    for i,sym in enumerate(SYM):
        sy=4.40-i*0.54; c=SC[sym]; has=qty[sym]>0
        ax.text(0.62,sy,sym,fontsize=13,fontweight='bold',
                color=c if (mode=="buy" or has) else MUTED)
        val = f'₹ {px[sym]:,.2f}' if mode=="buy" else f'{qty[sym]} shares'
        ax.text(3.95,sy,val,fontsize=12,color=TEXT if (mode=="buy" or has) else MUTED,ha='right')
    ax.plot([0.38,4.03],[2.72,2.72],color=BORDER,lw=0.8,alpha=0.55)
    if mode=="buy":
        ax.text(0.62,2.55,'BALANCE',fontsize=10,color=MUTED)
        ax.text(3.95,2.55,f'₹{bal:,.2f}',fontsize=12,fontweight='bold',color=GOLD,ha='right')
    else:
        pl=upl(); plc=GREEN if pl>=0 else RED
        ax.text(0.62,2.55,'UNREALIZED P/L',fontsize=10,color=MUTED)
        ax.text(3.95,2.55,f'{"+" if pl>=0 else ""}₹{pl:.0f}',fontsize=12,fontweight='bold',color=plc,ha='right')

    # Right form — labels above each box
    ax.text(5.68,4.72,'▶   STOCK SYMBOL',fontsize=11,color=col,fontweight='bold')
    ax.text(5.68,3.78,'▶   QUANTITY',fontsize=11,color=col,fontweight='bold')

    ax_sym = fig.add_axes([0.495,0.560,0.35,0.068])
    ax_qty = fig.add_axes([0.495,0.425,0.35,0.068])
    ax_btn = fig.add_axes([0.515,0.265,0.31,0.090])
    ax_btn.set_facecolor('#001800' if mode=="buy" else '#1a0000')
    for sp in ax_btn.spines.values(): sp.set_edgecolor(col); sp.set_linewidth(2.6)

    tb_s = mk_tb(ax_sym, col)
    tb_q = mk_tb(ax_qty, col)
    btn  = Button(ax_btn,'▲  EXECUTE BUY' if mode=="buy" else '▼  EXECUTE SELL',
                  color='#001800' if mode=="buy" else '#1a0000',
                  hovercolor='#003000' if mode=="buy" else '#2e0000')
    btn.label.set_color(col); btn.label.set_fontsize(13)
    btn.label.set_fontweight('bold'); btn.label.set_fontfamily('monospace')

    msg = ax.text(7.2,1.5,'',ha='center',fontsize=11,fontfamily='monospace')

    def on_click(e):
        ok,txt = trade(tb_s.text, tb_q.text, mode)
        msg.set_text(txt); msg.set_color(GREEN if ok else RED)
        upd_bal(); fig.canvas.draw_idle()

    btn.on_clicked(on_click)
    _ax.extend([ax_sym,ax_qty,ax_btn]); _wr.extend([tb_s,tb_q,btn])
    fig.canvas.draw_idle()

def show_portfolio():
    global scr; scr="portfolio"; clr()
    ax.clear(); ax.set_facecolor(BG); ax.axis('off')
    ax.set_xlim(0,10); ax.set_ylim(0,6.2)
    hdr('PORTFOLIO','HOLDINGS & PERFORMANCE',CYAN)

    pl=upl(); plc=GREEN if pl>=0 else RED; pls='+' if pl>=0 else ''
    card(0.18,4.55,4.60,0.72,ec=GOLD,lw=2)
    ax.text(0.48,5.08,'◈  CASH BALANCE',fontsize=9,color=MUTED)
    ax.text(4.58,5.08,f'₹{bal:,.2f}',fontsize=15,fontweight='bold',color=GOLD,ha='right')
    card(5.22,4.55,4.60,0.72,ec=plc,lw=2)
    ax.text(5.52,5.08,'◈  UNREALIZED P/L',fontsize=9,color=MUTED)
    ax.text(9.62,5.08,f'{pls}₹{pl:,.2f}',fontsize=15,fontweight='bold',color=plc,ha='right')

    df = pd.DataFrame({'sym':SYM,'qty':[qty[s] for s in SYM],
                       'avg':[avg[s] for s in SYM],'cur':[px[s] for s in SYM]})
    df['val']=df['cur']*df['qty']; df['pl']=(df['cur']-df['avg'])*df['qty']

    hln(4.35); hln(3.97)
    XC=[0.40,1.90,3.30,5.00,6.60,8.30]
    for x,c in zip(XC,['SYMBOL','QTY','AVG COST','MKT PRICE','VALUE','P / L']):
        ax.text(x,4.15,c,fontsize=9,color=MUTED,fontweight='bold')

    ry=3.60
    for _,r in df.iterrows():
        s,q,a,cu,v,rpl = r['sym'],int(r['qty']),r['avg'],r['cur'],r['val'],r['pl']
        c=SC[s]; plcr=GREEN if rpl>=0 else RED; plsr='+' if rpl>=0 else ''
        if q>0:
            ax.add_patch(patches.FancyBboxPatch((0.18,ry-0.24),9.65,0.52,
                boxstyle="round,pad=0.04",lw=1.2,edgecolor=c,facecolor='#121232',alpha=0.97,zorder=2))
        ax.text(XC[0],ry,s,fontsize=11,fontweight='bold' if q>0 else 'normal',color=c if q>0 else MUTED)
        ax.text(XC[1],ry,str(q),fontsize=11,color=TEXT if q>0 else MUTED)
        ax.text(XC[2],ry,f'₹{a:.0f}' if q>0 else '─',fontsize=11,color=TEXT)
        ax.text(XC[3],ry,f'₹{cu:.2f}',fontsize=11,color=TEXT)
        ax.text(XC[4],ry,f'₹{v:.0f}' if q>0 else '─',fontsize=11,color=TEXT)
        ax.text(XC[5],ry,f'{plsr}₹{rpl:.0f}' if q>0 else '─',fontsize=11,
                color=plcr if q>0 else MUTED,fontweight='bold' if q>0 else 'normal')
        ry -= 0.52

    if all(qty[s]==0 for s in SYM):
        ax.text(5,2.3,'─  No active positions  ─\nBuy stocks to see them here.',
                ha='center',fontsize=13,color=MUTED,va='center',linespacing=2.2)
    fig.canvas.draw_idle()

def show_charts():
    global scr; scr="chart"; clr()
    ax.clear(); ax.set_facecolor(BG); ax.axis('off')
    ax.set_xlim(0,10); ax.set_ylim(0,6.2)
    ax.text(5,5.9,'PRICE HISTORY',ha='center',fontsize=22,fontweight='bold',color=PURPLE)
    ax.text(5,5.52,'ALL SYMBOLS  ·  TICK CHART  ·  LIVE',ha='center',fontsize=9,color=MUTED)

    POS=[(0.148,0.478,0.40,0.310),(0.568,0.478,0.40,0.310),
         (0.148,0.068,0.40,0.310),(0.568,0.068,0.40,0.310)]
    for sym,pos in zip(SYM,POS):
        ac=fig.add_axes(pos); ac.set_facecolor(CARD2); c=SC[sym]
        d=np.array(his[sym],float); xs=np.arange(len(d))
        if len(d)>1:
            ac.fill_between(xs,d.min()-1,d,color=c,alpha=0.13)
            ac.plot(xs,d,color=c,lw=2,alpha=0.9)
            ac.scatter([xs[-1]],[d[-1]],color=c,s=55,zorder=5)
        else:
            ac.text(0.5,0.5,'Awaiting data...',ha='center',va='center',
                    transform=ac.transAxes,color=MUTED,fontsize=9)
        ac.set_title(f'  {sym}   ₹{px[sym]:.2f}',color=c,fontsize=11,fontweight='bold',loc='left',pad=5)
        ac.tick_params(colors=MUTED,labelsize=7)
        ac.spines['bottom'].set_color(BORDER); ac.spines['left'].set_color(BORDER)
        ac.spines['top'].set_visible(False);   ac.spines['right'].set_visible(False)
        ac.grid(True,color=BORDER,alpha=0.5,lw=0.6)
        ac.set_xlabel('ticks',color=MUTED,fontsize=7); ac.set_ylabel('₹ price',color=MUTED,fontsize=7)
        _ax.append(ac)
    fig.canvas.draw_idle()

# ── ANIMATION ─────────────────────────────────────────────────────────
def on_tick(f):
    tick(); upd_bal()
    if   scr=="home":      show_home()
    elif scr=="portfolio": show_portfolio()
    elif scr=="chart":     show_charts()

ani = FuncAnimation(fig, on_tick, interval=3000, cache_frame_data=False)

# ── WIRE NAV ──────────────────────────────────────────────────────────
nav['home'].on_clicked(      lambda e: show_home())
nav['buy'].on_clicked(       lambda e: show_trade("buy"))
nav['sell'].on_clicked(      lambda e: show_trade("sell"))
nav['portfolio'].on_clicked( lambda e: show_portfolio())
nav['charts'].on_clicked(    lambda e: show_charts())
nav['exit'].on_clicked(      lambda e: plt.close('all'))

show_home()
plt.show()
