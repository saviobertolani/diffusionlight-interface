import { useState, useRef } from 'react'
import { Upload, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { useFileUpload } from '../hooks/useApi'

const FileUploader = ({ onUploadSuccess, onUploadError }) => {
  const [dragActive, setDragActive] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [uploadResult, setUploadResult] = useState(null)
  const fileInputRef = useRef(null)
  
  const { uploadFile, loading, error } = useFileUpload()

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file) => {
    // Validar tipo de arquivo
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff']
    if (!allowedTypes.includes(file.type)) {
      onUploadError?.('Tipo de arquivo não suportado. Use JPG, PNG ou TIFF.')
      return
    }

    // Validar tamanho (200MB max)
    const maxSize = 200 * 1024 * 1024
    if (file.size > maxSize) {
      onUploadError?.('Arquivo muito grande. Tamanho máximo: 200MB.')
      return
    }

    setUploadedFile(file)
    
    try {
      const result = await uploadFile(file)
      setUploadResult(result)
      onUploadSuccess?.(result)
    } catch (err) {
      onUploadError?.(err.message)
      setUploadedFile(null)
    }
  }

  const removeFile = () => {
    setUploadedFile(null)
    setUploadResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (uploadedFile && uploadResult) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900">
                  Arquivo enviado com sucesso
                </h3>
                <div className="mt-1 text-sm text-gray-500">
                  <p><strong>Nome:</strong> {uploadedFile.name}</p>
                  <p><strong>Tamanho:</strong> {formatFileSize(uploadedFile.size)}</p>
                  {uploadResult.width && uploadResult.height && (
                    <p><strong>Resolução:</strong> {uploadResult.width} × {uploadResult.height}</p>
                  )}
                  {uploadResult.format && (
                    <p><strong>Formato:</strong> {uploadResult.format}</p>
                  )}
                </div>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={removeFile}>
              <X className="h-4 w-4 mr-1" />
              Remover
            </Button>
          </div>
          
          {/* Preview da imagem */}
          <div className="mt-4">
            <img 
              src={URL.createObjectURL(uploadedFile)} 
              alt="Preview" 
              className="max-w-full max-h-64 object-contain rounded-lg border"
            />
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
          } ${loading ? 'opacity-50 pointer-events-none' : 'cursor-pointer'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="hidden"
            disabled={loading}
          />
          
          {loading ? (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Enviando arquivo...
              </h3>
              <p className="text-gray-500">
                Aguarde enquanto processamos seu arquivo
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Upload className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Arraste uma imagem aqui ou clique para selecionar
              </h3>
              <p className="text-gray-500 mb-4">
                Formatos suportados: JPG, PNG, TIFF
              </p>
              <p className="text-sm text-gray-400">
                Tamanho máximo: 200MB • Resolução recomendada: 1920×1080 ou superior
              </p>
            </div>
          )}
        </div>
        
        {error && (
          <div className="mt-4 flex items-center space-x-2 text-red-600">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default FileUploader

