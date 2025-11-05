import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';

// GET single project
async function getProject(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const db = await getDb();
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`
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
          p.[updated_at],
          u.[username] as created_by_username
        FROM [dbo].[projects] p
        LEFT JOIN [dbo].[users] u ON p.[created_by] = u.[id]
        WHERE p.[id] = @id
      `);
    
    if (result.recordset.length === 0) {
      return NextResponse.json({ error: 'Project not found' }, { status: 404 });
    }
    
    return NextResponse.json({ project: result.recordset[0] });
  } catch (error: any) {
    console.error('Get project error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// PUT update project
async function updateProject(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const body = await req.json();
    const { channel_name, script_template, num_prompts, voice_id, auto_workflow, video_output_folder } = body;
    
    const db = await getDb();
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .input('channel_name', sql.NVarChar(255), channel_name)
      .input('script_template', sql.NVarChar(sql.MAX), script_template || null)
      .input('num_prompts', sql.Int, num_prompts || 12)
      .input('voice_id', sql.NVarChar(100), voice_id || null)
      .input('auto_workflow', sql.Bit, auto_workflow !== false)
      .input('video_output_folder', sql.NVarChar(500), video_output_folder || null)
      .query(`
        UPDATE [dbo].[projects]
        SET 
          [channel_name] = @channel_name,
          [script_template] = @script_template,
          [num_prompts] = @num_prompts,
          [voice_id] = @voice_id,
          [auto_workflow] = @auto_workflow,
          [video_output_folder] = @video_output_folder,
          [updated_at] = GETDATE()
        WHERE [id] = @id
      `);
    
    if (result.rowsAffected[0] === 0) {
      return NextResponse.json({ error: 'Project not found' }, { status: 404 });
    }
    
    // Get updated project
    const updated = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`SELECT * FROM [dbo].[projects] WHERE [id] = @id`);
    
    return NextResponse.json({ project: updated.recordset[0] });
  } catch (error: any) {
    console.error('Update project error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// DELETE project
async function deleteProject(req: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const db = await getDb();
    const result = await db.request()
      .input('id', sql.Int, parseInt(id))
      .query(`DELETE FROM [dbo].[projects] WHERE [id] = @id`);
    
    if (result.rowsAffected[0] === 0) {
      return NextResponse.json({ error: 'Project not found' }, { status: 404 });
    }
    
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('Delete project error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getProject);
export const PUT = requireAdmin(updateProject);
export const DELETE = requireAdmin(deleteProject);




