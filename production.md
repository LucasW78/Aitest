# 生产环境部署指南

## 网络配置

- **服务器IP**: 43.143.37.243
- **端口**: 9835
- **外部访问地址**: http://43.143.37.243:9835

## 部署方式

### 方式1: 使用部署脚本（推荐）

```bash
./deploy.sh
```

### 方式2: 手动部署

```bash
# 1. 安装依赖
npm install

# 2. 构建生产版本
npm run build

# 3. 启动生产服务器
npm run preview
```

### 方式3: 使用PM2进程管理

```bash
# 安装PM2
npm install -g pm2

# 使用PM2启动
pm2 start ecosystem.config.js

# 查看进程状态
pm2 status

# 查看日志
pm2 logs

# 停止服务
pm2 stop aitestdemo

# 重启服务
pm2 restart aitestdemo
```

## 防火墙配置

确保服务器防火墙允许9835端口的访问：

```bash
# 如果使用iptables
sudo iptables -A INPUT -p tcp --dport 9835 -j ACCEPT

# 如果使用ufw (Ubuntu)
sudo ufw allow 9835

# 如果使用firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=9835/tcp
sudo firewall-cmd --reload
```

## Nginx反向代理配置（可选）

如果需要配置域名访问，可以使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:9835;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 监控和日志

### 日志文件位置

- 应用日志: `./logs/out.log`
- 错误日志: `./logs/err.log`
- 合并日志: `./logs/combined.log`

### 监控命令

```bash
# 查看实时日志
tail -f logs/out.log

# 查看错误日志
tail -f logs/err.log

# 检查端口占用
netstat -tlnp | grep 9835

# 检查服务状态
curl http://localhost:9835
```

## 常见问题

### 1. 端口被占用

```bash
# 查看占用9835端口的进程
sudo lsof -i :9835

# 杀死进程
sudo kill -9 <PID>
```

### 2. 权限问题

确保有足够的权限操作文件和端口：

```bash
# 给脚本执行权限
chmod +x deploy.sh

# 检查目录权限
ls -la
```

### 3. 内存不足

如果服务器内存不足，可以优化配置：

```bash
# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 性能优化

### 1. 开启Gzip压缩

在`vite.config.ts`中添加：

```typescript
export default defineConfig({
  // ... 其他配置
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          element: ['element-plus']
        }
      }
    }
  }
})
```

### 2. 启用缓存

配置适当的缓存策略以减少服务器负载。

## 安全建议

1. **定期更新依赖包**
2. **配置HTTPS**（使用SSL证书）
3. **设置访问限制**
4. **定期备份数据**
5. **监控异常访问**

## 维护

### 定期任务

```bash
# 清理日志
crontab -e
# 添加：0 0 * * 0 find /opt/AItestdemo/logs -name "*.log" -mtime +7 -delete

# 重启服务
pm2 restart aitestdemo
```

### 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新部署
./deploy.sh
```