import json
import os

class MultiLevelUSSDGateway:
    def __init__(self):
        self.db_file = "db.json"
        # Seed the local database file if it doesn't exist yet
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({"237600000000": 5000.0}, f, indent=4)
        
        # Volatile session storage (Resets when script exits, mimicking Redis caching)
        self.session_states = {}

    def _read_balance(self, phone_number: str) -> float:
        """Reads balance data directly from the persistent JSON database file."""
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
            return data.get(phone_number, 0.0)
        except (IOError, json.JSONDecodeError):
            return 0.0

    def _write_balance(self, phone_number: str, new_balance: float):
        """Writes updated balance back safely to the JSON database file."""
        data = {}
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass
                
        data[phone_number] = new_balance
        
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    def process_input(self, phone_number: str, user_input: str) -> str:
        """Processes single input strokes guided by the user's current session state."""
        user_input = user_input.strip()

        # Rule 1: Dialing the shortcode always boots or resets the session state
        if user_input == "*123#":
            self.session_states[phone_number] = "MAIN_MENU"
            return (
                "Welcome to QuickMoney!\n"
                "1. Check Balance\n"
                "2. Request 1000 XAF Loan"
            )

        current_state = self.session_states.get(phone_number, "IDLE")

        if current_state == "IDLE":
            return "No active session. Dial *123# to begin."

        # --- STATE: MAIN_MENU ---
        if current_state == "MAIN_MENU":
            if user_input == "1":
                balance = self._read_balance(phone_number)
                self.session_states[phone_number] = "IDLE"  # Complete session
                return f"Your current balance is: {balance} XAF.\nThank you for using QuickMoney."

            elif user_input == "2":
                # Deepen session state to authorization menu layer
                self.session_states[phone_number] = "AWAITING_LOAN_CONFIRMATION"
                return (
                    "Are you sure you want to request a 1000 XAF loan?\n"
                    "1. Confirm\n"
                    "2. Cancel"
                )
            else:
                return "Invalid choice. Choose 1 or 2:\n1. Check Balance\n2. Request Loan"

        # --- STATE: AWAITING_LOAN_CONFIRMATION ---
        elif current_state == "AWAITING_LOAN_CONFIRMATION":
            if user_input == "1":
                # Read, modify, and commit data to file
                current_bal = self._read_balance(phone_number)
                new_bal = current_bal + 1000.0
                self._write_balance(phone_number, new_bal)
                
                self.session_states[phone_number] = "IDLE"  # Complete session
                return f"Loan approved! 1000 XAF has been credited.\nNew Balance: {new_bal} XAF."
            
            elif user_input == "2":
                self.session_states[phone_number] = "IDLE"
                return "Loan request cancelled.\nThank you for using QuickMoney."
            else:
                return "Invalid choice. Press 1 to Confirm or 2 to Cancel."

        return "An error occurred. Please dial *123# again."


if __name__ == "__main__":
    gateway = MultiLevelUSSDGateway()
    mock_phone = "237600000000"
    
    print("=============================================")
    print("       USSD LIVE TERMINAL SIMULATOR         ")
    print("=============================================")
    print("Type 'exit' to shut down the simulation.\n")
    
    while True:
        user_action = input("Enter option/code: ").strip()
        
        if user_action.lower() == 'exit':
            print("Shutting down gateway wrapper.")
            break
            
        if not user_action:
            continue
            
        menu_screen = gateway.process_input(mock_phone, user_action)
        
        print("\n┌────────────────────────────────────────┐")
        print("│             MOBILE SCREEN              │")
        print("├────────────────────────────────────────┤")
        for line in menu_screen.split('\n'):
            print(f"│ {line:<38} │")
        print("└────────────────────────────────────────┘\n")