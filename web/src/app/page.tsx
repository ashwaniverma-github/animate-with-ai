'use client'
import { useState } from 'react'
import axios from 'axios'

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [jobId, setJobId] = useState<number|null>(null)
  const [status, setStatus] = useState('')
  const [videoUrl, setVideoUrl] = useState('')

  const submit = async () => {
    const res = await axios.post('/api/submit', { prompt })
    setJobId(res.data.jobId)
    setStatus('pending')
    setVideoUrl('')
  }

  const checkStatus = async () => {
    if (!jobId) return
    const res = await axios.get(`/api/status/${jobId}`)
    setStatus(res.data.status)
    if (res.data.videoUrl) {
      setVideoUrl(res.data.videoUrl)
    }
  }

  return (
    <div className="p-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Animate with AI</h1>
      <textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Enter your prompt…"
        className="w-full h-24 p-2 border rounded"
      />
      <button 
        onClick={submit}
        className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Submit
      </button>

      {jobId && (
        <div className="mt-6">
          <p className="mb-2">Status: <strong>{status}</strong></p>
          {status !== 'completed' && (
            <button 
              onClick={checkStatus}
              className="px-3 py-1 bg-gray-500 rounded"
            >
              Check
            </button>
          )}
          {videoUrl && (
            <div className="mt-4">
              <video 
                src={videoUrl} 
                controls 
                className="w-full rounded shadow"
              />
              <a
                href={videoUrl}
                download={`animation-${jobId}.mp4`}
                className="mt-2 inline-block text-blue-600 underline"
              >
                ⬇️ Download Video
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
