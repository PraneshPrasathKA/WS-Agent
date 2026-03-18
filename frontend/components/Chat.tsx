'use client'

import React, { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import AudioRecorder from './AudioRecorder'
import { Send, Loader2, Volume2, VolumeX } from 'lucide-react'

interface Message {
  text: string
  isUser: boolean
}

interface ChatProps {
  onAssetShow: (assetType: string | null) => void
}

export default function Chat({ onAssetShow }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      text: "Hi! I'm WS AI. How can I help you today?",
      isUser: false,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [speechEnabled, setSpeechEnabled] = useState(true)
  const [pendingBooking, setPendingBooking] = useState<{ slot?: string, action: 'book' | 'waitlist' } | null>(null)
  const [availableSlots, setAvailableSlots] = useState<any[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const speechSynthRef = useRef<SpeechSynthesis | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Initialize speech synthesis
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      speechSynthRef.current = window.speechSynthesis

      // Speak the initial greeting after a short delay
      if (speechEnabled && messages.length === 1 && !messages[0].isUser) {
        setTimeout(() => {
          speakText(messages[0].text)
        }, 500)
      }
    }
    return () => {
      // Cancel any ongoing speech when component unmounts
      if (speechSynthRef.current) {
        speechSynthRef.current.cancel()
      }
    }
  }, [])

  const filterTags = (text: string) => {
    if (!text) return text
    // Failsafe: Strip any <function=...>, <tool_call=...>, or <section_id=...> tags
    // Matches opening tags, content until closing tags, or just standalone tags
    return text.replace(/<(?:function|tool_call|section_id)=[\s\S]*?(?:<\/(?:function|tool_call|section_id)>|$)/gi, '')
               .replace(/<\/?(?:function|tool_call|section_id)(?:=[^>]+)?>/gi, '')
               .replace(/^\s*(?:Action|Thought|Observation|AI):[\s\S]*?(?:\n|$)/gim, '')
               .trim()
  }

  const speakText = (text: string) => {
    if (!speechEnabled || !window.speechSynthesis) return

    // Clean text for speech too
    const cleanText = filterTags(text)
    if (!cleanText) return

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    // Create and speak the text
    const utterance = new SpeechSynthesisUtterance(cleanText)

    // Force English voice if available to avoid loading issues in some browsers
    const voices = window.speechSynthesis.getVoices()
    if (voices.length > 0) {
      const englishVoice = voices.find((v) => v.lang.startsWith('en'))
      if (englishVoice) {
        utterance.voice = englishVoice
      }
    }

    utterance.rate = 1.0 // Normal speed
    utterance.pitch = 1.0 // Normal pitch
    utterance.volume = 1.0 // Full volume
    utterance.lang = 'en-US'

    utterance.onerror = (error) => {
      console.error('Speech synthesis error:', error)
    }

    window.speechSynthesis.speak(utterance)
  }

  const toggleSpeech = () => {
    const newState = !speechEnabled
    setSpeechEnabled(newState)
    if (!newState && speechSynthRef.current) {
      // If disabling, stop current speech
      speechSynthRef.current.cancel()
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    // Stop agent speaking when user sends a new message
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }

    const userMessage = input.trim()

    // All messages go through chat API - agent handles booking
    // Check if user is selecting/confirming a slot time - set pending booking
    const messageLower = userMessage.toLowerCase()
    const slotTimeMatch = userMessage.match(/(\d{1,2}):?(\d{2})?\s*(am|pm)/i)
    const isConfirmation = messageLower.match(/(yes|yeah|ok|sure|book|confirm|that works|i'll take|i like|works|good|fine|perfect|walk|would)/i)

    // If user mentions a time or confirms, match to available slots
    if ((slotTimeMatch || isConfirmation) && availableSlots.length > 0) {
      let matchedSlot = availableSlots[0] // Default to first

      if (slotTimeMatch) {
        const hour = parseInt(slotTimeMatch[1])
        const minute = slotTimeMatch[2] ? parseInt(slotTimeMatch[2]) : 0
        const period = slotTimeMatch[3].toLowerCase()

        for (const slot of availableSlots) {
          const slotTimeStr = slot.ist.toLowerCase()
          const slotMatch = slotTimeStr.match(/(\d{1,2}):?(\d{2})?\s*(am|pm)/i)
          if (slotMatch) {
            const slotHour = parseInt(slotMatch[1])
            const slotMinute = slotMatch[2] ? parseInt(slotMatch[2]) : 0
            const slotPeriod = slotMatch[3].toLowerCase()

            // Normalize to 24-hour for comparison
            const userHour24 = period === 'pm' && hour !== 12 ? hour + 12 : (period === 'am' && hour === 12 ? 0 : hour)
            const slotHour24 = slotPeriod === 'pm' && slotHour !== 12 ? slotHour + 12 : (slotPeriod === 'am' && slotHour === 12 ? 0 : slotHour)

            if (slotHour24 === userHour24 && slotMinute === minute) {
              matchedSlot = slot
              break
            }
          }
        }
      }

      // Set pending booking so agent knows to ask for email/name
      if (matchedSlot && matchedSlot.utc) {
        setPendingBooking({
          action: 'book',
          slot: matchedSlot.utc
        })
        console.log('✅ Slot confirmed, pending booking set:', matchedSlot.utc)
      }
    }

    setInput('')
    setMessages((prev) => [...prev, { text: userMessage, isUser: true }])
    setLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || `Server error: ${response.status}`)
      }

      const data = await response.json()

      // Update session ID if provided
      if (data.session_id) {
        setSessionId(data.session_id)
      }

      // Store available slots if provided
      if (data.availableSlots && Array.isArray(data.availableSlots)) {
        console.log('✅ Received available slots from backend:', data.availableSlots)
        setAvailableSlots(data.availableSlots)
      } else {
        console.log('ℹ️ No slots in this response')
      }

      // Add agent response
      setMessages((prev) => [
        ...prev,
        { text: filterTags(data.reply), isUser: false },
      ])

      // If stage is BOOKING and we don't have pending booking yet, set it
      if (data.stage === 'BOOKING' && !pendingBooking && availableSlots.length > 0) {
        // Use first available slot as default
        setPendingBooking({
          action: 'book',
          slot: availableSlots[0]?.utc
        })
        console.log('✅ Stage is BOOKING, set pending booking')
      }

      // Speak the agent's response
      if (data.reply && speechEnabled) {
        setTimeout(() => {
          speakText(data.reply)
        }, 100)
      }

      // Trigger asset display if needed
      if (data.showAsset) {
        onAssetShow(data.showAsset)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setMessages((prev) => [
        ...prev,
        {
          text: `Sorry, I encountered an error: ${errorMessage}. Please check your backend connection and try again.`,
          isUser: false,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }



  const handleTranscript = (transcript: string, isFinal: boolean) => {
    if (transcript.trim()) {
      // Stop agent speaking when user starts talking (voice input)
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
      
      setInput(transcript)

      if (isFinal) {
        // Small delay to ensure input is set, then send
        setTimeout(() => {
          const userMessage = transcript.trim()
          setInput('')
          setMessages((prev) => [...prev, { text: userMessage, isUser: true }])
          setLoading(true)

          // Send the transcript as a message
          fetch('/api/chat', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: userMessage,
              session_id: sessionId,
            }),
          })
            .then(response => {
              if (!response.ok) {
                return response.json().then(err => { throw new Error(err.detail || 'Failed to get response') })
              }
              return response.json()
            })
            .then(data => {
              if (data.session_id) {
                setSessionId(data.session_id)
              }
              setMessages((prev) => [
                ...prev,
                { text: filterTags(data.reply), isUser: false },
              ])

              // Store available slots if provided
              if (data.availableSlots && Array.isArray(data.availableSlots)) {
                console.log('✅ Received available slots (voice):', data.availableSlots)
                setAvailableSlots(data.availableSlots)
              }

              // Speak the agent's response
              if (data.reply && speechEnabled) {
                setTimeout(() => {
                  speakText(data.reply)
                }, 100)
              }

              if (data.showAsset) {
                onAssetShow(data.showAsset)
              }
            })
            .catch(error => {
              console.error('Error sending message:', error)
              setMessages((prev) => [
                ...prev,
                {
                  text: `Sorry, I encountered an error: ${error.message}. Please try again.`,
                  isUser: false,
                },
              ])
            })
            .finally(() => {
              setLoading(false)
            })
        }, 100)
      }
    }
  }

    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg.text} isUser={msg.isUser} />
          ))}
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-200 dark:bg-gray-800 rounded-lg px-4 py-2">
                <Loader2 className="w-5 h-5 animate-spin text-gray-600 dark:text-gray-400" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex gap-2 items-center mb-2">
            <button
              onClick={toggleSpeech}
              className={`p-2 rounded-lg transition-colors ${speechEnabled
                  ? 'bg-blue-100 hover:bg-blue-200 dark:bg-blue-900 dark:hover:bg-blue-800 text-blue-600 dark:text-blue-300'
                  : 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-500 dark:text-gray-400'
                }`}
              title={speechEnabled ? 'Disable agent speech' : 'Enable agent speech'}
            >
              {speechEnabled ? (
                <Volume2 className="w-4 h-4" />
              ) : (
                <VolumeX className="w-4 h-4" />
              )}
            </button>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {speechEnabled ? 'Agent will speak responses' : 'Agent speech disabled'}
            </span>
          </div>
          <div className="flex gap-2">
            <AudioRecorder onTranscript={handleTranscript} disabled={loading} />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message or use mic..."
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

      </div>
    )
  }
