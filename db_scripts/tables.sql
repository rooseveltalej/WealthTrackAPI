CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50),
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Income (
    date DATE NOT NULL,
    userId INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (date, userId),
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE Expenses (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    userId INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE Savings (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    userId INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE Investments (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    userId INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE ExpenseGoals (
    date DATE NOT NULL,
    userId INTEGER NOT NULL,
    value NUMERIC(5, 2) NOT NULL, -- porcentaje
    PRIMARY KEY (date, userId),
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE SavingGoals (
    date DATE NOT NULL,
    userId INTEGER NOT NULL,
    value NUMERIC(5, 2) NOT NULL,
    PRIMARY KEY (date, userId),
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE InvestmentGoals (
    date DATE NOT NULL,
    userId INTEGER NOT NULL,
    value NUMERIC(5, 2) NOT NULL,
    PRIMARY KEY (date, userId),
    FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE
);


