# DiffusionLight Interface

Interface web moderna para geração de HDRIs usando DiffusionLight-ComfyUI, otimizada para deploy em cloud.

## 🎯 Visão Geral

Transforma o complexo workflow do DiffusionLight-ComfyUI em uma interface web intuitiva que permite gerar HDRIs profissionais sem conhecimento técnico em IA.

## 🌐 Arquitetura Cloud

- **Frontend**: React + Vite (Vercel)
- **Backend**: Flask + PostgreSQL (Railway)
- **Database**: Supabase (PostgreSQL + Storage)
- **GPU Processing**: RunPod (ComfyUI)
- **Queue**: Redis + Celery

## 🚀 Deploy Rápido

### Pré-requisitos
- Conta Supabase
- Conta RunPod
- Conta Railway
- Conta Vercel

### 1. Configurar Supabase
```bash
# Criar projeto no Supabase
# Configurar storage bucket: diffusionlight-files
# Copiar credenciais
```

### 2. Configurar RunPod
```bash
# Criar endpoint ComfyUI
# Instalar DiffusionLight nodes
# Configurar webhook
```

### 3. Deploy Backend (Railway)
```bash
# Conectar repositório
# Configurar variáveis de ambiente
# Deploy automático
```

### 4. Deploy Frontend (Vercel)
```bash
# Conectar repositório
# Configurar variáveis de ambiente
# Deploy automático
```

## 📁 Estrutura

```
├── cloud-backend/          # Backend Flask
│   ├── src/
│   │   ├── models/         # Modelos de dados
│   │   ├── routes/         # APIs REST
│   │   ├── services/       # Integração RunPod/Supabase
│   │   └── workers/        # Celery tasks
│   ├── requirements.txt
│   └── railway.json
├── cloud-frontend/         # Frontend React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── hooks/          # Hooks customizados
│   │   └── config/         # Configuração API
│   ├── package.json
│   └── vercel.json
└── deploy-scripts/         # Scripts de automação
```

## 🔧 Configuração Local

### Backend
```bash
cd cloud-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env com suas credenciais
python src/main.py
```

### Frontend
```bash
cd cloud-frontend
npm install
cp .env.example .env
# Editar .env com URL do backend
npm run dev
```

## 🌟 Funcionalidades

### Interface
- ✅ Dashboard com estatísticas
- ✅ Upload drag-and-drop
- ✅ Presets especializados (Automotivo, Produto, Arquitetônico)
- ✅ Monitoramento em tempo real
- ✅ Download direto de resultados

### Backend
- ✅ APIs REST completas
- ✅ Processamento assíncrono
- ✅ Integração RunPod
- ✅ Storage Supabase
- ✅ Sistema de webhooks

### Processamento
- ✅ GPU dedicada (RunPod)
- ✅ Workflow DiffusionLight otimizado
- ✅ Múltiplos formatos (HDR, EXR, NPY)
- ✅ Anti-aliasing configurável
- ✅ Estimativas de tempo precisas

## 💰 Custos Estimados

### Tier Gratuito (50 HDRIs/mês)
- Supabase: $0
- Railway: $0
- Vercel: $0
- RunPod: $5-15
- **Total**: $5-15/mês

### Tier Profissional (500 HDRIs/mês)
- Supabase Pro: $25
- Railway Pro: $20
- Vercel Pro: $20
- RunPod: $50-100
- **Total**: $115-165/mês

## 📚 Documentação

- [Guia de Deploy Cloud](docs/GUIA_DEPLOY_CLOUD.md)
- [Manual de Manutenção](docs/MANUAL_MANUTENCAO.md)
- [Manual do Usuário](docs/MANUAL_USUARIO.md)

## 🆘 Suporte

- **Issues**: Use o sistema de issues do GitHub
- **Email**: savio@setima.cc
- **Documentação**: Consulte a pasta `docs/`

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido para equipes criativas que precisam de HDRIs de qualidade rapidamente.**

