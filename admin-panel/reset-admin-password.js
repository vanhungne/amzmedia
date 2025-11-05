/**
 * Reset Admin Password
 * Sets admin password to: admin123
 */

const sql = require('mssql');
const bcrypt = require('bcryptjs');
require('dotenv').config();

const config = {
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    server: process.env.DB_SERVER,
    port: parseInt(process.env.DB_PORT || '1433'),
    database: process.env.DB_NAME,
    options: {
        encrypt: process.env.DB_ENCRYPT === 'true',
        trustServerCertificate: process.env.DB_TRUST_CERT === 'true',
        enableArithAbort: true,
    }
};

async function resetPassword() {
    try {
        console.log('🔄 Connecting to database...');
        const pool = await sql.connect(config);
        
        const newPassword = 'admin123';
        const hashedPassword = await bcrypt.hash(newPassword, 10);
        
        console.log('🔐 Resetting admin password...');
        await pool.request()
            .input('password_hash', sql.NVarChar, hashedPassword)
            .query(`UPDATE users SET password_hash = @password_hash WHERE username = 'admin'`);
        
        console.log('✅ Admin password reset successfully!');
        console.log('   Username: admin');
        console.log('   Password: admin123');
        
        await pool.close();
        process.exit(0);
    } catch (err) {
        console.error('❌ Error:', err.message);
        process.exit(1);
    }
}

resetPassword();

