#!/bin/bash

# Polaris Platform Production Deployment Script
# This script automates the deployment process for the Polaris platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_ENV=${DEPLOY_ENV:-production}
BACKUP_ENABLED=${BACKUP_ENABLED:-true}
HEALTH_CHECK_TIMEOUT=${HEALTH_CHECK_TIMEOUT:-60}
ROLLBACK_ON_FAILURE=${ROLLBACK_ON_FAILURE:-true}

# Directories
DEPLOY_DIR="/opt/polaris"
BACKUP_DIR="/opt/polaris/backups"
LOG_DIR="/var/log/polaris"
VENV_DIR="/opt/polaris/venv"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    sudo mkdir -p $DEPLOY_DIR $BACKUP_DIR $LOG_DIR
    sudo mkdir -p /var/polaris/uploads
    sudo chown -R $USER:$USER $DEPLOY_DIR $LOG_DIR
    sudo chmod 755 $DEPLOY_DIR $LOG_DIR
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]]; then
        print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    # Check Node.js for frontend
    if ! command_exists node; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check if MongoDB is accessible
    if ! command_exists mongosh && ! command_exists mongo; then
        print_warning "MongoDB client not found. Ensure MongoDB is accessible"
    fi
    
    print_success "System requirements check passed"
}

# Function to backup current deployment
backup_current_deployment() {
    if [[ "$BACKUP_ENABLED" == "true" ]]; then
        print_status "Creating backup of current deployment..."
        
        BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_PATH="$BACKUP_DIR/polaris_backup_$BACKUP_TIMESTAMP"
        
        if [[ -d "$DEPLOY_DIR/current" ]]; then
            sudo cp -r "$DEPLOY_DIR/current" "$BACKUP_PATH"
            print_success "Backup created at $BACKUP_PATH"
            echo "$BACKUP_PATH" > /tmp/polaris_backup_path
        else
            print_warning "No current deployment found to backup"
        fi
    fi
}

# Function to setup Python virtual environment
setup_python_environment() {
    print_status "Setting up Python virtual environment..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
    fi
    
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [[ -f "backend/requirements.txt" ]]; then
        pip install -r backend/requirements.txt
    else
        print_error "backend/requirements.txt not found"
        exit 1
    fi
    
    print_success "Python environment setup completed"
}

# Function to build frontend
build_frontend() {
    print_status "Building frontend application..."
    
    cd frontend
    
    # Install dependencies
    if command_exists yarn; then
        yarn install --production
        yarn build
    elif command_exists npm; then
        npm ci --production
        npm run build
    else
        print_error "Neither yarn nor npm found"
        exit 1
    fi
    
    cd ..
    print_success "Frontend build completed"
}

# Function to deploy application
deploy_application() {
    print_status "Deploying application..."
    
    # Create deployment directory
    DEPLOY_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    NEW_DEPLOY_DIR="$DEPLOY_DIR/releases/$DEPLOY_TIMESTAMP"
    sudo mkdir -p "$NEW_DEPLOY_DIR"
    
    # Copy application files
    sudo cp -r backend "$NEW_DEPLOY_DIR/"
    sudo cp -r frontend/build "$NEW_DEPLOY_DIR/frontend"
    
    # Copy configuration files
    if [[ -f ".env.production" ]]; then
        sudo cp .env.production "$NEW_DEPLOY_DIR/backend/.env"
    fi
    
    # Update symlink
    sudo rm -f "$DEPLOY_DIR/current"
    sudo ln -s "$NEW_DEPLOY_DIR" "$DEPLOY_DIR/current"
    
    print_success "Application deployed to $NEW_DEPLOY_DIR"
}

