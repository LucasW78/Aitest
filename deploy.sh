#!/bin/bash

# AI用例生成平台生产环境部署脚本

echo "🚀 开始部署AI用例生成平台到生产环境..."

# 配置变量
PORT=9835
HOST="43.143.37.243"
BUILD_DIR="dist"

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装"
    exit 1
fi

# 检查npm环境
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: npm 未安装"
    exit 1
fi

# 安装依赖
echo "📦 安装项目依赖..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

# 构建生产版本
echo "🔨 构建生产版本..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ 构建失败"
    exit 1
fi

# 检查构建结果
if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ 构建目录不存在: $BUILD_DIR"
    exit 1
fi

echo "✅ 构建成功！"
echo ""
echo "🎯 部署信息："
echo "   端口: $PORT"
echo "   IP: $HOST"
echo "   访问地址: http://$HOST:$PORT"
echo ""
echo "🌐 启动生产服务器..."
echo "   本地地址: http://localhost:$PORT"
echo "   外部地址: http://$HOST:$PORT"
echo ""

# 启动生产服务器
npx vite preview --port $PORT --host 0.0.0.0