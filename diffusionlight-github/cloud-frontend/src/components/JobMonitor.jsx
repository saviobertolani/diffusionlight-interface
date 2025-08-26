import { useState, useEffect, useCallback } from 'react'
import { Clock, CheckCircle, AlertCircle, X, Download, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { useJobs, usePolling } from '../hooks/useApi'

const JobMonitor = ({ jobId, onComplete, onError, onCancel }) => {
  const [job, setJob] = useState(null)
  const [results, setResults] = useState(null)
  const { getJob, cancelJob, getJobResults } = useJobs()

  const fetchJobStatus = useCallback(async () => {
    if (!jobId) return

    try {
      const jobData = await getJob(jobId)
      setJob(jobData)

      if (jobData.status === 'completed') {
        try {
          const resultsData = await getJobResults(jobId)
          setResults(resultsData)
          onComplete?.(jobData, resultsData)
        } catch (error) {
          console.error('Error fetching results:', error)
        }
      } else if (jobData.status === 'failed') {
        onError?.(jobData.error_message || 'Erro no processamento')
      }
    } catch (error) {
      console.error('Error fetching job:', error)
      onError?.(error.message)
    }
  }, [jobId, getJob, getJobResults, onComplete, onError])

  // Poll job status every 2 seconds if job is not completed
  const shouldPoll = job && ['pending', 'processing'].includes(job.status)
  usePolling(fetchJobStatus, 2000, shouldPoll)

  // Initial fetch
  useEffect(() => {
    if (jobId) {
      fetchJobStatus()
    }
  }, [jobId, fetchJobStatus])

  const handleCancel = async () => {
    if (!job || !['pending', 'processing'].includes(job.status)) return

    try {
      await cancelJob(job.id)
      await fetchJobStatus() // Refresh status
      onCancel?.(job)
    } catch (error) {
      console.error('Error canceling job:', error)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'processing':
        return <Clock className="h-5 w-5 text-blue-500 animate-spin" />
      case 'pending':
        return <Clock className="h-5 w-5 text-gray-400" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'cancelled':
        return <X className="h-5 w-5 text-gray-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-blue-100 text-blue-800'
      case 'pending':
        return 'bg-gray-100 text-gray-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-600'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Concluído'
      case 'processing':
        return 'Processando'
      case 'pending':
        return 'Pendente'
      case 'failed':
        return 'Falhou'
      case 'cancelled':
        return 'Cancelado'
      default:
        return 'Desconhecido'
    }
  }

  const formatProcessingTime = (seconds) => {
    if (!seconds) return 'N/A'
    
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    }
    return `${remainingSeconds}s`
  }

  const downloadFile = (fileUrl, filename) => {
    const link = document.createElement('a')
    link.href = `http://localhost:5000${fileUrl}`
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  if (!job) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span className="ml-2">Carregando status do job...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {getStatusIcon(job.status)}
              <span>{job.name || 'Processamento HDRI'}</span>
            </div>
            <Badge className={getStatusColor(job.status)}>
              {getStatusText(job.status)}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          {['pending', 'processing'].includes(job.status) && (
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Progresso</span>
                <span>{job.progress || 0}%</span>
              </div>
              <Progress value={job.progress || 0} className="h-3" />
            </div>
          )}

          {/* Job Info */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Arquivo:</span>
              <p className="text-gray-600">{job.input_file_name}</p>
            </div>
            <div>
              <span className="font-medium">Criado em:</span>
              <p className="text-gray-600">
                {new Date(job.created_at).toLocaleString('pt-BR')}
              </p>
            </div>
            {job.started_at && (
              <div>
                <span className="font-medium">Iniciado em:</span>
                <p className="text-gray-600">
                  {new Date(job.started_at).toLocaleString('pt-BR')}
                </p>
              </div>
            )}
            {job.completed_at && (
              <div>
                <span className="font-medium">Concluído em:</span>
                <p className="text-gray-600">
                  {new Date(job.completed_at).toLocaleString('pt-BR')}
                </p>
              </div>
            )}
            {job.processing_time && (
              <div>
                <span className="font-medium">Tempo de processamento:</span>
                <p className="text-gray-600">
                  {formatProcessingTime(job.processing_time)}
                </p>
              </div>
            )}
          </div>

          {/* Configuration */}
          {job.configuration && Object.keys(job.configuration).length > 0 && (
            <div>
              <span className="font-medium text-sm">Configuração:</span>
              <div className="mt-1 text-sm text-gray-600 space-y-1">
                {job.configuration.resolution && (
                  <p>Resolução: {job.configuration.resolution}x{job.configuration.resolution/2}</p>
                )}
                {job.configuration.output_format && (
                  <p>Formato: {job.configuration.output_format.toUpperCase()}</p>
                )}
                {job.configuration.anti_aliasing && (
                  <p>Anti-aliasing: {job.configuration.anti_aliasing}x</p>
                )}
              </div>
            </div>
          )}

          {/* Error Message */}
          {job.status === 'failed' && job.error_message && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span className="font-medium text-red-800">Erro:</span>
              </div>
              <p className="text-red-700 text-sm mt-1">{job.error_message}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-between">
            <div>
              {['pending', 'processing'].includes(job.status) && (
                <Button variant="destructive" onClick={handleCancel}>
                  <X className="h-4 w-4 mr-1" />
                  Cancelar
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Card */}
      {job.status === 'completed' && results && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>Resultados</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Files */}
            <div>
              <h4 className="font-medium mb-3">Arquivos gerados:</h4>
              <div className="space-y-2">
                {results.files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Eye className="h-4 w-4 text-blue-600" />
                        </div>
                      </div>
                      <div>
                        <p className="font-medium">{file.filename}</p>
                        {file.size && (
                          <p className="text-sm text-gray-500">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        )}
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => downloadFile(file.download_url, file.filename)}
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Metadata */}
            {results.metadata && (
              <div>
                <h4 className="font-medium mb-3">Informações técnicas:</h4>
                <div className="bg-gray-50 rounded-lg p-3 text-sm space-y-1">
                  {results.metadata.processing_time && (
                    <p><strong>Tempo de processamento:</strong> {results.metadata.processing_time}</p>
                  )}
                  {results.metadata.configuration && (
                    <div>
                      <strong>Configuração utilizada:</strong>
                      <pre className="mt-1 text-xs bg-white p-2 rounded border overflow-x-auto">
                        {JSON.stringify(results.metadata.configuration, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default JobMonitor

