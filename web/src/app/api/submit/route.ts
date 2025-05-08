import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'
import { db } from '@/lib/db'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req:NextRequest) {
  const { prompt } = await req.json()
  if (!prompt) return NextResponse.json({msg:"Prompt is empty"} , {status:402})

  // 1) Create job
  const job = await db.job.create({ data: { prompt, status: 'pending' } })

  // 2) Enqueue via Python service
  console.log("Wroker " + process.env.WORKER_URL)
  await axios.post(`${process.env.WORKER_URL}/enqueue`, { jobId: job.id, prompt })

  return  NextResponse.json({jobId:job.id} , {status:201})
}