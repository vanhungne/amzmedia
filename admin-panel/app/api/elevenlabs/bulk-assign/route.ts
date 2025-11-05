import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * POST /api/elevenlabs/bulk-assign
 * Bulk assign keys to a user
 * Body: { user_id, key_ids: [1, 2, 3], quantity }
 * - If key_ids provided: assign specific keys
 * - If quantity provided: assign N unassigned keys
 */
async function bulkAssignKeys(req: NextRequest) {
  try {
    const body = await req.json();
    const { user_id, key_ids, quantity } = body;
    
    if (!user_id) {
      return NextResponse.json(
        { error: 'user_id is required' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    
    // Check if user exists
    const userCheck = await db.request()
      .input('user_id', sql.Int, user_id)
      .query(`SELECT [id] FROM [dbo].[users] WHERE [id] = @user_id`);
    
    if (userCheck.recordset.length === 0) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }
    
    let keysToAssign: number[] = [];
    
    // Mode 1: Assign specific keys by ID
    if (key_ids && Array.isArray(key_ids) && key_ids.length > 0) {
      keysToAssign = key_ids;
    }
    // Mode 2: Assign N unassigned keys (only keys with credit > 800)
    else if (quantity && quantity > 0) {
      const unassignedKeys = await db.request()
        .input('quantity', sql.Int, quantity)
        .query(`
          SELECT TOP (@quantity) [id], [credit_balance]
          FROM [dbo].[elevenlabs_keys] 
          WHERE [assigned_user_id] IS NULL 
            AND [status] = 'active'
            AND ([credit_balance] IS NULL OR [credit_balance] > 800)
          ORDER BY [credit_balance] DESC, [created_at] ASC
        `);
      
      keysToAssign = unassignedKeys.recordset.map(k => k.id);
      
      if (keysToAssign.length === 0) {
        return NextResponse.json(
          { error: 'No unassigned keys with credit > 800 available' },
          { status: 400 }
        );
      }
      
      if (keysToAssign.length < quantity) {
        return NextResponse.json(
          { 
            error: `Only ${keysToAssign.length} keys with credit > 800 available (requested ${quantity})`,
            available_count: keysToAssign.length
          },
          { status: 400 }
        );
      }
    } else {
      return NextResponse.json(
        { error: 'Either key_ids or quantity must be provided' },
        { status: 400 }
      );
    }
    
    // Assign keys
    const assignedKeys: any[] = [];
    let successCount = 0;
    
    for (const keyId of keysToAssign) {
      try {
        // Check if key meets credit requirement before assigning
        const keyCheck = await db.request()
          .input('key_id', sql.Int, keyId)
          .query(`
            SELECT [id], [credit_balance], [status], [assigned_user_id]
            FROM [dbo].[elevenlabs_keys]
            WHERE [id] = @key_id
          `);
        
        if (keyCheck.recordset.length === 0) {
          console.warn(`Key ${keyId} not found, skipping`);
          continue;
        }
        
        const key = keyCheck.recordset[0];
        
        // Skip if already assigned
        if (key.assigned_user_id !== null) {
          console.warn(`Key ${keyId} already assigned, skipping`);
          continue;
        }
        
        // Check credit balance (must be > 800 or NULL)
        if (key.credit_balance !== null && key.credit_balance <= 800) {
          console.warn(`Key ${keyId} has insufficient credit (${key.credit_balance}), skipping`);
          continue;
        }
        
        // Assign the key
        await db.request()
          .input('key_id', sql.Int, keyId)
          .input('user_id', sql.Int, user_id)
          .query(`
            UPDATE [dbo].[elevenlabs_keys]
            SET [assigned_user_id] = @user_id, [updated_at] = GETDATE()
            WHERE [id] = @key_id
          `);
        
        successCount++;
        
        // Get updated key info
        const keyInfo = await db.request()
          .input('key_id', sql.Int, keyId)
          .query(`SELECT * FROM [dbo].[elevenlabs_keys] WHERE [id] = @key_id`);
        
        if (keyInfo.recordset.length > 0) {
          assignedKeys.push(keyInfo.recordset[0]);
        }
      } catch (error) {
        console.error(`Failed to assign key ${keyId}:`, error);
      }
    }
    
    // Increment user's total_keys_received counter
    if (successCount > 0) {
      await db.request()
        .input('user_id', sql.Int, user_id)
        .input('count', sql.Int, successCount)
        .query(`
          UPDATE [dbo].[users]
          SET [total_keys_received] = [total_keys_received] + @count,
              [updated_at] = GETDATE()
          WHERE [id] = @user_id
        `);
    }
    
    return NextResponse.json({
      success: true,
      assigned_count: assignedKeys.length,
      assigned_keys: assignedKeys,
      message: `Successfully assigned ${assignedKeys.length} keys to user`
    });
    
  } catch (error: any) {
    console.error('Bulk assign error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const POST = requireAdmin(bulkAssignKeys);


