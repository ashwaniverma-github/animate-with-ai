// web/src/app/api/status/[id]/route.ts
import { NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { supabase } from '@/lib/supabase'

export async function GET(
  req: Request,
  context: { params: Promise<{ id: string }> }
) {
  const { id } = await context.params
  const jobId = parseInt(id, 10)
  if (Number.isNaN(jobId)) {
    return NextResponse.json({ error: 'Invalid id' }, { status: 400 })
  }

  const job = await db.job.findUnique({ where: { id: jobId } })
  if (!job) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }
  if (job.status !== 'completed' || !job.storagePath) {
    return NextResponse.json({ status: job.status })
  }

  // 1) Try signed URL (for private buckets)
  let videoUrl: string | null = null
  const signed = await supabase
    .storage
    .from('videos')
    .createSignedUrl(job.storagePath, 60 * 60)

  if (!signed.error && signed.data?.signedUrl) {
    videoUrl = signed.data.signedUrl
  } else {
    console.warn('Signed URL failed:', signed.error)

    // 2) Fallback to public URL (if bucket/object is public)
    const pub = supabase
      .storage
      .from('videos')
      .getPublicUrl(job.storagePath)

    if (pub.data?.publicUrl) {
      videoUrl = pub.data.publicUrl
    } else {
      console.error('Public URL failed:', signed.error)
    }
  }

  if (!videoUrl) {
    return NextResponse.json(
      { error: 'Video not found in storage' },
      { status: 404 }
    )
  }

  return NextResponse.json({
    status: 'completed',
    videoUrl,
  })
}
