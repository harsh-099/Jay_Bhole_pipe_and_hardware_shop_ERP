from django.db import models

class Customer(models.Model):

    name = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=15
    )

    address = models.TextField()

    udhari = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    credit_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    

    due_date = models.DateField(
        null=True,
        blank=True
    )

    due_days = models.PositiveIntegerField(
        default=30
    )

    whatsapp = models.CharField(
        max_length=15,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

class CustomerLedger(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="ledger"
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    PARTICULAR = (

        ("Sale", "Sale"),

        ("Payment", "Payment"),

        ("Sale Return", "Sale Return"),

        ("Opening", "Opening"),

    )

    particular = models.CharField(
        max_length=30,
        choices=PARTICULAR
    )

    invoice_no = models.CharField(
        max_length=30,
        blank=True,
        default=""
    )

    debit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    remarks = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:

        ordering = ["date"]

    def __str__(self):

        return f"{self.customer.name} - {self.particular}"


    
class Payment(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    notes = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.customer.name} - ₹{self.amount}"