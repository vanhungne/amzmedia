/**
 * Test SQL Server Connection
 * Kiểm tra kết nối tới database
 */

const sql = require('mssql');
require('dotenv').config();

const config = {
    user: process.env.DB_USER || 'sa',
    password: process.env.DB_PASSWORD || 'Abc12345!',
    server: process.env.DB_SERVER || '14.226.226.126',
    port: parseInt(process.env.DB_PORT || '1433'),
    database: process.env.DB_NAME || 'WorkFlowAdmin',
    options: {
        encrypt: process.env.DB_ENCRYPT === 'true',
        trustServerCertificate: process.env.DB_TRUST_CERT === 'true',
        enableArithAbort: true,
        connectTimeout: 30000,
        requestTimeout: 30000
    },
    pool: {
        max: 10,
        min: 0,
        idleTimeoutMillis: 30000
    }
};

console.log('🔍 Testing SQL Server Connection...');
console.log('📋 Configuration:');
console.log(`   Server: ${config.server}`);
console.log(`   Port: ${config.port}`);
console.log(`   Database: ${config.database}`);
console.log(`   User: ${config.user}`);
console.log(`   Password: ${'*'.repeat(config.password.length)}`);
console.log(`   Encrypt: ${config.options.encrypt}`);
console.log(`   Trust Certificate: ${config.options.trustServerCertificate}`);
console.log('');

async function testConnection() {
    try {
        console.log('⏳ Connecting to SQL Server...');
        const pool = await sql.connect(config);
        console.log('✅ Connected successfully!');
        
        console.log('\n📊 Testing query...');
        const result = await pool.request().query('SELECT @@VERSION as version, DB_NAME() as dbname');
        console.log('✅ Query successful!');
        console.log('\n📋 Database Info:');
        console.log(`   Database: ${result.recordset[0].dbname}`);
        console.log(`   Version: ${result.recordset[0].version.split('\n')[0]}`);
        
        // Check if Users table exists
        console.log('\n🔍 Checking Users table...');
        const tableCheck = await pool.request().query(`
            SELECT COUNT(*) as tableExists 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'Users'
        `);
        
        if (tableCheck.recordset[0].tableExists > 0) {
            console.log('✅ Users table exists');
            
            // Count users
            const userCount = await pool.request().query('SELECT COUNT(*) as count FROM Users');
            console.log(`   Total users: ${userCount.recordset[0].count}`);
            
            // List users
            const users = await pool.request().query('SELECT id, username, role FROM Users');
            if (users.recordset.length > 0) {
                console.log('   Users:');
                users.recordset.forEach(user => {
                    console.log(`     - ${user.username} (${user.role})`);
                });
            }
        } else {
            console.log('⚠️  Users table does not exist!');
            console.log('   Run: npm run migrate');
        }
        
        await pool.close();
        console.log('\n✅ All tests passed!');
        process.exit(0);
        
    } catch (err) {
        console.error('\n❌ Connection failed!');
        console.error('Error details:');
        console.error(`   Code: ${err.code}`);
        console.error(`   Message: ${err.message}`);
        
        if (err.code === 'ESOCKET') {
            console.error('\n💡 Suggestions:');
            console.error('   1. Check if SQL Server is running');
            console.error('   2. Check if port 1433 is open');
            console.error('   3. Check firewall settings');
            console.error('   4. Verify server address: ' + config.server);
        } else if (err.code === 'ELOGIN') {
            console.error('\n💡 Suggestions:');
            console.error('   1. Check username and password');
            console.error('   2. Check if SQL Server Authentication is enabled');
            console.error('   3. Check if user has access to database');
        } else if (err.code === 'ENOTFOUND') {
            console.error('\n💡 Suggestions:');
            console.error('   1. Check server address format');
            console.error('   2. Remove port from server address (use separate port config)');
            console.error('   3. Current format: ' + config.server);
            console.error('   4. Try format: 14.226.226.126 (without ,1433)');
        }
        
        console.error('\n📋 Full error:');
        console.error(err);
        process.exit(1);
    }
}

testConnection();

