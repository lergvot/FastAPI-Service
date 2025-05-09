#!/bin/bash
# Загружаем актуальные IP GitHub
curl -s https://api.github.com/meta | grep -E 'web|actions' | grep -Po '"[\d./]+"' | tr -d '"' > /etc/nginx/whitelist_g>
# Форматируем файл в список allow
sed -i 's/^/allow /; s/$/;/' /etc/nginx/whitelist_github_ips.conf
echo "deny all;" >> /etc/nginx/whitelist_github_ips.conf

# Проверяем конфигурацию и перезапускаем Nginx
nginx -t && systemctl reload nginx