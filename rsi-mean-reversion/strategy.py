def initialize(context):
    g.security = '600570.SS'
    g.rsi_period = 14
    g.oversold = 30
    g.overbought = 70
    set_universe(g.security)
    set_benchmark('000300.SS')

def _calc_rsi(closes, period):
    """手写 RSI：Wilder 平滑法，不依赖 talib"""
    if len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0.0 for d in deltas]
    losses = [-d if d < 0 else 0.0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def handle_data(context, data):
    hist = get_history(g.rsi_period + 10, '1d', 'close', g.security)
    closes = hist['close'].values[::-1]

    rsi = _calc_rsi(closes, g.rsi_period)
    if rsi is None:
        return

    pos = get_position(g.security)
    cash = context.portfolio.cash

    # 超卖买入
    if rsi < g.oversold and pos.amount == 0:
        order_value(g.security, cash * 0.8)  # 留 20% 现金缓冲
        log.info('RSI oversold %.1f: buy %s' % (rsi, g.security))

    # 超买卖出
    elif rsi > g.overbought and pos.amount > 0:
        order_target(g.security, 0)
        log.info('RSI overbought %.1f: sell %s' % (rsi, g.security))
