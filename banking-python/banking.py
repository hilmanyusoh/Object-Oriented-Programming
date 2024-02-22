from abc import ABCMeta, abstractmethod
from random import randint
import psycopg2

class Account(metaclass=ABCMeta):
    @abstractmethod
    def createAccount(self):
        return 0
    
    @abstractmethod
    def authenticate(self):
        return 0
    
    @abstractmethod
    def withdraw(self):
        return 0
    
    @abstractmethod
    def deposit(self):
        return 0
    
    @abstractmethod
    def transfer(self):
        return 0
    
    @abstractmethod
    def displaybalance(self):
        return 0

class SavingAccount(Account):
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="12345678",
            database="postgres"
        )
        self.cursor = self.conn.cursor()
        self.savingAccounts = {}

    def createAccount(self, name, initialDeposit):
        self.accountNumber = randint(10000, 99999)
        self.savingAccounts[self.accountNumber] = [name, initialDeposit]
        self.cursor.execute("INSERT INTO accounts (account_number, account_holder, initial_deposit, withdrawal_amount, balance, deposit_amount) VALUES (%s, %s, %s, %s, %s, %s)", (self.accountNumber, name, initialDeposit, 0, initialDeposit, 0))
        self.conn.commit()
        print("Your account is successfully created, Your account number is {}".format(self.accountNumber))

    def authenticate(self, name, accountNumber):
        self.cursor.execute("SELECT account_holder FROM accounts WHERE account_number = %s", (accountNumber,))
        result = self.cursor.fetchone()
        if result and result[0] == name:
            print("Authentication Successful!")
            self.accountNumber = accountNumber
            return True
        print("Authentication failed")
        return False


    def withdraw(self, withdrawAmount):
        if withdrawAmount > self.savingAccounts[self.accountNumber][1]:
            print("Insufficient Balance")
        else:
            self.savingAccounts[self.accountNumber][1] -= withdrawAmount
            self.cursor.execute("UPDATE accounts SET balance = balance - %s, withdrawal_amount = withdrawal_amount + %s WHERE account_number = %s", (withdrawAmount, withdrawAmount, self.accountNumber))
            self.conn.commit()
            print("Withdraw Successful")
            self.displaybalance(self.accountNumber)

    def deposit(self, depositAmount):
        self.savingAccounts[self.accountNumber][1] += depositAmount
        self.cursor.execute("UPDATE accounts SET balance = balance + %s, deposit_amount = deposit_amount + %s WHERE account_number = %s", (depositAmount, depositAmount, self.accountNumber))
        self.conn.commit()
        print("Deposit Successful")
        self.displaybalance(self.accountNumber)
        
    def transfer(self, sender_accid, receiver_accid, amount):
        self.cursor.execute("SELECT balance FROM accounts WHERE accid = %s", (sender_accid,))
        sender_balance = self.cursor.fetchone()[0]

        if amount > sender_balance:
            print("Insufficient balance for transfer")
            return

        sender_new_balance = sender_balance - amount
        self.cursor.execute("UPDATE accounts SET balance = %s WHERE accid = %s", (sender_new_balance, sender_accid))

        self.cursor.execute("SELECT balance FROM accounts WHERE accid = %s", (receiver_accid,))
        receiver_balance = self.cursor.fetchone()[0]
        receiver_new_balance = receiver_balance + amount
        self.cursor.execute("UPDATE accounts SET balance = %s WHERE accid = %s", (receiver_new_balance, receiver_accid))

        # Record the transfer
        self.cursor.execute("INSERT INTO transfers (sender_accid, receiver_accid, amount) VALUES (%s, %s, %s)",
                            (sender_accid, receiver_accid, amount))

        self.db.commit()
    print("Transfer successful")

    def displaybalance(self, accountNumber):
        print("Available balance: {}".format(self.savingAccounts[accountNumber][1]))

savingAccount = SavingAccount()

while True:
    print("Enter 1 to open an account")
    print("Enter 2 to access an existing account")
    print("Enter 3 to exit")
    userChoice = int(input())
    
    if userChoice == 1:
        name = input("Enter your name: ")
        initialDeposit = float(input("Enter initial deposit: "))
        savingAccount.createAccount(name, initialDeposit)
    elif userChoice == 2:
        name = input("Enter name: ")
        accountNumber = int(input("Enter account number: "))
        authenticateStatus = savingAccount.authenticate(name, accountNumber)
        if authenticateStatus:
            while True:
                print("Enter 1 to withdraw")
                print("Enter 2 to deposit")
                print("Enter 3 to transfer")
                print("Enter 4 to display balance")
                print("Enter 5 to exit")
                userChoice = int(input())
                if userChoice == 1:
                    withdrawAmount = float(input("Enter withdrawal amount: "))
                    savingAccount.withdraw(withdrawAmount)
                elif userChoice == 2:
                    depositAmount = float(input("Enter deposit amount: "))
                elif userChoice == 3:
                    sender_accid, receiver_accid, amount = float(input("Enter transfer money"))
                    savingAccount.deposit(depositAmount)
                elif userChoice == 4:
                    savingAccount.displaybalance(accountNumber)
                elif userChoice == 5:
                    break
    elif userChoice == 3:
        break
