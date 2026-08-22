from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from decimal import Decimal
from accounts.decorators import allowed_roles
from billing.models import Bill, BillItem
from products.models import Product
from .models import SaleReturn, SaleReturnItem
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.db.models import Q
from shopsettings.models import ShopSettings

@allowed_roles(["Admin", "Manager", "Accountant", ])
def sale_return_list(request):

    search = request.GET.get("search", "").strip()

    bills = Bill.objects.order_by("-id")

    returns = SaleReturn.objects.select_related(
        "bill",
        "bill__customer"
    ).order_by("-id")

    if search:

        bills = bills.filter(

            Q(invoice_no__icontains=search) |
            Q(customer__name__icontains=search)

        )

        returns = returns.filter(

            Q(bill__invoice_no__icontains=search) |
            Q(bill__customer__name__icontains=search)

        )

    paginator = Paginator(returns, 10)

    page = request.GET.get("page")

    returns = paginator.get_page(page)

    total_return = sum(
        r.total_return
        for r in SaleReturn.objects.all()
    )

    context = {

        "bills": bills,

        "returns": returns,

        "search": search,

        "total_returns": SaleReturn.objects.count(),

        "total_return_amount": total_return

    }

    return render(
        request,
        "salesreturn/list.html",
        context
    )


@allowed_roles(["Admin", "Manager", "Accountant", ])
def sale_return(request, bill_id):

    bill = get_object_or_404(
        Bill,
        id=bill_id
    )

    items = BillItem.objects.filter(
        bill=bill
    )

    if request.method == "POST":

        sale_return = SaleReturn.objects.create(

            bill=bill,

            total_return=0

        )

        total_return = Decimal("0.00")

        for item in items:

            qty = request.POST.get(
                f"qty_{item.id}"
            )

            if qty:

                qty = int(qty)

                if qty <= 0:
                    continue

                if qty > item.quantity:
                    qty = item.quantity

                amount = item.price * qty

                SaleReturnItem.objects.create(

                    sale_return=sale_return,

                    bill_item=item,

                    quantity=qty,

                    returned_qty=qty,

                    amount=amount

                )

                product = item.product

                product.quantity += qty

                product.save()

                item.quantity -= qty

                item.save()

                total_return += amount

        sale_return.total_return = total_return

        sale_return.save()

        return redirect(
            "sale_return_list"
        )

    return render(

        request,

        "salesreturn/return.html",

        {

            "bill": bill,

            "items": items

        }

    )

from django.shortcuts import get_object_or_404, render

from shopsettings.models import ShopSettings
from .models import SaleReturn


def print_sale_return(request, id):

    sale_return = get_object_or_404(

        SaleReturn,

        id=id

    )

    shop = ShopSettings.objects.first()

    context = {

        "shop": shop,

        "return_data": sale_return,

    }

    return render(

        request,

        "salesreturn/sale_return_pdf.html",

        context

    )
