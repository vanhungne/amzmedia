import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * POST /api/elevenlabs/bulk-import
 * Bulk import ElevenLabs API keys from text content
 * Body: { keys_text, assigned_user_id }
 * keys_text format: one API key per line
 */
async function bulkImportKeys(req: NextRequest) {
  try {
    const body = await req.json();
    const { keys_text, assigned_user_id } = body;
    const userId = (req as any).user.userId;
    
    if (!keys_text) {
      return NextResponse.json(
        { error: 'keys_text is required' },
        { status: 400 }
      );
    }
    
    // Parse keys from text (one per line)
    const lines = keys_text.split('\n').map((line: string) => line.trim()).filter((line: string) => line.length > 0);
    const validKeys: string[] = [];
    const invalidKeys: string[] = [];
    const duplicateKeys: string[] = [];
    
    // Validate each key
    for (const key of lines) {
      // Skip comments or empty lines
      if (key.startsWith('#') || key.startsWith('//')) {
        continue;
      }
      
      // Validate format (starts with sk_)
      if (!key.startsWith('sk_')) {
        invalidKeys.push(key);
        continue;
      }
      
      validKeys.push(key);
    }
    
    if (validKeys.length === 0) {
      return NextResponse.json(
        { 
          error: 'No valid API keys found',
          invalid_keys: invalidKeys
        },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    const importedKeys: any[] = [];
    const skippedKeys: string[] = [];
    
    // Import each valid key
    for (const key of validKeys) {
      try {
        // Check if key already exists
        const existingKey = await db.request()
          .input('api_key', sql.NVarChar(500), key)
          .query(`SELECT [id] FROM [dbo].[elevenlabs_keys] WHERE [api_key] = @api_key`);
        
        if (existingKey.recordset.length > 0) {
          duplicateKeys.push(key);
          continue;
        }
        
        // Insert key
        const result = await db.request()
          .input('api_key', sql.NVarChar(500), key)
          .input('name', sql.NVarChar(255), null) // Auto-named by admin if needed
          .input('assigned_user_id', sql.Int, assigned_user_id || null)
          .input('created_by', sql.Int, userId)
          .query(`
            INSERT INTO [dbo].[elevenlabs_keys] 
            ([api_key], [name], [assigned_user_id], [created_by])
            OUTPUT INSERTED.*
            VALUES (@api_key, @name, @assigned_user_id, @created_by)
          `);
        
        importedKeys.push(result.recordset[0]);
      } catch (error) {
        console.error(`Failed to import key ${key.slice(0, 15)}...`, error);
        skippedKeys.push(key);
      }
    }
    
    return NextResponse.json({
      success: true,
      imported_count: importedKeys.length,
      duplicate_count: duplicateKeys.length,
      invalid_count: invalidKeys.length,
      skipped_count: skippedKeys.length,
      imported_keys: importedKeys,
      duplicates: duplicateKeys.map(k => `${k.slice(0, 15)}...${k.slice(-8)}`),
      invalid: invalidKeys,
      message: `Successfully imported ${importedKeys.length} keys`
    }, { status: 201 });
    
  } catch (error: any) {
    console.error('Bulk import error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const POST = requireAdmin(bulkImportKeys);


