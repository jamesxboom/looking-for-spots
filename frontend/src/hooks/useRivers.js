import { useState, useEffect, useCallback, useRef } from 'react'
import { fetchRivers, fetchRiverDetail, fetchRiverHistory } from '../lib/api'

export const useRivers = () => {
  const [rivers, setRivers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const intervalRef = useRef(null)

  const loadRivers = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchRivers()
      setRivers(Array.isArray(data) ? data : data.rivers || [])
      setLastUpdated(new Date())
    } catch (err) {
      setError(err.message || 'Failed to fetch river data')
      console.error('Error loading rivers:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  // Load on mount
  useEffect(() => {
    loadRivers()
  }, [loadRivers])

  // Set up interval for refreshing every 5 minutes
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      loadRivers()
    }, 5 * 60 * 1000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [loadRivers])

  return {
    rivers,
    loading,
    error,
    lastUpdated,
    refetch: loadRivers,
  }
}

export const useRiverDetail = (riverId) => {
  const [river, setRiver] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!riverId) return

    const loadDetail = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchRiverDetail(riverId)
        setRiver(data)
      } catch (err) {
        setError(err.message || 'Failed to fetch river detail')
        console.error(`Error loading river ${riverId}:`, err)
      } finally {
        setLoading(false)
      }
    }

    loadDetail()
  }, [riverId])

  return { river, loading, error }
}

export const useRiverHistory = (riverId, days = 7) => {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!riverId) return

    const loadHistory = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchRiverHistory(riverId, days)
        setHistory(data.readings || [])
      } catch (err) {
        setError(err.message || 'Failed to fetch river history')
        console.error(`Error loading history for river ${riverId}:`, err)
      } finally {
        setLoading(false)
      }
    }

    loadHistory()
  }, [riverId, days])

  return { history, loading, error }
}
