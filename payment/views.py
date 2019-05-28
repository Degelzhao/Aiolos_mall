from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from orders.models import Order
from .alipay_aiolos import call_alipay

# Create your views here.
def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    print(order)

    if order:
        subject = f'我的订单{order_id}'
        # total_amount = order.get_total_cost()  # 数据格式错误
        total_amount = float(order.get_total_cost())  # 处理错误码：INVALID_PARAMETER
        print(subject, f'总金额：{total_amount}')
        pay_url = call_alipay(order_id, total_amount, subject)
        # 重定向到支付宝支付页面
        return HttpResponseRedirect(pay_url)

def payment_done(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    print(order)

    # 优惠券失效
    if order.coupon:
        order.coupon.active = False
        order.coupon.save()

    # 取支付宝返回的参数
    params = request.GET.dict()
    print(params)

    trade_no = params.pop('trade_no', None)  # 取出trade_no
    # 确认支付
    order.paid = True
    # 保存支付宝订单号
    order.pay_id = trade_no
    order.save()

    return render(request, 'payment/done.html', {'trade_no': trade_no})