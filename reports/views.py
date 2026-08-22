from django.shortcuts import render
from billing.models import Bill
import expenses
from products.models import Product
from billing.models import BillItem
from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from expenses.models import Expense
from customers.models import Customer
from purchases.models import Purchase
from decimal import Decimal
from django.template.loader import get_template
from xhtml2pdf import pisa
from shopsettings.models import ShopSettings
from io import BytesIO
from django.utils import timezone
from accounts.decorators import allowed_roles
from datetime import timedelta



@allowed_roles(["Admin", "Manager"])
def sales_report(request):

    bills = Bill.objects.all().order_by(
        '-created_at'
    )

    from_date = request.GET.get(
        'from_date'
    )

    to_date = request.GET.get(
        'to_date'
    )

    if from_date:

        bills = bills.filter(
            created_at__date__gte=from_date
        )

    if to_date:

        bills = bills.filter(
            created_at__date__lte=to_date
        )

    total_sales = sum(
        bill.total_amount
        for bill in bills
    )

    cash_sales = sum(
        bill.total_amount
        for bill in bills
        if bill.payment_method == 'Cash'
    )

    upi_sales = sum(
        bill.total_amount
        for bill in bills
        if bill.payment_method == 'UPI'
    )

    credit_sales = sum(
        bill.total_amount
        for bill in bills
        if bill.payment_method == 'Credit'
    )

    context = {

        'bills': bills,

        'total_sales': total_sales,

        'cash_sales': cash_sales,

        'upi_sales': upi_sales,

        'credit_sales': credit_sales,

        'from_date': from_date,

        'to_date': to_date

    }

    return render(
        request,
        'reports/sales_report.html',
        context
    )
from decimal import Decimal

@allowed_roles(["Admin", "Manager"])
def stock_report(request):

    products = Product.objects.all().order_by("name")

    total_purchase_value = Decimal("0")
    total_selling_value = Decimal("0")
    total_profit = Decimal("0")

    for product in products:

        product.purchase_value = (
            product.purchase_price * product.quantity
        )

        product.selling_value = (
            product.selling_price * product.quantity
        )

        product.expected_profit = (
            product.selling_value
            -
            product.purchase_value
        )

        total_purchase_value += product.purchase_value
        total_selling_value += product.selling_value
        total_profit += product.expected_profit

    context = {

        "products": products,

        "total_purchase_value": total_purchase_value,

        "total_selling_value": total_selling_value,

        "total_profit": total_profit,

    }

    return render(

        request,

        "reports/stock_report.html",

        context

    )


@allowed_roles(["Admin","Manager"])
def top_products_report(request):

    products = (
        BillItem.objects
        .values("product__name")
        .annotate(
            total_qty=Sum("quantity"),
            total_amount=Sum("total")
        )
        .order_by("-total_qty")
    )

    context = {

        "products": products,

    }

    return render(

        request,

        "reports/top_products.html",

        context

    )


