import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * POST /api/elevenlabs/check-all
 * Check all ElevenLabs API keys status and credit from ElevenLabs server (Admin only)
 * This endpoint streams real-time progress as it checks each key
 */
async function checkAllElevenLabsKeys(req: NextRequest): Promise<NextResponse> {
  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      try {
        const db = await getDb();
        
        // Get all API keys
        const result = await db.request().query(`
          SELECT 
            [id],
            [api_key],
            [name],
            [status]
          FROM [dbo].[elevenlabs_keys]
          ORDER BY [id] ASC
        `);
        
        const keys = result.recordset;
        const results = [];
        
        // Send initial message
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          type: 'start', 
          total: keys.length 
        })}\n\n`));
        
        // Check each key
        let checkedCount = 0;
        for (const keyData of keys) {
          const apiKey = keyData.api_key;
          const keyId = keyData.id;
          
          // Send progress message
          checkedCount++;
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            type: 'progress',
            current: checkedCount,
            total: keys.length,
            keyId: keyId,
            keyName: keyData.name || `Key #${keyId}`,
            status: 'checking'
          })}\n\n`));
          
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
              let errorMessage = 'Unknown error';
              let newStatus = 'dead';
              
              if (response.status === 401) {
                errorMessage = 'Invalid API key';
                newStatus = 'dead';
              } else if (response.status === 429) {
                errorMessage = 'Rate limit exceeded';
                newStatus = 'active';
              } else {
                const errorText = await response.text();
                errorMessage = `API error: ${response.status} - ${errorText}`;
              }
              
              // Update key status in database
              await db.request()
                .input('id', sql.Int, keyId)
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
              
              const resultData = {
                id: keyId,
                name: keyData.name,
                success: false,
                status: newStatus,
                error: errorMessage
              };
              results.push(resultData);
              
              // Send result for this key
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
                type: 'result',
                ...resultData
              })}\n\n`));
              
              // Add small delay to avoid rate limiting
              await new Promise(resolve => setTimeout(resolve, 500));
              continue;
            }
            
            // Parse subscription data
            const subscriptionData = await response.json();
            
            // Calculate available credits
            const characterCount = subscriptionData.character_count || 0;
            const characterLimit = subscriptionData.character_limit || 0;
            const availableCredits = characterLimit - characterCount;
            
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
              .input('id', sql.Int, keyId)
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
            
            const resultData = {
              id: keyId,
              name: keyData.name,
              success: true,
              status: newStatus,
              credit_balance: availableCredits,
              tier: subscriptionData.tier || 'free',
              warning: errorMessage
            };
            results.push(resultData);
            
            // Send result for this key
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
              type: 'result',
              ...resultData
            })}\n\n`));
            
          } catch (apiError: any) {
            // Network or API call error
            const errorMessage = `Failed to connect: ${apiError.message}`;
            
            await db.request()
              .input('id', sql.Int, keyId)
              .input('error_message', sql.NVarChar(sql.MAX), errorMessage)
              .query(`
                UPDATE [dbo].[elevenlabs_keys]
                SET 
                  [last_error] = @error_message,
                  [updated_at] = GETDATE()
                WHERE [id] = @id
              `);
            
            const resultData = {
              id: keyId,
              name: keyData.name,
              success: false,
              error: errorMessage
            };
            results.push(resultData);
            
            // Send result for this key
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
              type: 'result',
              ...resultData
            })}\n\n`));
          }
          
          // Add small delay to avoid rate limiting
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        // Calculate summary
        const summary = {
          total: results.length,
          active: results.filter(r => r.success && 'status' in r && r.status === 'active').length,
          dead: results.filter(r => r.success && 'status' in r && r.status === 'dead').length,
          out_of_credit: results.filter(r => r.success && 'status' in r && r.status === 'out_of_credit').length,
          errors: results.filter(r => !r.success).length
        };
        
        // Send final summary
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          type: 'complete',
          summary,
          checked_at: new Date().toISOString()
        })}\n\n`));
        
        controller.close();
        
      } catch (error: any) {
        console.error('Check all ElevenLabs keys error:', error);
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          type: 'error',
          error: 'Internal server error',
          details: error.message
        })}\n\n`));
        controller.close();
      }
    }
  });
  
  return new NextResponse(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}

export const POST = requireAdmin(checkAllElevenLabsKeys);

