DROP TABLE IF EXISTS expense;

CREATE TABLE expense (
  id INTEGER PRIMARY KEY,
  username TEXT NOT NULL,
  expense_date TEXT NOT NULL,
  category TEXT,
  amount INT NOT NULL
);
