def initialize(context):
    g.pool = ['600570.SS', '000001.SZ', '600036.SS', '000858.SZ', '601318.SS']
    g.momentum_days = 20
    g.hold_n = 1
    set_universe(g.pool)
    set_benchmark('000300.SS')

def _month_start(context):
    """判断是否为每月第一个交易日（用 previous_date 的月份变化）"""
    today = context.blotter.current_dt
    prev = context.previous_date
    return today.month != prev.month or today.year != prev.year

def handle_data(context, data):
    if not _month_start(context):
        return

    scores = {}
    for sec in g.pool:
        hist = get_history(g.momentum_days + 5, '1d', 'close', sec)
        if hist is None or len(hist) < 2:
            continue
        closes = hist['close'].values[::-1]
        if len(closes) < 2:
            continue
        # 过去 N 日收益率
        score = closes[-1] / closes[0] - 1.0
        scores[sec] = score

    if not scores:
        return

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    targets = set([sec for sec, _ in ranked[:g.hold_n]])

    # 卖出不在目标中的持仓
    for sec in g.pool:
        pos = get_position(sec)
        if sec not in targets and pos.amount > 0:
            order_target(sec, 0)
            log.info('Rotate out: %s' % sec)

    # 等权买入目标标的
    if targets:
        cash = context.portfolio.cash
        per = cash / len(targets)
        for sec in targets:
            order_value(sec, per)
            log.info('Rotate in: %s, score=%.4f' % (sec, scores[sec]))
