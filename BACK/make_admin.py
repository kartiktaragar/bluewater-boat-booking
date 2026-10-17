
from app.database import get_db
from app.models import User

db = next(get_db())

try:
    email = input("Enter your registered account email: ").strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        print("Account not found. Check the email and try again.")
    else:
        print(f"Account found: {user.email}")
        print(f"Current role: {user.role}")

        confirm = input("Promote this account to admin? Type YES: ").strip()

        if confirm == "YES":
            user.role = "admin"
            db.commit()
            print("Success! Your account is now an admin.")
        else:
            print("No changes made.")
finally:
    db.close()
