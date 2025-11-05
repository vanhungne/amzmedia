import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/middleware';
import { getDb } from '@/lib/db';
import sql from 'mssql';
import { v4 as uuidv4 } from 'uuid';

// GET all projects
async function getProjects(req: NextRequest) {
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
        p.[updated_at],
        u.[username] as created_by_username
      FROM [dbo].[projects] p
      LEFT JOIN [dbo].[users] u ON p.[created_by] = u.[id]
      ORDER BY p.[created_at] DESC
    `);
    
    return NextResponse.json({ projects: result.recordset });
  } catch (error: any) {
    console.error('Get projects error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// POST create new project
async function createProject(req: NextRequest) {
  try {
    const body = await req.json();
    const { channel_name, script_template, num_prompts, voice_id, auto_workflow, video_output_folder } = body;
    const userId = (req as any).user.userId;
    
    if (!channel_name) {
      return NextResponse.json(
        { error: 'Channel name is required' },
        { status: 400 }
      );
    }
    
    const db = await getDb();
    const projectId = uuidv4();
    
    const result = await db.request()
      .input('project_id', sql.NVarChar(50), projectId)
      .input('channel_name', sql.NVarChar(255), channel_name)
      .input('script_template', sql.NVarChar(sql.MAX), script_template || null)
      .input('num_prompts', sql.Int, num_prompts || 12)
      .input('voice_id', sql.NVarChar(100), voice_id || null)
      .input('auto_workflow', sql.Bit, auto_workflow !== false)
      .input('video_output_folder', sql.NVarChar(500), video_output_folder || null)
      .input('created_by', sql.Int, userId)
      .query(`
        INSERT INTO [dbo].[projects] 
        ([project_id], [channel_name], [script_template], [num_prompts], [voice_id], [auto_workflow], [video_output_folder], [created_by])
        OUTPUT INSERTED.id, INSERTED.project_id, INSERTED.channel_name, INSERTED.script_template, 
               INSERTED.num_prompts, INSERTED.voice_id, INSERTED.auto_workflow, INSERTED.video_output_folder, INSERTED.created_at
        VALUES (@project_id, @channel_name, @script_template, @num_prompts, @voice_id, @auto_workflow, @video_output_folder, @created_by)
      `);
    
    return NextResponse.json({ project: result.recordset[0] }, { status: 201 });
  } catch (error: any) {
    console.error('Create project error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const GET = requireAdmin(getProjects);
export const POST = requireAdmin(createProject);




