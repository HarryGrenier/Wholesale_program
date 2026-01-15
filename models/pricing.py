# models/pricing.py

def price_with_fee(unit_price, case_fee):
    return round(float(unit_price) + float(case_fee), 2)

def markup_price(cost, markup_rate):
    return round(float(cost) * (1 + float(markup_rate)), 2)

def margin_pct_on_sale(cost, sale):
    sale = float(sale)
    if sale <= 0:
        return 0.0
    return (sale - float(cost)) / sale