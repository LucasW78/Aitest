#!/bin/bash

# AI用例生成平台启动脚本

echo "🚀 启动AI用例生成平台..."

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装，请先安装 Node.js >= 16.0.0"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: npm 未安装，请先安装 npm >= 8.0.0"
    exit 1
fi

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "❌ 错误: package.json 文件不存在"
    exit 1
fi

# 检查node_modules是否存在，如果不存在则安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装项目依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 启动开发服务器
echo "🌐 启动开发服务器..."
echo "📡 外部访问地址: http://43.143.37.243:9835"
echo "🏠 本地访问地址: http://localhost:9835"
echo ""
npm run dev