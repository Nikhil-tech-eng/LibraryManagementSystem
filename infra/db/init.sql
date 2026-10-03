-- ==============================================================================
-- Containerized Library Management System (LMS) - PostgreSQL Schema & Seed Data
-- ==============================================================================

CREATE TABLE IF NOT EXISTS members (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'member', -- 'member', 'librarian', 'admin'
    membership_status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'active', 'suspended'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    genre VARCHAR(100) NOT NULL,
    published_year INT NOT NULL,
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    cover_image_url TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS borrow_records (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
    member_id INT NOT NULL REFERENCES members(id) ON DELETE RESTRICT,
    borrow_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP WITH TIME ZONE,
    return_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'ISSUED', 'REJECTED', 'RETURNED'
    fine_amount NUMERIC(10,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications_log (
    id SERIAL PRIMARY KEY,
    recipient_email VARCHAR(255) NOT NULL,
    member_id INT REFERENCES members(id) ON DELETE SET NULL,
    subject VARCHAR(255) NOT NULL,
    message_type VARCHAR(50) NOT NULL, -- 'CHECKOUT', 'DUE_REMINDER', 'RETURN_RECEIPT', 'OVERDUE_NOTICE'
    content TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'SENT', -- 'SENT', 'FAILED', 'PENDING'
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- High-throughput query indexes
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_borrow_records_member_id ON borrow_records(member_id);
CREATE INDEX IF NOT EXISTS idx_borrow_records_book_id ON borrow_records(book_id);
CREATE INDEX IF NOT EXISTS idx_borrow_records_status ON borrow_records(status);
CREATE INDEX IF NOT EXISTS idx_notifications_recipient ON notifications_log(recipient_email);

-- ==============================================================================
-- Seed Data: Members
-- Passwords:
-- librarian@library.org -> admin123
-- alice@library.org     -> user123
-- bob@library.org       -> user123
-- ==============================================================================
INSERT INTO members (email, password_hash, full_name, role, membership_status) VALUES
('librarian@library.org', '$2b$12$AkizrGVkUrfJy/9epRQ.euSeRafmJQyyCL9fV5W/4rARggT8GCHPC', 'Elena Vance (Chief Librarian)', 'librarian', 'active'),
('alice@library.org', '$2b$12$SPIa.nlSv.oPheAqY3XTfuKWSwCb2FhvQO6YS5DdIXp5qtDT3XK6m', 'Alice Johnson', 'member', 'active'),
('bob@library.org', '$2b$12$SPIa.nlSv.oPheAqY3XTfuKWSwCb2FhvQO6YS5DdIXp5qtDT3XK6m', 'Bob Martinez', 'member', 'active')
ON CONFLICT (email) DO NOTHING;

-- ==============================================================================
-- Seed Data: 20 Varied Books across disciplines
-- ==============================================================================
INSERT INTO books (title, author, isbn, genre, published_year, total_copies, available_copies, cover_image_url, description) VALUES
('Designing Data-Intensive Applications', 'Martin Kleppmann', '978-1449373320', 'Computer Science', 2017, 6, 5, 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80', 'The definitive guide to distributed databases, replication, and data processing systems.'),
('Kubernetes in Action, Second Edition', 'Marko Lukša', '978-1617293726', 'Cloud Computing', 2024, 8, 7, 'https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=500&auto=format&fit=crop&q=80', 'Master container orchestration, declarative deployments, networking, and security on Kubernetes.'),
('Clean Architecture', 'Robert C. Martin', '978-0134494166', 'Software Engineering', 2017, 5, 5, 'https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=500&auto=format&fit=crop&q=80', 'A craftsman guide to software structure, boundary design, and enterprise rules.'),
('Site Reliability Engineering', 'Betsy Beyer et al.', '978-1491929124', 'DevOps & SRE', 2016, 4, 3, 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=500&auto=format&fit=crop&q=80', 'How Google runs production systems at scale with automation, SLOs, and blameless postmortems.'),
('Building Microservices, 2nd Edition', 'Sam Newman', '978-1492034025', 'Software Architecture', 2021, 5, 4, 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop&q=80', 'Designing fine-grained systems, service boundaries, communication patterns, and sagas.'),
('Dune', 'Frank Herbert', '978-0441172719', 'Science Fiction', 1965, 10, 8, 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80', 'Set on the desert planet Arrakis, a monumental epic of politics, religion, and ecology.'),
('Neuromancer', 'William Gibson', '978-0441569595', 'Cyberpunk', 1984, 4, 4, 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=500&auto=format&fit=crop&q=80', 'The seminal cyberpunk novel that introduced cyberspace, matrix constructs, and AI constructs.'),
('Deep Learning', 'Ian Goodfellow et al.', '978-0262035613', 'Artificial Intelligence', 2016, 5, 5, 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=500&auto=format&fit=crop&q=80', 'Mathematical foundations of neural networks, representation learning, and modern computer vision.'),
('The Pragmatic Programmer', 'David Thomas & Andrew Hunt', '978-0135957059', 'Software Engineering', 2019, 7, 6, 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=500&auto=format&fit=crop&q=80', 'Your journey to mastery: pragmatic philosophy, tooling, orthogonal design, and career growth.'),
('Domain-Driven Design', 'Eric Evans', '978-0321125217', 'Software Architecture', 2003, 3, 3, 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80', 'Tackling complexity in the heart of software using ubiquitous language and bounded contexts.'),
('Continuous Delivery', 'Jez Humble & David Farley', '978-0321601919', 'DevOps & SRE', 2010, 4, 4, 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=500&auto=format&fit=crop&q=80', 'Reliable software releases through build, test, and deployment automation pipelines.'),
('Database Internals', 'Alex Petrov', '978-1492040347', 'Computer Science', 2019, 4, 4, 'https://images.unsplash.com/photo-1507842229451-7f01be7fe730?w=500&auto=format&fit=crop&q=80', 'A deep dive into distributed storage engines, B-trees, LSM-trees, and consensus algorithms.'),
('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', '978-0062316097', 'History & Anthropology', 2015, 6, 5, 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80', 'From the cognitive revolution to the modern era: an inquiry into human history.'),
('Meditations', 'Marcus Aurelius', '978-0812968255', 'Philosophy', 2002, 5, 5, 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80', 'Personal writings of the Roman Emperor on Stoic philosophy, duty, resilience, and virtue.'),
('Introduction to Algorithms (CLRS)', 'Cormen et al.', '978-0262046305', 'Computer Science', 2022, 5, 4, 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&auto=format&fit=crop&q=80', 'Comprehensive reference covering sorting, graph algorithms, dynamic programming, and complexity.'),
('The Linux Programming Interface', 'Michael Kerrisk', '978-1593272203', 'Systems Programming', 2010, 3, 3, 'https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=500&auto=format&fit=crop&q=80', 'The definitive handbook for Linux and UNIX system programming: processes, signals, sockets, and memory.'),
('Cloud Native Patterns', 'Cornelia Davis', '978-1617294297', 'Cloud Computing', 2019, 4, 4, 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop&q=80', 'Designing change-tolerant, scalable software with microservices and dynamic orchestrators.'),
('Designing Distributed Systems', 'Brendan Burns', '978-1491983645', 'Cloud Computing', 2018, 5, 5, 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500&auto=format&fit=crop&q=80', 'Patterns and paradigms for scalable, reliable services by the co-founder of Kubernetes.'),
('Atomic Habits', 'James Clear', '978-0735211292', 'Personal Development', 2018, 8, 7, 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&auto=format&fit=crop&q=80', 'An easy and proven way to build good habits and break bad ones through tiny changes.'),
('Fahrenheit 451', 'Ray Bradbury', '978-1451673319', 'Fiction', 1953, 6, 6, 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80', 'A dystopian vision of a future American society where books are outlawed and burned.')
ON CONFLICT (isbn) DO NOTHING;

-- Initial Borrow Records
INSERT INTO borrow_records (book_id, member_id, borrow_date, due_date, status, fine_amount) VALUES
(1, 2, CURRENT_TIMESTAMP - INTERVAL '5 days', CURRENT_TIMESTAMP + INTERVAL '9 days', 'ISSUED', 0.00),
(2, 2, CURRENT_TIMESTAMP - INTERVAL '18 days', CURRENT_TIMESTAMP - INTERVAL '4 days', 'ISSUED', 4.00),
(4, 3, CURRENT_TIMESTAMP - INTERVAL '2 days', CURRENT_TIMESTAMP + INTERVAL '12 days', 'ISSUED', 0.00),
(6, 3, CURRENT_TIMESTAMP - INTERVAL '10 days', CURRENT_TIMESTAMP + INTERVAL '4 days', 'ISSUED', 0.00);

-- Safe migration for databases created by the original direct-checkout schema.
ALTER TABLE borrow_records ALTER COLUMN due_date DROP NOT NULL;
ALTER TABLE borrow_records ALTER COLUMN status SET DEFAULT 'PENDING';
UPDATE borrow_records SET status = 'ISSUED' WHERE status IN ('BORROWED', 'OVERDUE');

-- Initial Notifications Log
INSERT INTO notifications_log (recipient_email, member_id, subject, message_type, content, status) VALUES
('alice@library.org', 2, 'Book Checkout Confirmation: Designing Data-Intensive Applications', 'CHECKOUT', 'Dear Alice, you have successfully checked out Designing Data-Intensive Applications. Due date is in 14 days.', 'SENT'),
('alice@library.org', 2, 'OVERDUE NOTICE: Kubernetes in Action, Second Edition', 'OVERDUE_NOTICE', 'Dear Alice, your loan for Kubernetes in Action is overdue by 4 days. Please return it to avoid additional fees.', 'SENT'),
('bob@library.org', 3, 'Book Checkout Confirmation: Site Reliability Engineering', 'CHECKOUT', 'Dear Bob, your checkout for Site Reliability Engineering has been confirmed.', 'SENT');
