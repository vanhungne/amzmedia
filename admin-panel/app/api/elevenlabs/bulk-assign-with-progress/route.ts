import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';
import {
  generateOperationId,
  createOperation,
  updateProgress,
  completeOperation,
  failOperation,
  addError
} from '@/lib/progressTracking';

/**
 * POST /api/elevenlabs/bulk-assign-with-progress
 * Bulk assign keys to a user với progress tracking
 */
async function bulkAssignKeysWithProgress(req: NextRequest) {
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
      .query(`SELECT [id], [username] FROM [dbo].[users] WHERE [id] = @user_id`);
    
    if (userCheck.recordset.length === 0) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }
    
    const username = userCheck.recordset[0].username;
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
          { error: 'Không có keys unassigned với credit > 800' },
          { status: 400 }
        );
      }
      
      if (keysToAssign.length < quantity) {
        return NextResponse.json(
          { 
            error: `Chỉ có ${keysToAssign.length} keys available (yêu cầu ${quantity})`,
            available_count: keysToAssign.length
          },
          { status: 400 }
        );
      }
    } else {
      return NextResponse.json(
        { error: 'Cần cung cấp key_ids hoặc quantity' },
        { status: 400 }
      );
    }
    
    // Create operation
    const operationId = generateOperationId('bulk_assign');
    createOperation(operationId, keysToAssign.length);
    
    // Start processing in background
    processAssignmentInBackground(operationId, keysToAssign, user_id, username);
    
    // Return operation ID immediately
    return NextResponse.json({
      operationId,
      message: `Bắt đầu assign ${keysToAssign.length} keys cho user ${username}`,
      totalKeys: keysToAssign.length,
    });
    
  } catch (error: any) {
    console.error('Bulk assign with progress error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * Process assignment in background
 */
async function processAssignmentInBackground(
  operationId: string,
  keyIds: number[],
  userId: number,
  username: string
) {
  const db = await getDb();
  let successCount = 0;
  let skipCount = 0;

  try {
    for (let i = 0; i < keyIds.length; i++) {
      const keyId = keyIds[i];
      
      try {
        // Update progress
        updateProgress(
          operationId,
          i + 1,
          `Đang assign key ${i + 1}/${keyIds.length} cho user ${username}...`
        );

        // Check key status
        const keyCheck = await db.request()
          .input('key_id', sql.Int, keyId)
          .query(`
            SELECT [id], [api_key], [credit_balance], [status], [assigned_user_id]
            FROM [dbo].[elevenlabs_keys]
            WHERE [id] = @key_id
          `);
        
        if (keyCheck.recordset.length === 0) {
          addError(operationId, `Key #${keyId}`, 'Key không tồn tại');
          skipCount++;
          continue;
        }
        
        const key = keyCheck.recordset[0];
        
        // Skip if already assigned
        if (key.assigned_user_id !== null) {
          addError(operationId, key.api_key.substring(0, 10), 'Đã được assign');
          skipCount++;
          continue;
        }
        
        // Check credit balance
        if (key.credit_balance !== null && key.credit_balance <= 800) {
          addError(
            operationId, 
            key.api_key.substring(0, 10), 
            `Credit không đủ (${key.credit_balance})`
          );
          skipCount++;
          continue;
        }
        
        // Assign the key
        await db.request()
          .input('key_id', sql.Int, keyId)
          .input('user_id', sql.Int, userId)
          .query(`
            UPDATE [dbo].[elevenlabs_keys]
            SET [assigned_user_id] = @user_id, [updated_at] = GETDATE()
            WHERE [id] = @key_id
          `);
        
        successCount++;

        // Add small delay để tránh overwhelm database
        if (i % 10 === 0 && i > 0) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }

      } catch (error: any) {
        console.error(`Error assigning key ${keyId}:`, error);
        addError(operationId, `Key #${keyId}`, error.message);
        skipCount++;
      }
    }

    // Update user's total_keys_received
    if (successCount > 0) {
      await db.request()
        .input('user_id', sql.Int, userId)
        .input('count', sql.Int, successCount)
        .query(`
          UPDATE [dbo].[users]
          SET [total_keys_received] = [total_keys_received] + @count,
              [updated_at] = GETDATE()
          WHERE [id] = @user_id
        `);
    }

    // Complete operation
    completeOperation(
      operationId,
      `✅ Hoàn thành! Đã assign ${successCount} keys cho ${username}. ${skipCount > 0 ? `Bỏ qua ${skipCount} keys.` : ''}`
    );

  } catch (error: any) {
    console.error('Critical error in background assignment:', error);
    failOperation(operationId, `Lỗi nghiêm trọng: ${error.message}`);
  }
}

export const POST = requireAdmin(bulkAssignKeysWithProgress);





