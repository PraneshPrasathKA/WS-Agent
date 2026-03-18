import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { slot, email, name, session_id } = body

    if (!slot || !email) {
      return NextResponse.json(
        { error: 'Slot and email are required' },
        { status: 400 }
      )
    }

    const response = await fetch(`${BACKEND_URL}/book-meeting`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        slot,
        email,
        name,
        session_id,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(
        { success: false, error: error.error || 'Failed to book meeting' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Book meeting API error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

