require('dotenv').config();

const express = require('express');
const session = require('express-session'); // 1. REQUIRE THE NEW PACKAGE
const morgan = require('morgan'); // Logs every request automatically
const helmet = require('helmet'); // Adds security headers
const NodeCache = require('node-cache');
const myCache = new NodeCache({ stdTTL: 60 }); // Cache data for 60 seconds
const app = express();




const mysql = require('mysql2');

// 1. Create the database connection pool
const db = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME
});

// 2. Test the connection
db.getConnection((err, connection) => {
    if (err) {
        console.error('Database connection failed: ', err.message);
        return;
    }
    console.log('✅ Successfully connected to MySQL database securely!');
    connection.release();
});

const PORT = 3000;

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('public'));

// Security + request logging
app.use(helmet());
app.use(morgan('dev'));

// 2. SET UP THE SESSION WRISTBAND SYSTEM
// This MUST go below the other app.use lines, but BEFORE your routes!
app.use(session({
    secret: 'my_super_secret_key', // In real life, hide this in your .env file!
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false, // We use false because we are on localhost (HTTP, not HTTPS)
        httpOnly: true, // Prevents JS from stealing the cookie
        sameSite: 'lax' // Required for modern browsers to send cookies
    }
}));

// A "Background" Task Function
function sendWelcomeEmail(username, email) {
    console.log(`[Queue] Starting background job: Sending welcome email to ${email}...`);

    // Simulate a slow task (e.g., waiting 5 seconds)
    setTimeout(() => {
        console.log(`[Queue] ✅ Successfully sent email to ${username} at ${email}!`);
    }, 5000);
}

// Route to handle form submission (CREATE)
app.post('/submit', (req, res) => {
    console.log("Data received from frontend:", req.body);

    const { username, email, age, password } = req.body;

    // Server-side validation
    if (!username || username.length < 3 || !email.includes('@') || age < 18 || age > 99 || !password || password.length < 8) {
        console.log("Server validation tripped!");
        return res.status(400).json({ error: 'Validation Failed' });
    }

    const sql = `INSERT INTO users (username, email, age, password) VALUES (?, ?, ?, ?)`;
    const values = [username, email, age, password];

    db.query(sql, values, (err, result) => {
        if (err) {
            console.error("Database insert failed:", err.message);
            return res.status(500).json({ error: 'Database error or email already exists' });
        }

        console.log("✅ User safely saved to the database! ID:", result.insertId);

        // Offload background work so the user doesn't wait
        sendWelcomeEmail(username, email);

        res.status(200).json({ message: 'User registered successfully!', id: result.insertId });
    });
});

// Route to handle user login (Authentication)
app.post('/login', (req, res) => {
    const { email, password } = req.body;

    // 1. Basic validation
    if (!email || !password) {
        return res.status(400).json({ error: 'Please provide both email and password' });
    }

    // 2. Search the database for this specific email
    const sql = 'SELECT * FROM users WHERE email = ?';

    db.query(sql, [email], (err, results) => {
        if (err) {
            console.error("Database error during login:", err.message);
            return res.status(500).json({ error: 'Internal server error' });
        }

        // 3. If the array is empty, that email doesn't exist in our DB
        if (results.length === 0) {
            console.log("Login failed: Email not found.");
            return res.status(401).json({ error: 'Invalid email or password' });
        }

        // Grab the user data from the results array
        const user = results[0];

        // 4. Compare the provided password with the database password
        if (user.password !== password) {
            console.log("Login failed: Incorrect password.");
            return res.status(401).json({ error: 'Invalid email or password' });
        }

        // 5. Success!
        console.log(`✅ User authenticated successfully: ${user.username}`);
        
        // GIVE THEM THE VIP WRISTBAND HERE:
        req.session.userId = user.id; 

        // We send back a success message, but NEVER the password!
        res.status(200).json({
            message: 'Login successful!',
            user: { id: user.id, username: user.username, email: user.email }
        });
    });
});

// --- NEW CODE STARTS HERE ---
// Route to fetch all registered users (READ)
app.get('/api/users', (req, res) => {
    
    // THE BOUNCER: Check if the user has a session wristband
    if (!req.session.userId) {
        console.log("Blocked an unauthorized attempt to view users!");
        return res.status(401).json({ error: 'Unauthorized: You must log in first!' });
    }

    // 1. Check if the user list is already in cache
    const cachedUsers = myCache.get('allUsers');
    if (cachedUsers) {
        console.log("Serving users from Cache (Fast!)");
        return res.status(200).json(cachedUsers);
    }

    // 2. If not, go to the Database
    const sql = 'SELECT id, username, email, age, created_at FROM users';
    db.query(sql, (err, results) => {
        if (err) {
            console.error("Failed to fetch users:", err.message);
            return res.status(500).json({ error: 'Database error' });
        }

        // 3. Store the result in cache for next time
        myCache.set('allUsers', results);
        console.log("Serving users from Database (Slow)");
        res.status(200).json(results);
    });
});
// --- NEW CODE ENDS HERE ---

app.listen(PORT, () => console.log(`Server running at http://localhost:${PORT}`));