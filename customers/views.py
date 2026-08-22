from re import search
from urllib import request

from django.shortcuts import render, redirect
from .models import Customer
from .forms import CustomerForm
from billing.models import Bill
from .models import Payment
from decimal import Decimal
from django.core.paginator import Paginator
from django.utils import timezone
from accounts.decorators import allowed_roles
from urllib.parse import quote
from shopsettings.models import ShopSettings
from .models import Customer
from .models import Payment
from .models import CustomerLedger
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.utils import timezone



@allowed_roles(["Admin","Manager","Cashier"])


def customer_list(request):

    search = request.GET.get("search")

    customers = Customer.objects.all().order_by("name")

    if search:
        customers = customers.filter(
            name__icontains=search
        )

    paginator = Paginator(customers, 10)

    page = request.GET.get("page")

    customers = paginator.get_page(page)

    context = {

        "customers": customers,

        "search": search,

        "total_customers": Customer.objects.count()

    }

    return render(
        request,
        "customers/customer_list.html",
        context
    )


@allowed_roles(["Admin","Manager","Cashier"])
def add_customer(request):

    if request.method == "POST":

        form = CustomerForm(request.POST)

        print(request.POST)

        if form.is_valid():

            form.save()

            print("CUSTOMER SAVED")

            return redirect('customer_list')

        else:

            print("FORM ERRORS =", form.errors)

    else:

        form = CustomerForm()

    return render(
        request,
        'customers/add_customer.html',
        {'form': form}
    )

@allowed_roles(["Admin","Manager","Cashier"])
def edit_customer(request, id):

    customer = Customer.objects.get(id=id)

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():

            form.save()

            return redirect('customer_list')

    else:

        form = CustomerForm(instance=customer)

    return render(
        request,
        'customers/edit_customer.html',
        {'form': form}
    )


@allowed_roles(["Admin","Manager","Cashier"])
def delete_customer(request, id):

    customer = Customer.objects.get(id=id)

    customer.delete()

    return redirect('customer_list')

@allowed_roles(["Admin","Manager","Cashier"])
def customer_ledger(request, customer_id):

    customer = Customer.objects.get(
        id=customer_id
    )

    ledger = CustomerLedger.objects.filter(
        customer=customer
    ).order_by("-date")

    context = {

        'customer': customer,
        'ledger' : ledger,
        
        'today': timezone.now().date()

    }

    return render(
        request,
        'customers/ledger.html',
        context
    )

@allowed_roles(["Admin","Manager","Cashier"])
def receive_payment(request, customer_id):

    customer = Customer.objects.get(
        id=customer_id
    )

    if request.method == 'POST':

        amount = request.POST.get(
            'amount'
        )

        Payment.objects.create(

            customer=customer,

            amount=amount

        )

        customer.credit_balance -= Decimal(str(amount))

        if customer.credit_balance < 0:
            customer.credit_balance = 0

        if customer.credit_balance == 0:
            customer.due_date = None

        customer.save()
        last = CustomerLedger.objects.filter(
            customer=customer
        ).order_by("-id").first()

        balance = last.balance if last else customer.credit_balance + Decimal(str(amount))

        CustomerLedger.objects.create(
            customer=customer,
            particular="Payment",
            invoice_no="",
            debit=0,
            credit=Decimal(str(amount)),
            balance=balance - Decimal(str(amount)),
            remarks="Payment Received"
        )


        return redirect(
            'customer_ledger',
            customer_id=customer.id
        )

    context = {

        'customer': customer

    }

    return render(

        request,

        'customers/receive_payment.html',

        context

    )

from urllib.parse import quote
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from accounts.decorators import allowed_roles
from .models import Customer

