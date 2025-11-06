import { NextRequest, NextResponse } from 'next/server';
import { getProgress, getAllOperations } from '@/lib/progressTracking';

/**
 * GET /api/operations/[id]/status
 * Lấy trạng thái hiện tại của một operation
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> | { id: string } }
) {
  try {
    // Handle both sync and async params (Next.js 14+ uses Promise)
    const resolvedParams = await Promise.resolve(params);
    let operationId = resolvedParams.id;
    
    // Decode URI component in case of URL encoding
    operationId = decodeURIComponent(operationId);
    
    // Debug logging
    console.log(`[Operations API] Getting status for operation: ${operationId}`);
    console.log(`[Operations API] Current operations in store:`, getAllOperations().map(op => op.operationId));
    
    const progress = getProgress(operationId);

    if (!progress) {
      // Log all available operations for debugging
      const allOps = getAllOperations();
      console.warn(`[Operations API] Operation ${operationId} not found. Available operations:`, allOps.map(op => op.operationId));
      
      return NextResponse.json(
        { 
          error: 'Operation not found',
          message: 'Operation might have been completed and cleaned up, or server was restarted',
          operationId: operationId,
          availableOperations: allOps.map(op => op.operationId)
        },
        { status: 404 }
      );
    }

    // Convert Date objects to ISO strings for JSON serialization
    const serializedProgress = {
      ...progress,
      startedAt: progress.startedAt ? progress.startedAt.toISOString() : undefined,
      completedAt: progress.completedAt ? progress.completedAt.toISOString() : undefined,
    };

    console.log(`[Operations API] Successfully retrieved progress for ${operationId}:`, {
      status: progress.status,
      progress: progress.progress,
      currentItem: progress.currentItem,
      totalItems: progress.totalItems
    });

    return NextResponse.json(serializedProgress);
  } catch (error: any) {
    console.error('[Operations API] Error getting operation status:', error);
    console.error('[Operations API] Error details:', {
      message: error.message,
      stack: error.stack
    });
    return NextResponse.json(
      { 
        error: 'Internal server error',
        details: error.message 
      },
      { status: 500 }
    );
  }
}