@allowed_roles(["Admin","Manager"])
def sales_report_pdf(request):

    bills = Bill.objects.all().order_by("-created_at")

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if from_date:
        bills = bills.filter(created_at__date__gte=from_date)

    if to_date:
        bills = bills.filter(created_at__date__lte=to_date)

    total_sales = sum(
        bill.total_amount
        for bill in bills
    )

    cash_sales = sum(
        bill.total_amount
        for bill in bills
        if bill.payment_method == "Cash"
    )

    upi_sales = sum(
        bill.total_amount
        for bill in bills
        if bill.payment_method == "UPI"
    )

    credit_sales = sum(
        bill.total_amount
        for bill in bills
        if bill.payment_method == "Credit"
    )

    shop = ShopSettings.objects.first()
    current_time = timezone.localtime()

    template = get_template(
        "reports/sales_report_pdf.html"
    )

    html = template.render({

        "shop": shop,
        "current_time": current_time,

        "bills": bills,

        "total_sales": total_sales,

        "cash_sales": cash_sales,

        "upi_sales": upi_sales,

        "credit_sales": credit_sales,

        "from_date": from_date,

        "to_date": to_date,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'inline; filename="Sales_Report.pdf"'

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

@allowed_roles(["Admin","Manager"])
def expense_report(request):

    expenses = Expense.objects.all().order_by('-date')

    total_expense = sum(
        expense.amount
        for expense in expenses
    )

    context = {

        'expenses': expenses,

        'total_expense': total_expense

    }

    return render(
        request,
        'reports/expense_report.html',
        context
    )

@allowed_roles(["Admin","Manager"])
def profit_report(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    bills = Bill.objects.all()
    purchases = Purchase.objects.all()
    expenses = Expense.objects.all()

    if from_date:
        bills = bills.filter(created_at__date__gte=from_date)
        purchases = purchases.filter(created_at__date__gte=from_date)
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        bills = bills.filter(created_at__date__lte=to_date)
        purchases = purchases.filter(created_at__date__lte=to_date)
        expenses = expenses.filter(date__lte=to_date)

    total_sales = sum(
        bill.final_amount
        for bill in bills
    )

    total_purchase = sum(
        purchase.final_amount
        for purchase in purchases
    )

    total_expense = sum(
        expense.amount
        for expense in expenses
    )

    gross_profit = Decimal("0.00")

    items = BillItem.objects.filter(
        bill__in=bills
    )

    for item in items:

        gross_profit += (

            (item.price - item.purchase_price)

            * item.quantity

        )

    net_profit = gross_profit - Decimal(total_expense)

    if total_sales > 0:

        profit_margin = (

            net_profit / total_sales

        ) * 100

    else:

        profit_margin = Decimal("0.00")

    context = {

        "total_sales": total_sales,

        "total_purchase": total_purchase,

        "gross_profit": gross_profit,

        "total_expense": total_expense,

        "profit": net_profit,

        "profit_margin": round(
            profit_margin,
            2
        ),

        "from_date": from_date,

        "to_date": to_date,

    }

    return render(

        request,

        "reports/profit_report.html",

        context

    )


@allowed_roles(["Admin","Manager"])
def payment_recovery(request):

    customers = Customer.objects.filter(
        credit_balance__gt=0
    ).order_by("-credit_balance")

    total_recovery = sum(
        customer.credit_balance
        for customer in customers
    )

    context = {

        "customers": customers,

        "total_recovery": total_recovery

    }

    return render(

        request,

        "reports/payment_recovery.html",

        context

    )

@allowed_roles(["Admin","Manager"])
def purchase_report(request):

    purchases = Purchase.objects.all().order_by("-created_at")

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if from_date:
        purchases = purchases.filter(created_at__date__gte=from_date)

    if to_date:
        purchases = purchases.filter(created_at__date__lte=to_date)

    total_purchase = sum(
        purchase.final_amount
        for purchase in purchases
    )

    context = {

        "purchases": purchases,

        "total_purchase": total_purchase,

        "from_date": from_date,

        "to_date": to_date,

    }

    return render(

        request,

        "reports/purchase_report.html",

        context

    )

@allowed_roles(["Admin","Manager"])
def purchase_report_pdf(request):

    purchases = Purchase.objects.all().order_by("-created_at")

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if from_date:
        purchases = purchases.filter(created_at__date__gte=from_date)

    if to_date:
        purchases = purchases.filter(created_at__date__lte=to_date)

    total_purchase = sum(
        purchase.final_amount
        for purchase in purchases
    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/purchase_report_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "purchases": purchases,

        "total_purchase": total_purchase,

        "from_date": from_date,

        "to_date": to_date,

        "current_time": current_time,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Purchase_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response
    
@allowed_roles(["Admin","Manager"])  
def stock_report_pdf(request):

    products = Product.objects.all().order_by("name")

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    total_stock_value = Decimal("0.00")

    for product in products:
        total_stock_value += (
            product.purchase_price * product.quantity
        )

    template = get_template(
        "reports/stock_report_pdf.html"
    )

    html = template.render({

        "products": products,

        "shop": shop,

        "current_time": current_time,

        "total_stock_value": total_stock_value,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Stock_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

@allowed_roles(["Admin","Manager"])
def expense_report_pdf(request):

    expenses = Expense.objects.all().order_by("-date")

    total_expense = sum(
        expense.amount
        for expense in expenses
    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/expense_report_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "expenses": expenses,

        "total_expense": total_expense,

        "current_time": current_time,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Expense_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

@allowed_roles(["Admin","Manager"])
def profit_report_pdf(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    bills = Bill.objects.all()
    purchases = Purchase.objects.all()
    expenses = Expense.objects.all()

    if from_date:
        bills = bills.filter(created_at__date__gte=from_date)
        purchases = purchases.filter(created_at__date__gte=from_date)
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        bills = bills.filter(created_at__date__lte=to_date)
        purchases = purchases.filter(created_at__date__lte=to_date)
        expenses = expenses.filter(date__lte=to_date)

    total_sales = sum(
        bill.final_amount
        for bill in bills
    )

    total_purchase = sum(
        purchase.final_amount
        for purchase in purchases
    )

    total_expense = sum(
        expense.amount
        for expense in expenses
    )

    gross_profit = Decimal("0.00")

    items = BillItem.objects.filter(
        bill__in=bills
    )

    for item in items:

        gross_profit += (

            (item.price-item.purchase_price)

            * item.quantity

        )

    profit = gross_profit - Decimal(total_expense)

    if total_sales > 0:

        profit_margin = (
            profit / total_sales
        ) * 100

    else:

        profit_margin = Decimal("0.00")

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/profit_report_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "current_time": current_time,

        "total_sales": total_sales,

        "total_purchase": total_purchase,

        "total_expense": total_expense,

        "gross_profit": gross_profit,

        "profit": profit,

        "profit_margin": round(
            profit_margin,
            2
        )

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Profit_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

@allowed_roles(["Admin","Manager"])
def top_products_pdf(request):

    products = (

        BillItem.objects

        .values("product__name")

        .annotate(

            total_qty=Sum("quantity"),

            total_amount=Sum("total")

        )

        .order_by("-total_qty")

    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(

        "reports/top_products_pdf.html"

    )

    html = template.render({

        "shop": shop,

        "products": products,

        "current_time": current_time,

    })

    response = HttpResponse(

        content_type="application/pdf"

    )

    response["Content-Disposition"] = (

        'inline; filename="Top_Products_Report.pdf"'

    )

    pisa.CreatePDF(

        html,

        dest=response

    )

    return response

from django.db.models import F

@allowed_roles(["Admin","Manager"])
def low_stock_report(request):

    limit = request.GET.get("limit", 10)

    try:
        limit = int(limit)
    except:
        limit = 10

    products = Product.objects.filter(
        quantity__lte=limit
    ).order_by("quantity", "name")

    total_products = products.count()

    context = {

        "products": products,

        "limit": limit,

        "total_products": total_products,

    }

    return render(

        request,

        "reports/low_stock_report.html",

        context

    )

@allowed_roles(["Admin","Manager"])
def low_stock_pdf(request):

    limit = request.GET.get("limit", 10)

    try:
        limit = int(limit)
    except:
        limit = 10

    products = Product.objects.filter(
        quantity__lte=limit
    ).order_by("quantity", "name")

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/low_stock_report_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "products": products,

        "limit": limit,

        "current_time": current_time,

        "total_products": products.count(),

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Low_Stock_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

@allowed_roles(["Admin","Manager"])
def payment_recovery_pdf(request):

    customers = Customer.objects.filter(
        credit_balance__gt=0
    ).order_by("-credit_balance")

    total_recovery = sum(
        customer.credit_balance
        for customer in customers
    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/payment_recovery_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "customers": customers,

        "total_recovery": total_recovery,

        "current_time": current_time,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'inline; filename="Payment_Recovery_Report.pdf"'

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response
@allowed_roles(["Admin","Manager"])
def daily_sales_report(request):

    today = timezone.localdate()

    bills = Bill.objects.filter(
        created_at__date=today
    ).order_by("-created_at")

    total_sales = sum(
        bill.final_amount
        for bill in bills
    )

    cash_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Cash"
    )

    upi_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "UPI"
    )

    credit_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Credit"
    )

    total_bills = bills.count()

    context = {

        "bills": bills,

        "today": today,

        "total_sales": total_sales,

        "cash_sales": cash_sales,

        "upi_sales": upi_sales,

        "credit_sales": credit_sales,

        "total_bills": total_bills,

    }

    return render(

        request,

        "reports/daily_sales_report.html",

        context

    )

@allowed_roles(["Admin","Manager"])
def daily_sales_pdf(request):

    today = timezone.localdate()

    bills = Bill.objects.filter(
        created_at__date=today
    ).order_by("-created_at")

    total_sales = sum(
        bill.final_amount
        for bill in bills
    )

    cash_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Cash"
    )

    upi_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "UPI"
    )

    credit_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Credit"
    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/daily_sales_report_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "current_time": current_time,

        "today": today,

        "bills": bills,

        "total_bills": bills.count(),

        "total_sales": total_sales,

        "cash_sales": cash_sales,

        "upi_sales": upi_sales,

        "credit_sales": credit_sales,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Daily_Sales_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response


from datetime import date

@allowed_roles(["Admin","Manager"])
def monthly_sales_report(request):

    today = date.today()

    month = request.GET.get("month", today.month)

    year = request.GET.get("year", today.year)

    bills = Bill.objects.filter(

        created_at__month=month,

        created_at__year=year

    ).order_by("-created_at")

    total_sales = sum(
        bill.final_amount
        for bill in bills
    )

    cash_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Cash"
    )

    upi_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "UPI"
    )

    credit_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Credit"
    )

    import calendar

    context = {

        "bills": bills,

        "month": int(month),

        "year": int(year),

        "months": [

            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December"),

        ],

        "total_bills": bills.count(),

        "total_sales": total_sales,

        "cash_sales": cash_sales,

        "upi_sales": upi_sales,

        "credit_sales": credit_sales,

    }

 

    return render(

        request,

        "reports/monthly_sales_report.html",

        context

    )


@allowed_roles(["Admin","Manager"])
def monthly_sales_pdf(request):

    from datetime import date

    today = date.today()

    month = request.GET.get("month", today.month)
    year = request.GET.get("year", today.year)

    bills = Bill.objects.filter(
        created_at__month=month,
        created_at__year=year
    ).order_by("-created_at")

    total_sales = sum(
        bill.final_amount
        for bill in bills
    )

    cash_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Cash"
    )

    upi_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "UPI"
    )

    credit_sales = sum(
        bill.final_amount
        for bill in bills
        if bill.payment_method == "Credit"
    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/monthly_sales_report_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "current_time": current_time,

        "month": month,

        "year": year,

        "bills": bills,

        "total_bills": bills.count(),

        "total_sales": total_sales,

        "cash_sales": cash_sales,

        "upi_sales": upi_sales,

        "credit_sales": credit_sales,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'inline; filename="Monthly_Sales_Report.pdf"'

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

@allowed_roles(["Admin","Manager"])
def customer_ledger_report(request):

    customers = Customer.objects.all().order_by("name")

    customer_id = request.GET.get("customer")

    selected_customer = None

    bills = Bill.objects.none()

    total_sales = 0

    total_credit = 0

    total_paid = 0

    current_balance = 0

    if customer_id:

        selected_customer = Customer.objects.get(
            id=customer_id
        )

        bills = Bill.objects.filter(
            customer=selected_customer
        ).order_by("created_at")

        total_sales = sum(
            bill.final_amount
            for bill in bills
        )

        total_credit = sum(
            bill.credit_amount
            for bill in bills
        )

        total_paid = total_sales - total_credit

        current_balance = (
            selected_customer.credit_balance
        )

    context = {

        "customers": customers,

        "selected_customer": selected_customer,

        "bills": bills,

        "total_sales": total_sales,

        "total_credit": total_credit,

        "total_paid": total_paid,

        "current_balance": current_balance,

    }

    return render(

        request,

        "reports/customer_ledger_report.html",

        context

    )

@allowed_roles(["Admin","Manager"])
def customer_ledger_pdf(request):

    customer_id = request.GET.get("customer")

    if not customer_id:
        return HttpResponse("Customer not selected")

    customer = Customer.objects.get(id=customer_id)

    bills = Bill.objects.filter(
        customer=customer
    ).order_by("created_at")

    total_sales = sum(
        bill.final_amount
        for bill in bills
    )

    total_credit = sum(
        bill.credit_amount
        for bill in bills
    )

    total_paid = total_sales - total_credit

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/customer_ledger_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "customer": customer,

        "bills": bills,

        "total_sales": total_sales,

        "total_credit": total_credit,

        "total_paid": total_paid,

        "current_balance": customer.credit_balance,

        "current_time": current_time,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'inline; filename="Customer_Ledger.pdf"'

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

from suppliers.models import Supplier

@allowed_roles(["Admin","Manager"])
def supplier_ledger_report(request):

    suppliers = Supplier.objects.all().order_by("name")

    supplier_id = request.GET.get("supplier")

    selected_supplier = None

    purchases = Purchase.objects.none()

    total_purchase = 0

    total_paid = 0

    pending = 0

    if supplier_id:

        selected_supplier = Supplier.objects.get(
            id=supplier_id
        )

        purchases = Purchase.objects.filter(
            supplier=selected_supplier
        ).order_by("date")

        total_purchase = sum(
            purchase.total_amount
            for purchase in purchases
        )

        total_paid = sum(
            purchase.paid_amount
            for purchase in purchases
        )

        pending = total_purchase - total_paid

    context = {

        "suppliers": suppliers,

        "selected_supplier": selected_supplier,

        "purchases": purchases,

        "total_purchase": total_purchase,

        "total_paid": total_paid,

        "pending": pending,

    }

    return render(

        request,

        "reports/supplier_ledger_report.html",

        context

    )

from suppliers.models import Supplier

@allowed_roles(["Admin","Manager"])
def supplier_ledger_report(request):

    suppliers = Supplier.objects.all().order_by("name")

    supplier_id = request.GET.get("supplier")

    selected_supplier = None

    purchases = Purchase.objects.none()

    total_purchase = Decimal("0")

    total_paid = Decimal("0")

    total_balance = Decimal("0")

    if supplier_id:

        selected_supplier = Supplier.objects.get(
            id=supplier_id
        )

        purchases = Purchase.objects.filter(
            supplier=selected_supplier
        ).order_by("-created_at")

        total_purchase = sum(
            purchase.final_amount
            for purchase in purchases
        )

        total_paid = sum(
            purchase.paid_amount
            for purchase in purchases
        )

        total_balance = sum(
            purchase.balance_amount
            for purchase in purchases
        )

    context = {

        "suppliers": suppliers,

        "selected_supplier": selected_supplier,

        "purchases": purchases,

        "total_purchase": total_purchase,

        "total_paid": total_paid,

        "total_balance": total_balance,

    }

    return render(

        request,

        "reports/supplier_ledger_report.html",

        context

    )

@allowed_roles(["Admin","Manager"])
def supplier_ledger_pdf(request):

    supplier_id = request.GET.get("supplier")

    if not supplier_id:
        return HttpResponse("Supplier not selected")

    supplier = Supplier.objects.get(id=supplier_id)

    purchases = Purchase.objects.filter(
        supplier=supplier
    ).order_by("-created_at")

    total_purchase = sum(
        purchase.final_amount
        for purchase in purchases
    )

    total_paid = sum(
        purchase.paid_amount
        for purchase in purchases
    )

    total_balance = sum(
        purchase.balance_amount
        for purchase in purchases
    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/supplier_ledger_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "supplier": supplier,

        "purchases": purchases,

        "total_purchase": total_purchase,

        "total_paid": total_paid,

        "total_balance": total_balance,

        "current_time": current_time,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'inline; filename="Supplier_Ledger.pdf"'

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

from django.db.models import Count, Sum
@allowed_roles(["Admin","Manager"])
def best_customers_report(request):

    customers = (

        Customer.objects

        .annotate(

            total_bills=Count("bill"),

            total_sales=Sum("bill__final_amount")

        )

        .order_by("-total_sales")

    )

    context = {

        "customers": customers

    }

    return render(

        request,

        "reports/best_customers_report.html",

        context

    )

@allowed_roles(["Admin","Manager"])
def best_customers_pdf(request):

    customers = (

        Customer.objects

        .annotate(

            total_bills=Count("bill"),

            total_sales=Sum("bill__final_amount")

        )

        .order_by("-total_sales")

    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/best_customers_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "customers": customers,

        "current_time": current_time,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Best_Customers_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response


from django.db.models import Count, Sum
@allowed_roles(["Admin","Manager"])
def best_suppliers_report(request):

    suppliers = (

        Supplier.objects

        .annotate(

            total_purchase=Sum("purchase__final_amount"),

            total_orders=Count("purchase")

        )

        .order_by("-total_purchase")

    )

    return render(

        request,

        "reports/best_suppliers_report.html",

        {

            "suppliers": suppliers

        }

    )

@allowed_roles(["Admin","Manager"])
def best_suppliers_pdf(request):

    suppliers = (

        Supplier.objects

        .annotate(

            total_purchase=Sum("purchase__final_amount"),

            total_orders=Count("purchase")

        )

        .order_by("-total_purchase")

    )

    shop = ShopSettings.objects.first()

    current_time = timezone.localtime()

    template = get_template(
        "reports/best_suppliers_pdf.html"
    )

    html = template.render({

        "shop": shop,

        "suppliers": suppliers,

        "current_time": current_time,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Best_Suppliers_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response

@allowed_roles(["Admin","Manager"])
def payment_mode_report(request):

    bills = Bill.objects.all().order_by("-created_at")

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if from_date:
        bills = bills.filter(created_at__date__gte=from_date)

    if to_date:
        bills = bills.filter(created_at__date__lte=to_date)

    cash_bills = bills.filter(payment_method="Cash")
    upi_bills = bills.filter(payment_method="UPI")
    credit_bills = bills.filter(payment_method="Credit")

    context = {

        "cash_count": cash_bills.count(),
        "upi_count": upi_bills.count(),
        "credit_count": credit_bills.count(),

        "cash_total": sum(
            bill.final_amount
            for bill in cash_bills
        ),

        "upi_total": sum(
            bill.final_amount
            for bill in upi_bills
        ),

        "credit_total": sum(
            bill.final_amount
            for bill in credit_bills
        ),

        "from_date": from_date,
        "to_date": to_date,

    }

    return render(
        request,
        "reports/payment_mode_report.html",
        context
    )


@allowed_roles(["Admin","Manager"])
def payment_mode_pdf(request):

    bills = Bill.objects.all().order_by("-created_at")

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if from_date:
        bills = bills.filter(created_at__date__gte=from_date)

    if to_date:
        bills = bills.filter(created_at__date__lte=to_date)

    cash_bills = bills.filter(payment_method="Cash")
    upi_bills = bills.filter(payment_method="UPI")
    credit_bills = bills.filter(payment_method="Credit")

    context = {

        "shop": ShopSettings.objects.first(),

        "current_time": timezone.localtime(),

        "cash_count": cash_bills.count(),

        "upi_count": upi_bills.count(),

        "credit_count": credit_bills.count(),

        "cash_total": sum(
            bill.final_amount
            for bill in cash_bills
        ),

        "upi_total": sum(
            bill.final_amount
            for bill in upi_bills
        ),

        "credit_total": sum(
            bill.final_amount
            for bill in credit_bills
        ),

        "from_date": from_date,

        "to_date": to_date,

    }

    template = get_template(
        "reports/payment_mode_pdf.html"
    )

    html = template.render(context)

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'inline; filename="Payment_Mode_Report.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response
    )

    return response


def dead_stock_report(request):

    days = int(
        request.GET.get(
            "days",
            90
        )
    )

    cutoff_date = timezone.now().date() - timedelta(days=days)

    products = Product.objects.all()

    dead_products = []

    total_value = 0

    for product in products:

        last_sale = BillItem.objects.filter(

            product=product

        ).order_by(

            "-bill__created_at"

        ).first()

        if last_sale:

            last_sale_date = last_sale.bill.created_at.date()

        else:

            last_sale_date = None

        if (

            last_sale_date is None

            or

            last_sale_date <= cutoff_date

        ):

            stock_value = (

                product.quantity *

                product.purchase_price

            )

            total_value += stock_value

            if last_sale_date:

                days_idle = (

                    timezone.now().date()

                    -

                    last_sale_date

                ).days

            else:

                days_idle = "-"

            dead_products.append({

                "product": product,

                "last_sale": last_sale_date,

                "days_idle": days_idle,

                "stock_value": stock_value

            })

    context = {

        "products": dead_products,

        "days": days,

        "total_value": total_value

    }

    return render(

        request,

        "reports/dead_stock_report.html",

        context

    )

def print_dead_stock_report(request):

    days = int(request.GET.get("days", 90))

    cutoff_date = timezone.now() - timedelta(days=days)

    products = Product.objects.all()

    dead_products = []

    total_value = 0

    for product in products:

        last_bill = (
            BillItem.objects
            .filter(product=product)
            .order_by("-bill__created_at")
            .first()
        )

        if last_bill:

            last_sale = last_bill.bill.created_at

            if last_sale > cutoff_date:
                continue

            days_idle = (timezone.now() - last_sale).days

        else:

            last_sale = None
            days_idle = "Never Sold"

        stock_value = product.quantity * product.purchase_price

        total_value += stock_value

        dead_products.append({

            "product": product,

            "last_sale": last_sale,

            "days_idle": days_idle,

            "stock_value": stock_value

        })

    shop = ShopSettings.objects.first()

    context = {

        "shop": shop,

        "products": dead_products,

        "days": days,

        "total_value": total_value,

        "today": timezone.now()

    }

    return render(

        request,

        "reports/dead_stock_print.html",

        context

    )

from django.utils import timezone


def business_position_report(request):

    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    sales = Bill.objects.all()

    purchases = Purchase.objects.all()

    expenses = Expense.objects.all()

    if from_date:

        sales = sales.filter(created_at__date__gte=from_date)

        purchases = purchases.filter(created_at__date__gte=from_date)

        expenses = expenses.filter(date__gte=from_date)

    if to_date:

        sales = sales.filter(created_at__date__lte=to_date)

        purchases = purchases.filter(created_at__date__lte=to_date)
        expenses = expenses.filter(date__lte=to_date)

    total_sales = sales.aggregate(
        total=Sum("final_amount")
    )["total"] or Decimal("0")

    total_purchase = purchases.aggregate(
        total=Sum("final_amount")
    )["total"] or Decimal("0")

    total_expense = expenses.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    business_balance = (

        total_sales

        -

        total_purchase

        -

        total_expense

    )

    if business_balance >= 200000:

        health = "Excellent"

        color = "success"

    elif business_balance >= 50000:

        health = "Good"

        color = "warning"

    else:

        health = "Critical"

        color = "danger"

    context = {

        "shop": ShopSettings.objects.first(),

        "from_date": from_date,

        "to_date": to_date,

        "sales": sales,

        "purchases": purchases,

        "expenses": expenses,

        "total_sales": total_sales,

        "total_purchase": total_purchase,

        "total_expense": total_expense,

        "business_balance": business_balance,

        "health": health,

        "color": color,

        "today": timezone.now(),

    }

    return render(

        request,

        "reports/business_position_report.html",

        context,

    )



def print_business_position_report(request):

    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    sales = Bill.objects.all()
    purchases = Purchase.objects.all()
    expenses = Expense.objects.all()

    if from_date:

        sales = sales.filter(created_at__date__gte=from_date)

        purchases = purchases.filter(
            created_at__date__gte=from_date
        )

        expenses = expenses.filter(
            date__gte=from_date
        )

    if to_date:

        sales = sales.filter(created_at__date__lte=to_date)

        purchases = purchases.filter(
            created_at__date__lte=to_date
        )

        expenses = expenses.filter(
            date__lte=to_date
        )

    total_sales = sales.aggregate(
        total=Sum("final_amount")
    )["total"] or Decimal("0")

    total_purchase = purchases.aggregate(
        total=Sum("final_amount")
    )["total"] or Decimal("0")

    total_expense = expenses.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    business_balance = (
        total_sales
        - total_purchase
        - total_expense
    )

    if business_balance >= 200000:

        health = "Excellent"

        color = "success"

    elif business_balance >= 50000:

        health = "Good"

        color = "warning"

    else:

        health = "Critical"

        color = "danger"

    context = {

        "shop": ShopSettings.objects.first(),

        "from_date": from_date,

        "to_date": to_date,

        "sales": sales,

        "purchases": purchases,

        "expenses": expenses,

        "total_sales": total_sales,

        "total_purchase": total_purchase,

        "total_expense": total_expense,

        "business_balance": business_balance,

        "health": health,

        "color": color,

        "today": timezone.now(),

    }

    return render(

        request,

        "reports/business_position_print.html",

        context,

    )