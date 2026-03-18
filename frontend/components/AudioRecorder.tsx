'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Mic, Square } from 'lucide-react'

interface AudioRecorderProps {
  onTranscript: (transcript: string, isFinal: boolean) => void
  disabled?: boolean
}

export default function AudioRecorder({ onTranscript, disabled }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    // Check if browser supports Web Speech API
    if (typeof window !== 'undefined') {
      const supported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
      setIsSupported(supported)
    }
  }, [])

  const startRecording = () => {
    // Use Web Speech API directly for simpler implementation
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      const recognition = new SpeechRecognition()
      recognitionRef.current = recognition
      
      recognition.continuous = false
      recognition.interimResults = true
      recognition.lang = 'en-US'
      
      recognition.onstart = () => {
        setIsRecording(true)
      }
      
      recognition.onresult = (event: any) => {
        let interimTranscript = ''
        let finalTranscript = ''
        
        // Loop through all results from the start of the current session
        for (let i = 0; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript
          } else {
            interimTranscript += event.results[i][0].transcript
          }
        }
        
        // Combine them to show the full text spoken so far during this mic session
        if (finalTranscript || interimTranscript) {
          const combined = (finalTranscript + ' ' + interimTranscript).trim()
          
          // Only auto-send if there's no interim left and it's final
          if (finalTranscript && !interimTranscript) {
             onTranscript(finalTranscript, true)
          } else {
             onTranscript(combined, false)
          }
        }
      }
      
      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsRecording(false)
        recognitionRef.current = null
        if (event.error === 'not-allowed') {
          alert('Microphone permission denied. Please allow microphone access and try again.')
        } else if (event.error === 'network') {
          alert('Network error occurred during speech recognition. Please check your connection.')
        } else if (event.error !== 'aborted' && event.error !== 'no-speech') {
          console.warn('Speech recognition failed silently:', event.error)
        }
      }
      
      recognition.onend = () => {
        setIsRecording(false)
        recognitionRef.current = null
      }
      
      try {
        recognition.start()
      } catch (error) {
        console.error('Error starting speech recognition:', error)
        alert('Could not start speech recognition. Please check your browser settings.')
        setIsRecording(false)
        recognitionRef.current = null
      }
    } else {
      alert('Speech recognition is not supported in your browser. Please use a modern browser like Chrome or Edge.')
    }
  }

  const stopRecording = () => {
    // Stop Web Speech API recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (error) {
        console.error('Error stopping recognition:', error)
      }
      recognitionRef.current = null
    }
    setIsRecording(false)
  }

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  // Show button even if not supported, with a message
  if (!isSupported) {
    return (
      <button
        disabled
        className="p-3 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed"
        title="Voice input not supported in this browser. Please use Chrome or Edge."
      >
        <Mic className="w-5 h-5" />
      </button>
    )
  }

  return (
    <button
      onClick={toggleRecording}
      disabled={disabled}
      className={`p-3 rounded-lg transition-colors ${
        isRecording
          ? 'bg-red-600 hover:bg-red-700 text-white'
          : 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
      title={isRecording ? 'Stop recording' : 'Start voice recording'}
    >
      {isRecording ? (
        <Square className="w-5 h-5" />
      ) : (
        <Mic className="w-5 h-5" />
      )}
    </button>
  )
}

