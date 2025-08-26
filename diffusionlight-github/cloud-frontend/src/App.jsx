import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Upload, Image, Download, Eye, Settings, Clock, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react'
import FileUploader from './components/FileUploader'
import JobMonitor from './components/JobMonitor'
import { useJobs, useStatistics } from './hooks/useApi'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('dashboard')
  const [uploadedFile, setUploadedFile] = useState(null)
  const [currentJob, setCurrentJob] = useState(null)
  const [jobs, setJobs] = useState([])
  const [statistics, setStatistics] = useState(null)
  const [configuration, setConfiguration] = useState({
    resolution: 1024,
    output_format: 'hdr',
    anti_aliasing: '4',
    preset: 'automotivo'
  })
  const [error, setError] = useState(null)

  const { createJob, listJobs } = useJobs()
  const { getStatistics } = useStatistics()

  // Carregar dados iniciais
  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [jobsData, statsData] = await Promise.all([
        listJobs(10),
        getStatistics()
      ])
      setJobs(jobsData)
      setStatistics(statsData)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    }
  }

  const handleFileUpload = (fileData) => {
    setUploadedFile(fileData)
    setCurrentView('configure')
    setError(null)
  }

  const handleUploadError = (errorMessage) => {
    setError(errorMessage)
  }

  const handleStartProcessing = async () => {
    if (!uploadedFile) return

    try {
      const jobName = `HDRI - ${uploadedFile.filename}`
      const jobData = await createJob(uploadedFile.file_id, configuration, jobName)
      
      setCurrentJob(jobData.job_id)
      setCurrentView('processing')
      setError(null)
    } catch (error) {
      setError(error.message)
    }
  }

  const handleJobComplete = (job, results) => {
    setCurrentView('results')
    loadDashboardData() // Refresh dashboard data
  }

  const handleJobError = (errorMessage) => {
    setError(errorMessage)
  }

  const handleJobCancel = () => {
    setCurrentView('dashboard')
    setCurrentJob(null)
    setUploadedFile(null)
    loadDashboardData()
  }

  const handleBackToDashboard = () => {
    setCurrentView('dashboard')
    setCurrentJob(null)
    setUploadedFile(null)
    setError(null)
    loadDashboardData()
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'processing':
        return <Clock className="h-4 w-4 text-blue-500 animate-spin" />
      case 'pending':
        return <Clock className="h-4 w-4 text-gray-400" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
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
      default:
        return 'Desconhecido'
    }
  }

  const renderDashboard = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-gray-900">DiffusionLight</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Configurações
              </Button>
              <div className="h-8 w-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">SB</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">HDRIs Gerados</CardTitle>
              <Image className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.jobs?.completed || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Total de jobs concluídos
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Em Processamento</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.jobs?.processing || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Tempo médio: {statistics?.jobs?.avg_processing_time || 0}s
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Taxa de Sucesso</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.jobs?.success_rate || 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                Últimos jobs processados
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Action */}
        <div className="text-center mb-8">
          <Button 
            size="lg" 
            className="h-12 px-8"
            onClick={() => setCurrentView('upload')}
          >
            <Upload className="h-5 w-5 mr-2" />
            Criar Novo HDRI
          </Button>
        </div>

        {/* Recent Jobs */}
        <Card>
          <CardHeader>
            <CardTitle>Jobs Recentes</CardTitle>
            <CardDescription>Acompanhe o status dos seus processamentos</CardDescription>
          </CardHeader>
          <CardContent>
            {jobs.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Image className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Nenhum job encontrado</p>
                <p className="text-sm">Crie seu primeiro HDRI clicando no botão acima</p>
              </div>
            ) : (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(job.status)}
                      <div>
                        <h4 className="font-medium">{job.name}</h4>
                        <p className="text-sm text-gray-500">
                          {new Date(job.created_at).toLocaleString('pt-BR')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <Badge className={getStatusColor(job.status)}>
                        {getStatusText(job.status)}
                      </Badge>
                      {job.status === 'processing' && (
                        <div className="w-24">
                          <Progress value={job.progress || 0} className="h-2" />
                        </div>
                      )}
                      <span className="text-sm text-gray-500 min-w-[80px]">
                        {job.processing_time ? `${job.processing_time.toFixed(1)}s` : '-'}
                      </span>
                      {job.status === 'completed' && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => {
                            setCurrentJob(job.id)
                            setCurrentView('results')
                          }}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Ver Resultados
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderUpload = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Button variant="ghost" onClick={handleBackToDashboard}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Voltar
              </Button>
              <h1 className="text-xl font-semibold text-gray-900 ml-4">Upload de Imagem</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Selecione uma Imagem</CardTitle>
            <CardDescription>
              Faça upload de uma imagem para gerar o HDRI. Formatos suportados: JPG, PNG, TIFF
            </CardDescription>
          </CardHeader>
          <CardContent>
            <FileUploader 
              onUploadSuccess={handleFileUpload}
              onUploadError={handleUploadError}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )

  const renderConfigure = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Button variant="ghost" onClick={() => setCurrentView('upload')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Voltar
              </Button>
              <h1 className="text-xl font-semibold text-gray-900 ml-4">Configurar Processamento</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Preview */}
          <Card>
            <CardHeader>
              <CardTitle>Preview da Imagem</CardTitle>
            </CardHeader>
            <CardContent>
              {uploadedFile && (
                <div className="space-y-4">
                  <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                    <img 
                      src={`data:image/jpeg;base64,${uploadedFile.preview}`} 
                      alt="Preview" 
                      className="max-w-full max-h-full object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextSibling.style.display = 'flex'
                      }}
                    />
                    <div className="hidden items-center justify-center w-full h-full text-gray-500">
                      <div className="text-center">
                        <Image className="h-12 w-12 mx-auto mb-2" />
                        <p>Preview não disponível</p>
                      </div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><strong>Nome:</strong> {uploadedFile.filename}</p>
                    <p><strong>Tamanho:</strong> {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                    {uploadedFile.width && uploadedFile.height && (
                      <p><strong>Resolução:</strong> {uploadedFile.width} × {uploadedFile.height}</p>
                    )}
                    {uploadedFile.format && (
                      <p><strong>Formato:</strong> {uploadedFile.format}</p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Configurações</CardTitle>
              <CardDescription>Escolha as configurações para o processamento</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Presets */}
              <div>
                <h4 className="font-medium mb-3">Presets</h4>
                <div className="grid grid-cols-1 gap-3">
                  {[
                    { id: 'automotivo', name: 'Automotivo', desc: 'Otimizado para cenas automotivas' },
                    { id: 'produto', name: 'Produto', desc: 'Ideal para fotografia de produto' },
                    { id: 'arquitetonico', name: 'Arquitetônico', desc: 'Para ambientes e arquitetura' }
                  ].map((preset) => (
                    <Button 
                      key={preset.id}
                      variant={configuration.preset === preset.id ? "default" : "outline"} 
                      className="justify-start h-auto p-4"
                      onClick={() => setConfiguration(prev => ({ ...prev, preset: preset.id }))}
                    >
                      <div className="text-left">
                        <div className="font-medium">{preset.name}</div>
                        <div className="text-sm opacity-70">{preset.desc}</div>
                      </div>
                    </Button>
                  ))}
                </div>
              </div>

              {/* Advanced Settings */}
              <div>
                <h4 className="font-medium mb-3">Configurações Avançadas</h4>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium block mb-2">Resolução de Saída</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={configuration.resolution}
                      onChange={(e) => setConfiguration(prev => ({ ...prev, resolution: parseInt(e.target.value) }))}
                    >
                      <option value={512}>512x256 (Rápido)</option>
                      <option value={1024}>1024x512 (Padrão)</option>
                      <option value={2048}>2048x1024 (Alta Qualidade)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-2">Formato de Saída</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={configuration.output_format}
                      onChange={(e) => setConfiguration(prev => ({ ...prev, output_format: e.target.value }))}
                    >
                      <option value="hdr">HDR (.hdr)</option>
                      <option value="exr">OpenEXR (.exr)</option>
                      <option value="npy">NumPy (.npy)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-2">Anti-aliasing</label>
                    <select 
                      className="w-full p-2 border rounded-md"
                      value={configuration.anti_aliasing}
                      onChange={(e) => setConfiguration(prev => ({ ...prev, anti_aliasing: e.target.value }))}
                    >
                      <option value="1">1x</option>
                      <option value="2">2x</option>
                      <option value="4">4x</option>
                      <option value="8">8x</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Estimate */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Estimativa de Processamento</h4>
                <p className="text-blue-700">
                  Tempo estimado: {configuration.resolution === 512 ? '2-3' : configuration.resolution === 1024 ? '3-5' : '5-8'} minutos
                </p>
                <p className="text-sm text-blue-600">Baseado na resolução e configurações selecionadas</p>
              </div>

              {/* Action Button */}
              <Button 
                className="w-full h-12"
                onClick={handleStartProcessing}
                disabled={!uploadedFile}
              >
                Iniciar Processamento
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )

  const renderProcessing = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Processando HDRI</h1>
            </div>
            <Button variant="outline" onClick={handleBackToDashboard}>
              Voltar ao Dashboard
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        <JobMonitor 
          jobId={currentJob}
          onComplete={handleJobComplete}
          onError={handleJobError}
          onCancel={handleJobCancel}
        />
      </div>
    </div>
  )

  const renderResults = () => (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Resultados do HDRI</h1>
            </div>
            <Button variant="outline" onClick={handleBackToDashboard}>
              Voltar ao Dashboard
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <JobMonitor 
          jobId={currentJob}
          onComplete={handleJobComplete}
          onError={handleJobError}
          onCancel={handleJobCancel}
        />
      </div>
    </div>
  )

  // Render based on current view
  switch (currentView) {
    case 'upload':
      return renderUpload()
    case 'configure':
      return renderConfigure()
    case 'processing':
      return renderProcessing()
    case 'results':
      return renderResults()
    default:
      return renderDashboard()
  }
}

export default App

