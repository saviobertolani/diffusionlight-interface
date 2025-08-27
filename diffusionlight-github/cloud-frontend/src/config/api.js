// API Configuration for production deployment

const config = {
  // API Base URL - will be set by environment variable
API_BASE_URL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000/api',
  
  // App Configuration
  APP_NAME: import.meta.env.VITE_APP_NAME || 'DiffusionLight',
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  
  // Environment
  NODE_ENV: import.meta.env.VITE_NODE_ENV || 'development',
  
  // Upload Settings
  MAX_FILE_SIZE: parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '200') * 1024 * 1024, // Convert MB to bytes
  ALLOWED_FILE_TYPES: (import.meta.env.VITE_ALLOWED_FILE_TYPES || 'jpg,jpeg,png,tiff,tif').split(','),
  
  // Feature Flags
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_ERROR_REPORTING: import.meta.env.VITE_ENABLE_ERROR_REPORTING === 'true',
  ENABLE_DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true',
  
  // UI Settings
  THEME: import.meta.env.VITE_THEME || 'light',
  BRAND_COLOR: import.meta.env.VITE_BRAND_COLOR || '#3b82f6',
  
  // External Services
  GOOGLE_ANALYTICS_ID: import.meta.env.VITE_GOOGLE_ANALYTICS_ID,
  SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN,
}

// Validation
if (config.NODE_ENV === 'production') {
  if (!config.API_BASE_URL || config.API_BASE_URL.includes('localhost')) {
    console.warn('⚠️ API_BASE_URL not configured for production')
  }
}

// Debug logging
if (config.ENABLE_DEBUG) {
  console.log('🔧 App Configuration:', config)
}

export default config