# Function to setup systemd services
setup_systemd_services() {
    print_status "Setting up systemd services..."
    
    # Backend service
    sudo tee /etc/systemd/system/polaris-backend.service > /dev/null <<EOF
[Unit]
Description=Polaris Platform Backend
After=network.target mongodb.service
Wants=mongodb.service

[Service]
Type=simple
User=polaris
Group=polaris
WorkingDirectory=$DEPLOY_DIR/current/backend
Environment=POLARIS_ENV=production
ExecStart=$VENV_DIR/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Frontend service (using nginx)
    sudo tee /etc/nginx/sites-available/polaris > /dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name polaris.example.com www.polaris.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name polaris.example.com www.polaris.example.com;
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/polaris.crt;
    ssl_certificate_key /etc/ssl/private/polaris.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Frontend files
    root $DEPLOY_DIR/current/frontend;
    index index.html;
    
    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Frontend routing
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
}
EOF

    # Enable services
    sudo systemctl daemon-reload
    sudo systemctl enable polaris-backend
    
    if command_exists nginx; then
        sudo ln -sf /etc/nginx/sites-available/polaris /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl reload nginx
    fi
    
    print_success "Systemd services configured"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    source "$VENV_DIR/bin/activate"
    cd "$DEPLOY_DIR/current/backend"
    
    # Run any migration scripts here
    # python migrate.py
    
    print_success "Database migrations completed"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    sudo systemctl start polaris-backend
    sudo systemctl status polaris-backend --no-pager
    
    print_success "Services started"
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    local timeout=$HEALTH_CHECK_TIMEOUT
    local count=0
    
    while [[ $count -lt $timeout ]]; do
        if curl -f -s http://localhost:8000/api/system/health > /dev/null; then
            print_success "Health check passed"
            return 0
        fi
        
        sleep 1
        ((count++))
    done
    
    print_error "Health check failed after $timeout seconds"
    return 1
}

# Function to rollback deployment
rollback_deployment() {
    print_error "Deployment failed. Rolling back..."
    
    if [[ -f "/tmp/polaris_backup_path" ]]; then
        BACKUP_PATH=$(cat /tmp/polaris_backup_path)
        if [[ -d "$BACKUP_PATH" ]]; then
            sudo rm -f "$DEPLOY_DIR/current"
            sudo ln -s "$BACKUP_PATH" "$DEPLOY_DIR/current"
            sudo systemctl restart polaris-backend
            print_success "Rollback completed"
        fi
    fi
}

# Function to cleanup old releases
cleanup_old_releases() {
    print_status "Cleaning up old releases..."
    
    # Keep last 5 releases
    if [[ -d "$DEPLOY_DIR/releases" ]]; then
        cd "$DEPLOY_DIR/releases"
        ls -t | tail -n +6 | xargs -r sudo rm -rf
        print_success "Old releases cleaned up"
    fi
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Setup log rotation
    sudo tee /etc/logrotate.d/polaris > /dev/null <<EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

    # Setup monitoring script
    sudo tee /usr/local/bin/polaris-monitor.sh > /dev/null <<'EOF'
#!/bin/bash
# Simple monitoring script

LOG_FILE="/var/log/polaris/monitor.log"
API_URL="http://localhost:8000/api/system/health"

check_health() {
    if curl -f -s "$API_URL" > /dev/null; then
        echo "$(date): Health check passed" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): Health check failed" >> "$LOG_FILE"
        # Send alert here (email, Slack, etc.)
        return 1
    fi
}

check_health
EOF

    sudo chmod +x /usr/local/bin/polaris-monitor.sh
    
    # Setup cron job for monitoring
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/polaris-monitor.sh") | crontab -
    
    print_success "Monitoring setup completed"
}

# Main deployment function
main() {
    print_status "Starting Polaris Platform deployment..."
    print_status "Environment: $DEPLOY_ENV"
    print_status "Timestamp: $(date)"
    
    # Pre-deployment checks
    check_requirements
    create_directories
    
    # Backup current deployment
    backup_current_deployment
    
    # Build and deploy
    setup_python_environment
    build_frontend
    deploy_application
    
    # Configure services
    setup_systemd_services
    run_migrations
    start_services
    
    # Post-deployment
    if run_health_checks; then
        cleanup_old_releases
        setup_monitoring
        print_success "Deployment completed successfully!"
        print_status "Application is running at https://polaris.example.com"
    else
        if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
            rollback_deployment
        fi
        exit 1
    fi
}

# Trap errors and cleanup
trap 'print_error "Deployment failed at line $LINENO"' ERR

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi