def initialize(context):
    g.security = '600570.SS'
    g.fast = 5
    g.slow = 20
    set_universe(g.security)
    set_benchmark('000300.SS')

def handle_data(context, data):
    # 取足够覆盖慢线的历史数据；PTrade 返回的 DataFrame 默认按时间倒序
    hist = get_history(g.slow + 5, '1d', 'close', g.security)
    closes = hist['close'].values[::-1]  # 反转为时间正序，rolling 才不会算错[reference:2]

    if len(closes) < g.slow:
        return

    # 用 pandas Series 计算均线（pandas 在 PTrade 内置可用）
    import pandas as pd
    s = pd.Series(closes)
    ma_fast = s.rolling(g.fast).mean().iloc[-1]
    ma_slow = s.rolling(g.slow).mean().iloc[-1]

    pos = get_position(g.security)
    cash = context.portfolio.cash

    # 金叉且空仓 → 全仓买入
    if ma_fast > ma_slow and pos.amount == 0:
        order_value(g.security, cash)
        log.info('SMA golden cross: buy %s' % g.security)

    # 死叉且持仓 → 清仓
    elif ma_fast < ma_slow and pos.amount > 0:
        order_target(g.security, 0)
        log.info('SMA death cross: sell %s' % g.security)
