import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

/**
 * API endpoint for Python tool to fetch projects
 * GET /api/tool/projects
 * Headers: Authorization: Bearer <token>
 * Returns: { success, projects }
 */
async function getProjectsForTool(req: NextRequest) {
  try {
    const db = await getDb();
    const result = await db.request().query(`
      SELECT 
        p.[id],
        p.[project_id],
        p.[channel_name],
        p.[script_template],
        p.[num_prompts],
        p.[voice_id],
        p.[auto_workflow],
        p.[video_output_folder],
        p.[created_at],
        p.[updated_at]
      FROM [dbo].[projects] p
      WHERE p.[id] IS NOT NULL
      ORDER BY p.[channel_name] ASC
    `);
    
    return NextResponse.json({
      success: true,
      projects: result.recordset,
    });
  } catch (error: any) {
    console.error('Get projects for tool error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Manager và admin đều có thể xem projects
export const GET = requireAuth(getProjectsForTool, ['admin', 'manager', 'user']);

/**
 * POST /api/tool/projects
 * Create new project
 */
async function createProjectForTool(req: NextRequest) {
  try {
    // Check if user is admin
    const authHeader = req.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get user from token
    const token = authHeader.substring(7); // Remove 'Bearer '
    const db = await getDb();
    
    const userResult = await db.request()
      .input('token', sql.NVarChar, token)
      .query(`
        SELECT u.id, u.username, u.role
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = @token AND s.expires_at > GETDATE()
      `);
    
    if (userResult.recordset.length === 0) {
      return NextResponse.json(
        { success: false, error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const user = userResult.recordset[0];
    
    // Only admin can create projects
    if (user.role !== 'admin') {
      return NextResponse.json(
        { success: false, error: 'Forbidden - Admin only' },
        { status: 403 }
      );
    }

    const body = await req.json();
    const { channel_name, script_template, num_prompts, voice_id, auto_workflow } = body;

    if (!channel_name) {
      return NextResponse.json(
        { success: false, error: 'Channel name is required' },
        { status: 400 }
      );
    }

    // Generate UUID for project_id
    const { randomUUID } = await import('crypto');
    const project_id = randomUUID();

    // Insert project
    const result = await db.request()
      .input('project_id', sql.NVarChar, project_id)
      .input('channel_name', sql.NVarChar, channel_name)
      .input('script_template', sql.NVarChar, script_template || '')
      .input('num_prompts', sql.Int, num_prompts || 12)
      .input('voice_id', sql.NVarChar, voice_id || '')
      .input('auto_workflow', sql.Bit, auto_workflow !== false)
      .input('created_by', sql.Int, user.id)
      .query(`
        INSERT INTO projects (
          project_id, channel_name, script_template, 
          num_prompts, voice_id, auto_workflow, created_by
        )
        OUTPUT INSERTED.*
        VALUES (
          @project_id, @channel_name, @script_template,
          @num_prompts, @voice_id, @auto_workflow, @created_by
        )
      `);

    return NextResponse.json({
      success: true,
      project: result.recordset[0]
    });

  } catch (error: any) {
    console.error('Create project error:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const POST = createProjectForTool;






