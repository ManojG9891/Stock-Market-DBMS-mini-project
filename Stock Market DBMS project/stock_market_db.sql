CREATE DATABASE stock_market_db;

USE stock_market_db;

CREATE TABLE account_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    secondname VARCHAR(50) ,
    gender VARCHAR(6) NOT NULL,
    age INT(3) NOT NULL,
    occupation VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    mobilenumber BIGINT NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL,
    total_balance_amount FLOAT
);

CREATE TABLE brokerlogin (
    b_id INT,
    b_firstname VARCHAR(50),
    b_email VARCHAR(100),
    b_password VARCHAR(20)
);

CREATE TABLE loginpage (
    id INT PRIMARY KEY,
    firstname VARCHAR(50),
    email VARCHAR(100),
    password VARCHAR(20)
);

CREATE TRIGGER after_account_details_insert
AFTER INSERT ON account_details
FOR EACH ROW
INSERT INTO loginpage (id,firstname, email, password)
VALUES (NEW.id,NEW.firstname, NEW.email, NEW.password);

CREATE TRIGGER after_account_details_update
AFTER UPDATE ON account_details
FOR EACH ROW
BEGIN
    UPDATE loginpage
    SET firstname = NEW.firstname,
        email = NEW.email,
        password = NEW.password
    WHERE loginpage.id = OLD.id;
END;

CREATE TABLE stock_details (
    stock_id INT PRIMARY KEY,
    stock_name VARCHAR(50) NOT NULL,
    stock_price FLOAT NOT NULL,
    today_gain FLOAT NOT NULL,
    one_year_lowprice FLOAT,
    one_year_highprice FLOAT,
    ceo_name VARCHAR(50) NOT NULL,
    founded YEAR,
    industry VARCHAR(50) NOT NULL,
    headquarters VARCHAR(100) NOT NULL,
    market_cap BIGINT NOT NULL,
    current_year_profit BIGINT NOT NULL
);


INSERT INTO stock_details (stock_id, stock_name, stock_price, today_gain, one_year_lowprice, one_year_highprice, ceo_name, founded, industry, headquarters, market_cap, current_year_profit)
VALUES
(12345, 'Reliance Industries', 2523.25, 2.75, 1800, 2600, 'Mukesh Ambaniaa', 1973, 'Conglomerate', 'Mumbai', 1500000000, 1200000),
(23456, 'Tata Consultancy Services', 3291.25, 2.25, 2500, 3400, 'Rajesh Gopinathan', 1968, 'IT Services', 'Mumbai', 1200000000, 1100000),
(34567, 'Infosys', 1559.55, -1.5, 1200, 1600, 'Salil Parekh', 1981, 'IT Services', 'Bengaluru', 1000000000, 900000),
(45678, 'HDFC Bank', 1423.65, -0.75, 1100, 1500, 'Sashidhar Jagdishan', 1994, 'Banking', 'Mumbai', 1300000000, 950000),
(56789, 'ICICI Bank', 709.5, -1.5, 600, 750, 'Sandeep Bakhshi', 1994, 'Banking', 'Mumbai', 1100000000, 850000),
(63746, 'Asian Paints', 3020.1, 1.25, 2400, 3100, 'Amit Syngle', 1942, 'Chemicals', 'Mumbai', 1600000000, 1300000),
(67291, 'Tata Motors', 1002, 5, 800, 1200, 'Natarajan Chandrasekaran', 1945, 'Automobile', 'Mumbai', 1200000000, 200000),
(67890, 'Bharti Airtel', 563.4, -0.75, 400, 600, 'Gopal Vittal', 1995, 'Telecommunications', 'New Delhi', 900000000, 780000),
(78901, 'Hindustan Unilever', 2309.75, -1.5, 1900, 2400, 'Sanjiv Mehta', 1933, 'FMCG', 'Mumbai', 1400000000, 1100000),
(89012, 'Mahindra & Mahindra', 841.25, 2.25, 700, 900, 'Anand Mahindra', 1945, 'Automobile', 'Mumbai', 1000000000, 800000),
(90123, 'Maruti Suzuki', 7523.6, -0.75, 5500, 7600, 'Kenichi Ayukawa', 1981, 'Automobile', 'Gurugram', 1700000000, 1500000);



CREATE TABLE holdings (
    id INT,
    stock_id INT,
    stock_name VARCHAR(50),
    quantities INT,
    buy_date DATE,
    buy_price FLOAT,
    total_profit FLOAT,
    FOREIGN KEY (id) REFERENCES account_details(id),
    FOREIGN KEY (stock_id) REFERENCES stock_details(stock_id)
);

CREATE TABLE trading_history (
    id INT NOT NULL,
    stock_id INT NOT NULL,
    trading_id INT AUTO_INCREMENT PRIMARY KEY,
    t_type CHAR(4),
    stock_name VARCHAR(50) NOT NULL,
    quantities INT NOT NULL,
    buy_date DATE,
    buy_price FLOAT,
    sell_date DATE,
    sell_price FLOAT,
    FOREIGN KEY (id) REFERENCES account_details(id),
    FOREIGN KEY (stock_id) REFERENCES stock_details(stock_id)
);

CREATE TRIGGER trade_update
AFTER INSERT ON holdings
FOR EACH ROW
INSERT INTO trading_history (t_type, id, stock_id, stock_name, quantities, buy_date, buy_price)
VALUES ('BUY', NEW.id, NEW.stock_id, NEW.stock_name, NEW.quantities, NEW.buy_date, NEW.buy_price);

CREATE TABLE fund_transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    id INT NOT NULL,
    type VARCHAR(50),
    date DATETIME,
    amount FLOAT,
    FOREIGN KEY (id) REFERENCES account_details(id)
);

CREATE TABLE bank_details (
    id INT NOT NULL,
    amount FLOAT,
    card_number BIGINT, 
    expiry_date DATE,
    cvv INT(3),
    date DATETIME,
    FOREIGN KEY (id) REFERENCES account_details(id)
);

CREATE TRIGGER fund_update
AFTER INSERT ON bank_details
FOR EACH ROW
INSERT INTO fund_transaction (id, amount, date, type)
VALUES (NEW.id, NEW.amount, NEW.date, 'DEPOSIT');
