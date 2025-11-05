import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * POST /api/elevenlabs/[id]/check
 * Check ElevenLabs API key status and credit from ElevenLabs server (Admin only)
 * This endpoint calls ElevenLabs API to verify if the key is working and get credit balance
 */
async function checkElevenLabsKey(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const db = await getDb();
    
    // Get the API key from database
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`
        SELECT 
          [id],
          [api_key],
          [name],
          [status]
        FROM [dbo].[elevenlabs_keys]
        WHERE [id] = @id
      `);
    
    if (result.recordset.length === 0) {
      return NextResponse.json({ error: 'Key not found' }, { status: 404 });
    }
    
    const keyData = result.recordset[0];
    const apiKey = keyData.api_key;
    
    // Call ElevenLabs API to check subscription and credit
    try {
      const response = await fetch('https://api.elevenlabs.io/v1/user/subscription', {
        method: 'GET',
        headers: {
          'xi-api-key': apiKey,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        // API key is invalid or dead
        const errorText = await response.text();
        let errorMessage = 'Unknown error';
        let newStatus = 'dead';
        
        if (response.status === 401) {
          errorMessage = 'Invalid API key';
          newStatus = 'dead';
        } else if (response.status === 429) {
          errorMessage = 'Rate limit exceeded';
          newStatus = 'active'; // Still active, just rate limited
        } else {
          errorMessage = `API error: ${response.status} - ${errorText}`;
        }
        
        // Update key status in database
        await db.request()
          .input('id', sql.Int, parseInt(id))
          .input('status', sql.NVarChar(20), newStatus)
          .input('error_message', sql.NVarChar(sql.MAX), errorMessage)
          .query(`
            UPDATE [dbo].[elevenlabs_keys]
            SET 
              [status] = @status,
              [last_error] = @error_message,
              [updated_at] = GETDATE()
            WHERE [id] = @id
          `);
        
        return NextResponse.json({
          success: false,
          status: newStatus,
          error: errorMessage,
          checked_at: new Date().toISOString()
        });
      }
      
      // Parse subscription data
      const subscriptionData = await response.json();
      
      // Log response for debugging
      console.log(`[Check Key ${id}] ElevenLabs API Response:`, JSON.stringify(subscriptionData, null, 2));
      
      // Calculate available credits
      const characterCount = subscriptionData.character_count || 0;
      const characterLimit = subscriptionData.character_limit || 0;
      const availableCredits = characterLimit - characterCount;
      
      console.log(`[Check Key ${id}] Calculated credits:`, {
        characterCount,
        characterLimit,
        availableCredits
      });
      
      // Determine status - key hết credit (<= 800) không được tính là active
      let newStatus = 'active';
      let errorMessage = null;
      
      if (availableCredits <= 0) {
        newStatus = 'out_of_credit';
        errorMessage = 'No credits remaining';
      } else if (availableCredits <= 800) {
        // Credit <= 800 không được tính là active
        newStatus = 'out_of_credit';
        errorMessage = 'Insufficient credits (must be > 800)';
      } else if (availableCredits < 1000) {
        errorMessage = 'Low credits warning';
      }
      
      // Update key in database
      await db.request()
        .input('id', sql.Int, parseInt(id))
        .input('status', sql.NVarChar(20), newStatus)
        .input('credit_balance', sql.Int, availableCredits)
        .input('error_message', sql.NVarChar(sql.MAX), errorMessage)
        .query(`
          UPDATE [dbo].[elevenlabs_keys]
          SET 
            [status] = @status,
            [credit_balance] = @credit_balance,
            [last_error] = @error_message,
            [last_used] = GETDATE(),
            [updated_at] = GETDATE()
          WHERE [id] = @id
        `);
      
      return NextResponse.json({
        success: true,
        status: newStatus,
        credit_balance: availableCredits,
        subscription_info: {
          tier: subscriptionData.tier || 'free',
          character_count: characterCount,
          character_limit: characterLimit,
          can_extend_character_limit: subscriptionData.can_extend_character_limit || false,
          allowed_to_extend_character_limit: subscriptionData.allowed_to_extend_character_limit || false,
          next_character_count_reset_unix: subscriptionData.next_character_count_reset_unix || null,
          voice_limit: subscriptionData.voice_limit || 0,
          professional_voice_limit: subscriptionData.professional_voice_limit || 0,
          can_use_instant_voice_cloning: subscriptionData.can_use_instant_voice_cloning || false,
          can_use_professional_voice_cloning: subscriptionData.can_use_professional_voice_cloning || false,
        },
        warning: errorMessage,
        checked_at: new Date().toISOString()
      });
      
    } catch (apiError: any) {
      // Network or API call error
      const errorMessage = `Failed to connect to ElevenLabs API: ${apiError.message}`;
      
      await db.request()
        .input('id', sql.Int, parseInt(id))
        .input('error_message', sql.NVarChar(sql.MAX), errorMessage)
        .query(`
          UPDATE [dbo].[elevenlabs_keys]
          SET 
            [last_error] = @error_message,
            [updated_at] = GETDATE()
          WHERE [id] = @id
        `);
      
      return NextResponse.json({
        success: false,
        error: errorMessage,
        checked_at: new Date().toISOString()
      }, { status: 500 });
    }
    
  } catch (error: any) {
    console.error('Check ElevenLabs key error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error.message },
      { status: 500 }
    );
  }
}

export const POST = requireAdmin(checkElevenLabsKey);

