#!/bin/bash

# DiffusionLight Deploy Script
# This script automates the deployment of DiffusionLight to various cloud platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="diffusionlight"
BACKEND_DIR="../cloud-backend"
FRONTEND_DIR="../cloud-frontend"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check if required tools are installed
    command -v git >/dev/null 2>&1 || { log_error "git is required but not installed."; exit 1; }
    command -v node >/dev/null 2>&1 || { log_error "node is required but not installed."; exit 1; }
    command -v npm >/dev/null 2>&1 || { log_error "npm is required but not installed."; exit 1; }
    
    log_success "All dependencies are installed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env files if they don't exist
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        log_warning "Backend .env file not found. Creating from example..."
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        log_warning "Please edit $BACKEND_DIR/.env with your configuration"
    fi
    
    if [ ! -f "$FRONTEND_DIR/.env" ]; then
        log_warning "Frontend .env file not found. Creating from example..."
        cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
        log_warning "Please edit $FRONTEND_DIR/.env with your configuration"
    fi
}

deploy_to_railway() {
    log_info "Deploying backend to Railway..."
    
    cd "$BACKEND_DIR"
    
    # Check if Railway CLI is installed
    if ! command -v railway >/dev/null 2>&1; then
        log_error "Railway CLI is not installed. Install it from: https://railway.app/cli"
        return 1
    fi
    
    # Login check
    if ! railway whoami >/dev/null 2>&1; then
        log_warning "Not logged in to Railway. Please run: railway login"
        return 1
    fi
    
    # Deploy
    railway up
    
    log_success "Backend deployed to Railway"
    cd - >/dev/null
}

deploy_to_render() {
    log_info "Deploying backend to Render..."
    
    cd "$BACKEND_DIR"
    
    log_info "Please follow these steps to deploy to Render:"
    echo "1. Go to https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create a new Web Service"
    echo "4. Use the render.yaml configuration file"
    echo "5. Set environment variables as specified in .env.example"
    
    cd - >/dev/null
}

deploy_to_vercel() {
    log_info "Deploying frontend to Vercel..."
    
    cd "$FRONTEND_DIR"
    
    # Check if Vercel CLI is installed
    if ! command -v vercel >/dev/null 2>&1; then
        log_info "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    # Build the project
    log_info "Building frontend..."
    npm install
    npm run build
    
    # Deploy
    vercel --prod
    
    log_success "Frontend deployed to Vercel"
    cd - >/dev/null
}

deploy_to_netlify() {
    log_info "Deploying frontend to Netlify..."
    
    cd "$FRONTEND_DIR"
    
    # Check if Netlify CLI is installed
    if ! command -v netlify >/dev/null 2>&1; then
        log_info "Installing Netlify CLI..."
        npm install -g netlify-cli
    fi
    
    # Build the project
    log_info "Building frontend..."
    npm install
    npm run build
    
    # Deploy
    netlify deploy --prod --dir=dist
    
    log_success "Frontend deployed to Netlify"
    cd - >/dev/null
}

setup_supabase() {
    log_info "Setting up Supabase..."
    
    echo "Please follow these steps to set up Supabase:"
    echo "1. Go to https://supabase.com"
    echo "2. Create a new project"
    echo "3. Go to Settings > API"
    echo "4. Copy the Project URL and anon key"
    echo "5. Go to Storage and create a bucket named 'diffusionlight-files'"
    echo "6. Set the bucket to public"
    echo "7. Update your .env files with the Supabase credentials"
    
    log_warning "Don't forget to update DATABASE_URL with your Supabase PostgreSQL connection string"
}

setup_runpod() {
    log_info "Setting up RunPod..."
    
    echo "Please follow these steps to set up RunPod:"
    echo "1. Go to https://runpod.io"
    echo "2. Create an account and add credits"
    echo "3. Go to Serverless > Endpoints"
    echo "4. Create a new endpoint with ComfyUI template"
    echo "5. Install DiffusionLight nodes in the ComfyUI environment"
    echo "6. Copy the endpoint ID and API key"
    echo "7. Update your .env files with RunPod credentials"
    
    log_warning "Make sure to configure the webhook URL to point to your deployed backend"
}

show_help() {
    echo "DiffusionLight Deploy Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  check         Check dependencies"
    echo "  setup         Setup environment files"
    echo "  railway       Deploy backend to Railway"
    echo "  render        Deploy backend to Render"
    echo "  vercel        Deploy frontend to Vercel"
    echo "  netlify       Deploy frontend to Netlify"
    echo "  supabase      Setup Supabase instructions"
    echo "  runpod        Setup RunPod instructions"
    echo "  full          Full deployment (setup + deploy)"
    echo "  help          Show this help message"
    echo ""
}

# Main script
case "${1:-help}" in
    check)
        check_dependencies
        ;;
    setup)
        setup_environment
        ;;
    railway)
        check_dependencies
        deploy_to_railway
        ;;
    render)
        check_dependencies
        deploy_to_render
        ;;
    vercel)
        check_dependencies
        deploy_to_vercel
        ;;
    netlify)
        check_dependencies
        deploy_to_netlify
        ;;
    supabase)
        setup_supabase
        ;;
    runpod)
        setup_runpod
        ;;
    full)
        check_dependencies
        setup_environment
        log_info "Starting full deployment..."
        log_info "Please choose your preferred platforms and follow the instructions"
        setup_supabase
        setup_runpod
        ;;
    help|*)
        show_help
        ;;
esac

log_success "Script completed!"

