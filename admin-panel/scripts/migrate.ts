import 'dotenv/config';
import { initDatabase, closeDb } from '../lib/db';

async function migrate() {
  try {
    console.log('🚀 Starting database migration...');
    await initDatabase();
    console.log('✅ Migration completed successfully!');
  } catch (error: any) {
    console.error('❌ Migration failed:', error.message);
    process.exit(1);
  } finally {
    await closeDb();
  }
}

migrate();

