# Bank Database System - ERD (Entity Relationship Diagram)

## الكيانات (Entities) والعلاقات (Relationships)

---

## الجداول (Tables)

### 1. Customer (العملاء)
| Column       | Type         | Key |
|--------------|--------------|-----|
| CustomerID   | INT          | PK  |
| FirstName    | VARCHAR(50)  |     |
| LastName     | VARCHAR(50)  |     |
| NationalID   | VARCHAR(20)  | UQ  |
| Phone        | VARCHAR(15)  |     |
| Email        | VARCHAR(100) |     |
| Address      | VARCHAR(200) |     |
| DateOfBirth  | DATE         |     |

---

### 2. Branch (الفروع)
| Column      | Type        | Key |
|-------------|-------------|-----|
| BranchID    | INT         | PK  |
| BranchName  | VARCHAR(100)|     |
| Location    | VARCHAR(200)|     |
| Phone       | VARCHAR(15) |     |

---

### 3. Employee (الموظفون)
| Column      | Type        | Key |
|-------------|-------------|-----|
| EmployeeID  | INT         | PK  |
| FirstName   | VARCHAR(50) |     |
| LastName    | VARCHAR(50) |     |
| Position    | VARCHAR(50) |     |
| Salary      | DECIMAL     |     |
| HireDate    | DATE        |     |
| Phone       | VARCHAR(15) |     |
| Email       | VARCHAR(100)|     |
| BranchID    | INT         | FK → Branch |

---

### 4. Account (الحسابات)
| Column      | Type        | Key |
|-------------|-------------|-----|
| AccountID   | INT         | PK  |
| AccountType | VARCHAR(20) |     |
| Balance     | DECIMAL     |     |
| OpenDate    | DATE        |     |
| Status      | VARCHAR(20) |     |
| CustomerID  | INT         | FK → Customer |
| BranchID    | INT         | FK → Branch   |

> AccountType: Savings / Checking / Current
> Status: Active / Inactive / Closed

---

### 5. Transaction (المعاملات)
| Column          | Type        | Key |
|-----------------|-------------|-----|
| TransactionID   | INT         | PK  |
| TransactionType | VARCHAR(20) |     |
| Amount          | DECIMAL     |     |
| TransactionDate | DATETIME    |     |
| Description     | VARCHAR(200)|     |
| BalanceAfter    | DECIMAL     |     |
| AccountID       | INT         | FK → Account |

> TransactionType: Deposit / Withdrawal / Transfer

---

### 6. Loan (القروض)
| Column         | Type        | Key |
|----------------|-------------|-----|
| LoanID         | INT         | PK  |
| LoanType       | VARCHAR(50) |     |
| Amount         | DECIMAL     |     |
| InterestRate   | DECIMAL     |     |
| MonthlyPayment | DECIMAL     |     |
| StartDate      | DATE        |     |
| EndDate        | DATE        |     |
| Status         | VARCHAR(20) |     |
| CustomerID     | INT         | FK → Customer |
| BranchID       | INT         | FK → Branch   |

> LoanType: Personal / Mortgage / Car / Business
> Status: Active / Paid / Defaulted

---

## العلاقات (Relationships)

```
Customer  (1) ──────── (N)  Account
Customer  (1) ──────── (N)  Loan
Branch    (1) ──────── (N)  Account
Branch    (1) ──────── (N)  Employee
Branch    (1) ──────── (N)  Loan
Account   (1) ──────── (N)  Transaction
```

---

## ERD Diagram (Text Representation)

```
┌─────────────┐         ┌─────────────┐
│   BRANCH    │◄────────│  EMPLOYEE   │
│─────────────│  1:N    │─────────────│
│ BranchID PK │         │ EmployeeID  │
│ BranchName  │         │ FirstName   │
│ Location    │         │ LastName    │
│ Phone       │         │ Position    │
└──────┬──────┘         │ Salary      │
       │                │ BranchID FK │
       │ 1:N            └─────────────┘
       │
       ▼
┌─────────────┐   1:N   ┌─────────────────┐
│   ACCOUNT   │◄────────│    CUSTOMER      │
│─────────────│         │─────────────────│
│ AccountID PK│         │ CustomerID PK   │
│ AccountType │         │ FirstName       │
│ Balance     │         │ LastName        │
│ OpenDate    │         │ NationalID      │
│ Status      │         │ Phone           │
│ CustomerID  │         │ Email           │
│ BranchID    │         │ Address         │
└──────┬──────┘         │ DateOfBirth     │
       │                └────────┬────────┘
       │ 1:N                     │ 1:N
       ▼                         ▼
┌───────────────┐        ┌─────────────┐
│  TRANSACTION  │        │    LOAN     │
│───────────────│        │─────────────│
│ TransactionID │        │ LoanID PK   │
│ TransType     │        │ LoanType    │
│ Amount        │        │ Amount      │
│ TransDate     │        │ InterestRate│
│ Description   │        │ StartDate   │
│ BalanceAfter  │        │ EndDate     │
│ AccountID FK  │        │ Status      │
└───────────────┘        │ CustomerID  │
                         │ BranchID    │
                         └─────────────┘
```

---

## ملخص العلاقات

| من       | إلى         | النوع |
|----------|-------------|-------|
| Customer | Account     | One to Many (1:N) - عميل واحد له حسابات كتير |
| Customer | Loan        | One to Many (1:N) - عميل واحد يقدر ياخد قروض كتير |
| Branch   | Account     | One to Many (1:N) - الفرع بيحتوي على حسابات كتير |
| Branch   | Employee    | One to Many (1:N) - الفرع بيحتوي على موظفين كتير |
| Branch   | Loan        | One to Many (1:N) - الفرع بيصدر قروض كتير |
| Account  | Transaction | One to Many (1:N) - الحساب بيحتوي على معاملات كتير |
