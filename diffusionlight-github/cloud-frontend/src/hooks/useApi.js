import { useState, useEffect, useCallback } from 'react'
import config from '../config/api'

const API_BASE_URL = config.API_BASE_URL

export const useApi = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const apiCall = useCallback(async (endpoint, options = {}) => {
    setLoading(true)
    setError(null)

    try {
      const url = `${API_BASE_URL}${endpoint}`
      const requestConfig = {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      }

      // Remove Content-Type for FormData
      if (options.body instanceof FormData) {
        delete requestConfig.headers['Content-Type']
      }

      if (config.ENABLE_DEBUG) {
        console.log('🌐 API Request:', { url, config: requestConfig })
      }

      const response = await fetch(url, requestConfig)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP ${response.status}`)
      }

      const data = await response.json()
      
      if (config.ENABLE_DEBUG) {
        console.log('✅ API Response:', data)
      }
      
      return data
    } catch (err) {
      const errorMessage = err.message
      setError(errorMessage)
      
      if (config.ENABLE_ERROR_REPORTING && config.SENTRY_DSN) {
        // Report error to Sentry if configured
        console.error('API Error:', err)
      }
      
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { apiCall, loading, error, setError }
}

export const useFileUpload = () => {
  const { apiCall, loading, error } = useApi()

  const uploadFile = useCallback(async (file) => {
    // Validate file size
    if (file.size > config.MAX_FILE_SIZE) {
      throw new Error(`File too large. Maximum size: ${config.MAX_FILE_SIZE / 1024 / 1024}MB`)
    }

    // Validate file type
    const fileExtension = file.name.split('.').pop().toLowerCase()
    if (!config.ALLOWED_FILE_TYPES.includes(fileExtension)) {
      throw new Error(`Invalid file type. Allowed: ${config.ALLOWED_FILE_TYPES.join(', ')}`)
    }

    const formData = new FormData()
    formData.append('file', file)

    return await apiCall('/files/upload', {
      method: 'POST',
      body: formData,
    })
  }, [apiCall])

  return { uploadFile, loading, error }
}

export const useJobs = () => {
  const { apiCall, loading, error } = useApi()

  const createJob = useCallback(async (fileId, configuration = {}, name = '') => {
    return await apiCall('/jobs', {
      method: 'POST',
      body: JSON.stringify({
        file_id: fileId,
        configuration,
        name,
      }),
    })
  }, [apiCall])

  const getJob = useCallback(async (jobId) => {
    return await apiCall(`/jobs/${jobId}`)
  }, [apiCall])

  const listJobs = useCallback(async (limit = 50) => {
    return await apiCall(`/jobs?limit=${limit}`)
  }, [apiCall])

  const cancelJob = useCallback(async (jobId) => {
    return await apiCall(`/jobs/${jobId}/cancel`, {
      method: 'POST',
    })
  }, [apiCall])

  const getJobResults = useCallback(async (jobId) => {
    return await apiCall(`/jobs/${jobId}/results`)
  }, [apiCall])

  return {
    createJob,
    getJob,
    listJobs,
    cancelJob,
    getJobResults,
    loading,
    error,
  }
}

export const useStatistics = () => {
  const { apiCall, loading, error } = useApi()

  const getStatistics = useCallback(async () => {
    return await apiCall('/statistics')
  }, [apiCall])

  return { getStatistics, loading, error }
}

export const usePolling = (callback, interval = 2000, enabled = true) => {
  useEffect(() => {
    if (!enabled) return

    const poll = async () => {
      try {
        await callback()
      } catch (error) {
        if (config.ENABLE_DEBUG) {
          console.error('Polling error:', error)
        }
      }
    }

    // Execute immediately
    poll()

    // Set up interval
    const intervalId = setInterval(poll, interval)

    return () => clearInterval(intervalId)
  }, [callback, interval, enabled])
}

