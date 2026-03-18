import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const audioFile = formData.get('audio')

    if (!audioFile) {
      return NextResponse.json(
        { error: 'No audio file provided' },
        { status: 400 }
      )
    }

    // Forward audio to backend for transcription
    const backendFormData = new FormData()
    backendFormData.append('audio', audioFile)

    const response = await fetch(`${BACKEND_URL}/transcribe`, {
      method: 'POST',
      body: backendFormData,
    })

    if (!response.ok) {
      // If backend doesn't support transcription, try Web Speech API fallback on client
      return NextResponse.json(
        { error: 'Transcription service unavailable' },
        { status: 503 }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Transcription error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