@allowed_roles(["Admin", "Manager", "Cashier"])
def whatsapp_reminder(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    shop = ShopSettings.objects.first()

    # -------------------------
    # Pending Bills
    # -------------------------

    pending_bills = Bill.objects.filter(

        customer=customer,

        balance_amount__gt=0

    ).order_by("-created_at")[:3]

    # -------------------------
    # Recent Payments
    # -------------------------

    recent_payments = Payment.objects.filter(

        customer=customer

    ).order_by("-created_at")[:2]

    due_date = "-"

    if customer.due_date:

        due_date = customer.due_date.strftime(
            "%d-%m-%Y"
        )

    shop_name = "Jay Bhole Hardware"

    mobile = ""

    if shop:

        if shop.shop_name:

            shop_name = shop.shop_name

        mobile = shop.mobile

    # -------------------------
    # Message Start
    # -------------------------

    message = f"""
🏪 *{shop_name}*

Dear *{customer.name}*,

Greetings from {shop_name}.

This is a friendly reminder regarding your outstanding account.

━━━━━━━━━━━━━━━━━━
📄 *ACCOUNT SUMMARY*
━━━━━━━━━━━━━━━━━━

👤 Customer : {customer.name}

💰 Outstanding :
₹ {customer.credit_balance}

📅 Due Date :
{due_date}

━━━━━━━━━━━━━━━━━━
🧾 *RECENT PENDING BILLS*
━━━━━━━━━━━━━━━━━━
"""
        # -------------------------
    # Pending Bills List
    # -------------------------

    if pending_bills.exists():

        for i, bill in enumerate(pending_bills, start=1):

            message += f"""
{i}️⃣ {bill.invoice_no}
📅 {bill.created_at.strftime("%d-%m-%Y")}
💵 ₹ {bill.balance_amount}
"""

    else:

        message += "\nNo Pending Bills\n"

    # -------------------------
    # Payment History
    # -------------------------

    message += """

━━━━━━━━━━━━━━━━━━
💳 *RECENT PAYMENTS*
━━━━━━━━━━━━━━━━━━
"""

    if recent_payments.exists():

        for payment in recent_payments:

            message += f"""
{payment.created_at.strftime("%d-%m-%Y")}
₹ {payment.amount}
"""

    else:

        message += "\nNo Payment History\n"

    # -------------------------
    # English Ending
    # -------------------------

    message += f"""

━━━━━━━━━━━━━━━━━━

Kindly clear the outstanding amount at your earliest convenience.

📄 Customer Statement available on request.

Thank you for your continued support.

Regards,

*{shop_name}*

📞 {mobile}

━━━━━━━━━━━━━━━━━━
🇮🇳 *मराठी*
━━━━━━━━━━━━━━━━━━

नमस्कार *{customer.name}*,

आपल्या खात्यामध्ये खालीलप्रमाणे थकबाकी बाकी आहे.

💰 थकीत रक्कम
₹ {customer.credit_balance}

📅 देय तारीख
{due_date}

━━━━━━━━━━━━━━━━━━
🧾 *शेवटची थकीत बिले*
━━━━━━━━━━━━━━━━━━
"""

    # -------------------------
    # Marathi Bills
    # -------------------------

    if pending_bills.exists():

        for i, bill in enumerate(pending_bills, start=1):

            message += f"""
{i}️⃣ {bill.invoice_no}
📅 {bill.created_at.strftime("%d-%m-%Y")}
💵 ₹ {bill.balance_amount}
"""

    else:

        message += "\nथकीत बिले नाहीत.\n"

    # -------------------------
    # Marathi Payments
    # -------------------------

    message += """

━━━━━━━━━━━━━━━━━━
💳 *शेवटच्या भरलेल्या रक्कमा*
━━━━━━━━━━━━━━━━━━
"""

    if recent_payments.exists():

        for payment in recent_payments:

            message += f"""
{payment.created_at.strftime("%d-%m-%Y")}
₹ {payment.amount}
"""

    else:

        message += "\nपेमेंट हिस्टरी उपलब्ध नाही.\n"

    message += f"""

━━━━━━━━━━━━━━━━━━

कृपया आपल्या सोयीनुसार लवकरात लवकर थकीत रक्कम जमा करावी.

आपल्या सहकार्याबद्दल धन्यवाद.

🙏 *{shop_name}*

📞 {mobile}
"""

    whatsapp_no = customer.whatsapp or customer.mobile

    return redirect(

        f"https://wa.me/91{whatsapp_no}?text={quote(message)}"

    )
@allowed_roles(["Admin", "Manager", "Cashier"])
def customer_statement(request, customer_id):

    customer = get_object_or_404(
        Customer,
        id=customer_id
    )

    from_date = request.GET.get("from")
    to_date = request.GET.get("to")

    ledger = CustomerLedger.objects.filter(
        customer=customer
    ).order_by("date")

    if from_date:

        ledger = ledger.filter(
            date__date__gte=from_date
        )

    if to_date:

        ledger = ledger.filter(
            date__date__lte=to_date
        )

    total_debit = ledger.aggregate(

        total=Sum("debit")

    )["total"] or 0

    total_credit = ledger.aggregate(

        total=Sum("credit")

    )["total"] or 0

    closing_balance = 0

    last = ledger.last()

    if last:

        closing_balance = last.balance

    context = {

        "shop": ShopSettings.objects.first(),

        "customer": customer,

        "ledger": ledger,

        "total_debit": total_debit,

        "total_credit": total_credit,

        "closing_balance": closing_balance,

        "from_date": from_date,

        "to_date": to_date,

        "today": timezone.now(),

    }

    return render(

        request,

        "customers/customer_statement.html",

        context

    )


from django.http import JsonResponse

def ajax_save_customer(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "status": "error"
            }
        )

    name = request.POST.get("name")
    mobile = request.POST.get("mobile")
    address = request.POST.get("address")
    due_days = request.POST.get("due_days") or 30

    # Duplicate Mobile

    existing = Customer.objects.filter(
        mobile=mobile
    ).first()

    if existing:

        return JsonResponse({

            "status": "exists",

            "id": existing.id,

            "name": existing.name

        })

    customer = Customer.objects.create(

        name=name,

        mobile=mobile,

        address=address,

        due_days=due_days

    )

    return JsonResponse({

        "status": "success",

        "id": customer.id,

        "name": customer.name

    })