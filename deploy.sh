#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install required system packages
apt-get install -y python3-venv python3-pip nginx

# Create application directory
mkdir -p /root/company-research
cd /root/company-research

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Copy service file
cp company-research.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable and start the service
systemctl enable company-research
systemctl start company-research

# Configure Nginx
cat > /etc/nginx/sites-available/company-research << 'EOL'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL

# Enable Nginx site
ln -sf /etc/nginx/sites-available/company-research /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

echo "Deployment completed successfully!" 