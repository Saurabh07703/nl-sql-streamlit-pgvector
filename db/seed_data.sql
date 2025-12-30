INSERT INTO departments (name) VALUES
('HR'), ('Engineering'), ('Sales'), ('Finance');

INSERT INTO employees (name, department_id, email, salary) VALUES
('John Doe', 2, 'john@company.com', 85000),
('Emily Smith', 1, 'emily@company.com', 60000),
('Rahul Verma', 3, 'rahul@company.com', 75000),
('Aditi Sharma', 2, 'aditi@company.com', 95000);

INSERT INTO products (name, price) VALUES
('Gold Ring', 1200),
('Silver Necklace', 800),
('Diamond Bracelet', 4500),
('Platinum Chain', 5200);

INSERT INTO orders (customer_name, employee_id, order_total, order_date) VALUES
('Rohan Mehta', 1, 2300, '2024-01-10'),
('Ananya Gupta', 2, 5200, '2024-02-05'),
('David Paul', 3, 1200, '2024-02-15'),
('Sneha Rao', 4, 3100, '2024-03-02');
