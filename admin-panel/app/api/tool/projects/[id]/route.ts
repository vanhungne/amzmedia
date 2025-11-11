import { NextRequest, NextResponse } from 'next/server';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * API endpoint for Python tool to update/delete projects
 * PUT /api/tool/projects/[id] - Update project
 * DELETE /api/tool/projects/[id] - Delete project
 */

// Verify token and get user
async function verifyToken(req: NextRequest) {
  const authHeader = req.headers.get('authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }

  const token = authHeader.substring(7);
  
  try {
    const db = await getDb();
    const result = await db.request()
      .input('token', sql.NVarChar, token)
      .query(`
        SELECT u.id, u.username, u.role
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = @token AND s.expires_at > GETDATE()
      `);
    
    if (result.recordset.length > 0) {
      return result.recordset[0];
    }
  } catch (error) {
    console.error('Token verification error:', error);
  }
  
  return null;
}

/**
 * PUT /api/tool/projects/[id]
 * Update existing project
 */
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Verify authentication
    const user = await verifyToken(req);
    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Manager và admin đều có thể update projects
    if (user.role !== 'admin' && user.role !== 'manager') {
      return NextResponse.json(
        { success: false, error: 'Forbidden - Admin or Manager only' },
        { status: 403 }
      );
    }

    const projectId = params.id;
    const body = await req.json();
    const { channel_name, script_template, num_prompts, voice_id, auto_workflow } = body;

    if (!channel_name) {
      return NextResponse.json(
        { success: false, error: 'Channel name is required' },
        { status: 400 }
      );
    }

    const db = await getDb();
    
    // Check if project exists
    const checkResult = await db.request()
      .input('project_id', sql.NVarChar, projectId)
      .query('SELECT id FROM projects WHERE project_id = @project_id');
    
    if (checkResult.recordset.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Project not found' },
        { status: 404 }
      );
    }

    // Update project
    await db.request()
      .input('project_id', sql.NVarChar, projectId)
      .input('channel_name', sql.NVarChar, channel_name)
      .input('script_template', sql.NVarChar, script_template || '')
      .input('num_prompts', sql.Int, num_prompts || 12)
      .input('voice_id', sql.NVarChar, voice_id || '')
      .input('auto_workflow', sql.Bit, auto_workflow !== false)
      .query(`
        UPDATE projects
        SET 
          channel_name = @channel_name,
          script_template = @script_template,
          num_prompts = @num_prompts,
          voice_id = @voice_id,
          auto_workflow = @auto_workflow,
          updated_at = GETDATE()
        WHERE project_id = @project_id
      `);

    return NextResponse.json({
      success: true,
      message: 'Project updated successfully'
    });

  } catch (error: any) {
    console.error('Update project error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/tool/projects/[id]
 * Delete project
 */
export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Verify authentication
    const user = await verifyToken(req);
    if (!user) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Only admin can delete projects
    if (user.role !== 'admin') {
      return NextResponse.json(
        { success: false, error: 'Forbidden - Admin only' },
        { status: 403 }
      );
    }

    const projectId = params.id;
    const db = await getDb();
    
    // Check if project exists
    const checkResult = await db.request()
      .input('project_id', sql.NVarChar, projectId)
      .query('SELECT id FROM projects WHERE project_id = @project_id');
    
    if (checkResult.recordset.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Project not found' },
        { status: 404 }
      );
    }

    // Delete project
    await db.request()
      .input('project_id', sql.NVarChar, projectId)
      .query('DELETE FROM projects WHERE project_id = @project_id');

    return NextResponse.json({
      success: true,
      message: 'Project deleted successfully'
    });

  } catch (error: any) {
    console.error('Delete project error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

