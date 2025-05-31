
-- 2) INSERT de ingresos (tabla Income)
-- Solo un inserto por mes (mayo 2023), amount = 5000.00
INSERT INTO Income (date, userid, amount)
VALUES
  ('2023-05-01', 1, 5000.00);


-- 3) INSERT de gastos (tabla Expenses)
-- Varios gastos homogéneos repartidos durante mayo 2023
INSERT INTO Expenses (date, userid, amount, category) VALUES
  ('2023-05-02', 1,  800.00, 'Housing'),
  ('2023-05-04', 1,  120.00, 'Utilities'),
  ('2023-05-06', 1,  450.00, 'Groceries'),
  ('2023-05-10', 1,  200.00, 'Transportation'),
  ('2023-05-15', 1,   80.00, 'Subscriptions'),
  ('2023-05-20', 1,  350.00, 'Dining Out'),
  ('2023-05-25', 1,  800.00, 'Housing'),
  ('2023-05-28', 1,  500.00, 'Entertainment'),
  ('2023-05-30', 1,   90.00, 'Utilities');


-- 4) INSERT de ahorros (tabla Savings)
INSERT INTO Savings (date, userid, amount, category) VALUES
  ('2023-05-01', 1,  500.00, 'Emergency Fund'),
  ('2023-05-15', 1,  400.00, 'Vacation'),
  ('2023-05-28', 1,  300.00, 'Home Purchase');


-- 5) INSERT de inversiones (tabla Investments)
INSERT INTO Investments (date, userid, amount, category) VALUES
  ('2023-05-05', 1,  400.00, 'Stocks'),
  ('2023-05-15', 1,  350.00, 'Bonds'),
  ('2023-05-20', 1,  250.00, 'Crypto');


-- 6) INSERT de metas mensuales (ExpenseGoals, SavingGoals, InvestmentGoals)
-- Supondremos metas: 50% gasto, 20% ahorro, 30% inversión sobre el ingreso total (5000).
INSERT INTO ExpenseGoals     (date, userid, value) VALUES ('2023-05-01', 1, 50.00);
INSERT INTO SavingGoals      (date, userid, value) VALUES ('2023-05-01', 1, 20.00);
INSERT INTO InvestmentGoals  (date, userid, value) VALUES ('2023-05-01', 1, 30.00);



-- Asumiendo que el usuario con email 'test@correo.com' tiene id = 1
INSERT INTO income      (date,     userid, amount)
VALUES ('2025-05-10',   1,      5000.00);

INSERT INTO expenses    (date,     userid, amount,  category) VALUES
                         ('2025-05-02', 1,  800.00,  'Housing'),
                         ('2025-05-06', 1,  450.00,  'Groceries');

INSERT INTO savings     (date,     userid, amount,  category) VALUES
                         ('2025-05-01', 1,  500.00,  'Emergency Fund');

INSERT INTO investments (date,     userid, amount,  category) VALUES
                         ('2025-05-05', 1,  400.00,  'Stocks');

INSERT INTO expensegoals   (date,     userid, value) VALUES ('2025-05-01', 1, 50.00);
INSERT INTO savinggoals    (date,     userid, value) VALUES ('2025-05-01', 1, 20.00);
INSERT INTO investmentgoals(date,     userid, value) VALUES ('2025-05-01', 1, 30.00);

