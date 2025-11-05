import { getDb, closeDb } from '../lib/db';

/**
 * Migration script to add key tracking columns to users table
 * Run: npx tsx scripts/add-user-key-tracking.ts
 */
async function addUserKeyTracking() {
  try {
    console.log('🔄 Starting migration: Add user key tracking columns...');
    
    const db = await getDb();
    
    // Add columns to users table if they don't exist
    await db.request().query(`
      -- Add total_keys_received column
      IF NOT EXISTS (
        SELECT * FROM sys.columns 
        WHERE object_id = OBJECT_ID('[dbo].[users]') 
        AND name = 'total_keys_received'
      )
      BEGIN
        ALTER TABLE [dbo].[users]
        ADD [total_keys_received] INT NOT NULL DEFAULT 0;
        PRINT '✅ Added column: total_keys_received';
      END
      ELSE
      BEGIN
        PRINT '⏭️  Column already exists: total_keys_received';
      END

      -- Add total_keys_used column
      IF NOT EXISTS (
        SELECT * FROM sys.columns 
        WHERE object_id = OBJECT_ID('[dbo].[users]') 
        AND name = 'total_keys_used'
      )
      BEGIN
        ALTER TABLE [dbo].[users]
        ADD [total_keys_used] INT NOT NULL DEFAULT 0;
        PRINT '✅ Added column: total_keys_used';
      END
      ELSE
      BEGIN
        PRINT '⏭️  Column already exists: total_keys_used';
      END

      -- Add current_active_keys computed column (for convenience)
      -- This will be calculated as: COUNT of active keys assigned to user
    `);
    
    // Initialize counters for existing users based on historical data
    console.log('🔄 Initializing counters from existing data...');
    
    await db.request().query(`
      -- Update total_keys_received based on assigned_user_id history
      UPDATE u
      SET u.total_keys_received = (
        SELECT COUNT(*) 
        FROM [dbo].[elevenlabs_keys] k 
        WHERE k.assigned_user_id = u.id
      )
      FROM [dbo].[users] u;
      
      -- Update total_keys_used based on keys that have been used
      UPDATE u
      SET u.total_keys_used = (
        SELECT COUNT(*) 
        FROM [dbo].[elevenlabs_keys] k 
        WHERE k.assigned_user_id = u.id 
        AND k.last_used IS NOT NULL
      )
      FROM [dbo].[users] u;
    `);
    
    console.log('✅ Migration completed successfully!');
    console.log('');
    console.log('📊 Summary:');
    console.log('   - Added: total_keys_received (INT)');
    console.log('   - Added: total_keys_used (INT)');
    console.log('   - Initialized counters from existing data');
    
    await closeDb();
    process.exit(0);
  } catch (error: any) {
    console.error('❌ Migration failed:', error.message);
    await closeDb();
    process.exit(1);
  }
}

addUserKeyTracking();