@allowed_roles(["Admin", "Manager", "Accountant"])
def sale_return_pdf(request, return_id):

    sale_return = get_object_or_404(
        SaleReturn,
        id=return_id
    )

    shop = ShopSettings.objects.first()

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="{sale_return.return_no}.pdf"'
    )

    p = canvas.Canvas(response)

    width = 595
    y = 810

    # ===============================
    # SHOP HEADER
    # ===============================

    if shop:

        if shop.logo:

            try:

                p.drawImage(

                    shop.logo.path,

                    40,

                    y - 55,

                    width=55,

                    height=55,

                    preserveAspectRatio=True

                )

            except:

                pass

        p.setFont(
            "Helvetica-Bold",
            18
        )

        p.drawCentredString(
            width / 2,
            y,
            shop.shop_name
        )

        y -= 18

        p.setFont(
            "Helvetica",
            10
        )

        p.drawCentredString(
            width / 2,
            y,
            shop.address
        )

        y -= 14

        p.drawCentredString(
            width / 2,
            y,
            f"Mobile : {shop.mobile}"
        )

        y -= 14

        p.drawCentredString(
            width / 2,
            y,
            f"GST : {shop.gst_number}"
        )

    y -= 25

    p.line(
        30,
        y,
        565,
        y
    )

    y -= 28

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawCentredString(
        width / 2,
        y,
        "SALE RETURN"
    )

    y -= 30

    # ===============================
    # SALE RETURN DETAILS
    # ===============================

    p.setFont(
        "Helvetica",
        11
    )

    p.drawString(
        40,
        y,
        f"Return No : {sale_return.return_no}"
    )

    p.drawRightString(
        550,
        y,
        f"Date : {sale_return.created_at.strftime('%d-%m-%Y')}"
    )

    y -= 20

    p.drawString(
        40,
        y,
        f"Invoice No : {sale_return.bill.invoice_no}"
    )

    p.drawRightString(
        550,
        y,
        f"Status : {sale_return.status}"
    )

    y -= 20

    customer = (
        sale_return.bill.customer.name
        if sale_return.bill.customer
        else "Walk In Customer"
    )

    p.drawString(
        40,
        y,
        f"Customer : {customer}"
    )

    y -= 30
        # ===============================
    # TABLE HEADER
    # ===============================

    p.setFont(
        "Helvetica-Bold",
        11
    )

    p.rect(40, y - 18, 35, 18)
    p.rect(75, y - 18, 250, 18)
    p.rect(325, y - 18, 70, 18)
    p.rect(395, y - 18, 80, 18)
    p.rect(475, y - 18, 80, 18)

    p.drawCentredString(
        57,
        y - 13,
        "Sr"
    )

    p.drawCentredString(
        200,
        y - 13,
        "Product"
    )

    p.drawCentredString(
        360,
        y - 13,
        "Qty"
    )

    p.drawCentredString(
        435,
        y - 13,
        "Rate"
    )

    p.drawCentredString(
        515,
        y - 13,
        "Amount"
    )

    y -= 18

    # ===============================
    # TABLE DATA
    # ===============================

    p.setFont(
        "Helvetica",
        10
    )

    sr = 1

    for item in sale_return.items.all():

        y -= 18

        if y < 120:

            p.showPage()

            y = 800

            p.setFont(
                "Helvetica-Bold",
                11
            )

            p.rect(40, y - 18, 35, 18)
            p.rect(75, y - 18, 250, 18)
            p.rect(325, y - 18, 70, 18)
            p.rect(395, y - 18, 80, 18)
            p.rect(475, y - 18, 80, 18)

            p.drawCentredString(57, y - 13, "Sr")
            p.drawCentredString(200, y - 13, "Product")
            p.drawCentredString(360, y - 13, "Qty")
            p.drawCentredString(435, y - 13, "Rate")
            p.drawCentredString(515, y - 13, "Amount")

            y -= 18

            p.setFont(
                "Helvetica",
                10
            )

        p.rect(40, y, 35, 18)
        p.rect(75, y, 250, 18)
        p.rect(325, y, 70, 18)
        p.rect(395, y, 80, 18)
        p.rect(475, y, 80, 18)

        p.drawCentredString(
            57,
            y + 5,
            str(sr)
        )

        p.drawString(
            80,
            y + 5,
            item.bill_item.product.name[:35]
        )

        p.drawCentredString(
            360,
            y + 5,
            str(item.quantity)
        )

        rate = (
            item.amount / item.quantity
            if item.quantity else 0
        )

        p.drawRightString(
            468,
            y + 5,
            f"{rate:.2f}"
        )

        p.drawRightString(
            548,
            y + 5,
            f"{item.amount:.2f}"
        )

        sr += 1

            # ===============================
    # TOTAL SECTION
    # ===============================

    y -= 35

    p.setFont(
        "Helvetica-Bold",
        12
    )

    p.rect(
        365,
        y - 22,
        200,
        22
    )

    p.drawString(
        365,
        y - 13,
        "Total Return Amount"
    )

    p.drawRightString(
        545,
        y - 13,
        f"Rs. {sale_return.total_return:.2f}"
    )

    y -= 60

    # ===============================
    # TERMS & CONDITIONS
    # ===============================

    p.setFont(
        "Helvetica-Bold",
        11
    )

    p.drawString(
        40,
        y,
        "Terms & Conditions"
    )

    y -= 18

    p.setFont(
        "Helvetica",
        10
    )

    p.drawString(
        45,
        y,
        "• Returned goods once accepted cannot be exchanged again."
    )

    y -= 15

    p.drawString(
        45,
        y,
        "• Amount refunded/adjusted as per shop policy."
    )

    y -= 15

    p.drawString(
        45,
        y,
        "• This is a computer generated Sale Return."
    )

    # ===============================
    # SIGNATURE
    # ===============================

    y -= 70

    p.line(
        390,
        y,
        550,
        y
    )

    y -= 15

    p.setFont(
        "Helvetica",
        10
    )

    p.drawCentredString(
        470,
        y,
        "Authorized Signature"
    )

    # ===============================
    # FOOTER
    # ===============================

    p.setFont(
        "Helvetica",
        9
    )

    p.drawCentredString(
        width / 2,
        55,
        "THANK YOU • VISIT AGAIN"
    )

    p.drawCentredString(
        width / 2,
        40,
        f"Printed On : {sale_return.created_at.strftime('%d-%m-%Y %H:%M')}"
    )

    p.drawCentredString(
        width / 2,
        25,
        f"Sale Return No : {sale_return.return_no}"
    )

    # ===============================
    # SAVE PDF
    # ===============================

    p.showPage()

    p.save()

    return response 