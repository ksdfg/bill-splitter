#!/bin/sh
set -eu

cat > /usr/share/nginx/html/config.js <<EOF
window.__APP_CONFIG__ = Object.assign({}, window.__APP_CONFIG__, {
  VITE_API_BASE_URL: "${VITE_API_BASE_URL:-}"
});
EOF

exec "$@"
