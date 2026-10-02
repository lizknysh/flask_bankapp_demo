from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from datetime import datetime
from decimal import Decimal, InvalidOperation
import os

app = Flask(__name__)

# Used for classroom demo messages.
app.secret_key = "swag-classroom-demo-secret"

print("Project folder:", os.getcwd())

# Demo customer account
account = {
    "name": "Elizabeth Knysh",
    "number": "28071",
    "type": "Savings Account",
    "branch": "SWAG",
    "currency": "USD",
}

balance = Decimal("500000.00")

transactions = [
    {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "Opening Balance",
        "amount": Decimal("500000.00"),
        "balance": balance,
    }
]


def read_amount():
    """Read and validate the amount submitted by an HTML form."""
    try:
        amount = Decimal(request.form.get("amount", ""))

        if not amount.is_finite() or amount <= 0:
            return None

        # Accept amounts with no more than two decimal places.
        if amount != amount.quantize(Decimal("0.01")):
            return None

        return amount.quantize(Decimal("0.01"))

    except (InvalidOperation, ValueError):
        return None


def add_transaction(transaction_type, amount):
    """Record an operation with its resulting balance."""
    transactions.append(
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": transaction_type,
            "amount": amount,
            "balance": balance,
        }
    )


@app.route("/")
def home():
    total_deposits = sum(
        (
            transaction["amount"]
            for transaction in transactions
            if transaction["type"] == "Deposit"
        ),
        Decimal("0.00"),
    )

    total_withdrawals = sum(
        (
            transaction["amount"]
            for transaction in transactions
            if transaction["type"] == "Withdrawal"
        ),
        Decimal("0.00"),
    )

    return render_template(
        "index.html",
        account=account,
        balance=balance,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        transactions=list(reversed(transactions)),
    )


@app.route("/deposit", methods=["POST"])
def deposit():
    global balance

    amount = read_amount()

    if amount is None:
        flash(
            "Enter a positive amount with no more than two decimal places.",
            "error",
        )
        return redirect(url_for("home"))

    balance += amount
    add_transaction("Deposit", amount)

    flash(f"Successfully deposited ${amount:,.2f} USD.", "success")

    return redirect(url_for("home"))


@app.route("/withdraw", methods=["POST"])
def withdraw():
    global balance

    amount = read_amount()

    if amount is None:
        flash(
            "Enter a positive amount with no more than two decimal places.",
            "error",
        )
        return redirect(url_for("home"))

    if amount > balance:
        flash(
            "Insufficient funds. Enter an amount within your balance.",
            "error",
        )
        return redirect(url_for("home"))

    balance -= amount
    add_transaction("Withdrawal", amount)

    flash(f"Successfully withdrew ${amount:,.2f} USD.", "success")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)