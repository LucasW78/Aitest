module.exports = {
  apps: [
    {
      name: 'aitestdemo',
      script: 'npx',
      args: 'vite preview --port 9835 --host 0.0.0.0',
      cwd: '/opt/AItestdemo',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        HOST: '0.0.0.0',
        PORT: 9835
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true
    }
  ]
};