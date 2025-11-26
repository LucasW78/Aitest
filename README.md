# AI用例生成平台 (AItestdemo)

一个基于Vue 3 + TypeScript的智能测试用例生成平台，支持文档管理和测试用例设计。

## 🌟 功能特性

### 📚 文档管理
- **文档上传**: 支持多种格式文件上传 (.txt, .md, .doc, .docx, .pdf, .jpg, .jpeg, .png)
- **智能筛选**: 按文档标题和标签进行筛选，标签支持"或"关系查询
- **标签管理**: 自定义标签，支持动态添加和删除，带清空功能
- **文档操作**: 在线预览、下载、删除功能
- **批量标签**: 支持为文档批量添加和管理标签
- **响应式设计**: 适配不同屏幕尺寸，支持移动端操作

### 🎯 用例设计
- **双重输入**: 支持文件上传和在线文本输入，两者相互独立
- **智能生成**: 基于文档或文本生成测试用例
- **思维导图**: 使用JsMind库进行思维导图可视化
- **交互编辑**: 支持思维导图节点的二次编辑和扩展
- **键盘快捷键**:
  - `Tab` - 添加子节点
  - `Enter` - 添加同级节点
  - `Delete/Backspace` - 删除节点
  - 双击节点进入编辑模式
- **导出功能**: 支持测试用例导出为XMind格式
- **二次校验**: 提供测试用例格式校验功能

### 🧠 思维导图 (JsMind)
- **专业展示**: 基于JsMind库的专业思维导图引擎
- **可视化交互**: 支持缩放、展开/收起、拖拽操作
- **节点编辑**: 支持添加、编辑、删除节点
- **类型区分**: 不同测试类型用不同样式展示
- **自动布局**: 智能节点布局和连线

## 🛠 技术栈

### 前端技术
- **框架**: Vue 3.3.8 + TypeScript 5.2.2
- **UI组件**: Element Plus 2.4.4
- **构建工具**: Vite 5.0.0
- **状态管理**: Pinia 2.1.7
- **路由管理**: Vue Router 4.2.5
- **思维导图**: JsMind (CDN集成)

### 后端预留
- **框架**: FastAPI (Python)
- **数据验证**: Pydantic
- **服务器**: Uvicorn
- **测试框架**: pytest + coverage

### 开发工具
- **进程管理**: PM2
- **代码检查**: ESLint
- **版本控制**: Git

## 📁 项目结构

```
AItestdemo/
├── src/
│   ├── components/
│   │   └── JsMindViewer.vue          # 思维导图查看器组件
│   ├── views/
│   │   ├── Home.vue                  # 主页面（Tab导航）
│   │   ├── DocumentManagement.vue    # 文档管理页面
│   │   └── TestCaseDesign.vue        # 测试用例设计页面
│   ├── router/
│   │   └── index.ts                  # 路由配置
│   ├── types/
│   │   └── index.ts                  # TypeScript类型定义
│   ├── App.vue                       # 根组件
│   └── main.ts                       # 应用入口
├── backend/                           # 后端代码（预留）
│   └── src/
│       └── models/
│           └── test_models.py        # 测试数据模型
├── public/                           # 静态资源
├── dist/                            # 构建输出
├── logs/                            # 日志目录
├── package.json                     # 前端依赖
├── vite.config.ts                   # Vite配置
├── ecosystem.config.js              # PM2配置
├── start.sh                         # 快速启动脚本
└── deploy.sh                        # 部署脚本
```

## 🚀 安装和运行

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0

### 快速启动
```bash
# 克隆项目
git clone [项目地址]
cd AItestdemo

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 或使用快速启动脚本
./start.sh
```

### 访问地址
- **本地访问**: http://localhost:9835
- **外部访问**: http://0.0.0.0:9835
- **生产环境**: http://43.143.37.243:9835

### 生产部署
```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 或使用PM2部署
npm run deploy
```

## 📖 使用指南

### 文档管理
1. 进入"文档管理"页面
2. 使用筛选条件查找文档：
   - 按文档标题搜索（实时输入）
   - 按标签筛选（支持多选"或"关系）
   - 点击"搜索"按钮应用筛选条件
3. 点击"上传文档"按钮上传新文件
4. 在文档列表中进行操作：
   - 点击文档标题预览内容
   - 管理标签（添加、删除）
   - 下载或删除文档
5. 标签编辑：
   - 点击标签旁的"+"添加新标签
   - 输入完成后按Enter确认或失焦保存
   - 按ESC取消编辑

### 用例设计
1. 进入"用例设计"页面
2. 选择输入方式：
   - **文件上传**: 拖拽或点击上传文件，上传完成后可选择生成或删除
   - **在线输入**: 在文本框中输入需求描述，无字符限制
3. 生成测试用例：
   - 点击对应的"生成测试用例"按钮
   - 系统将生成思维导图形式的测试用例
4. 编辑思维导图：
   - 双击节点进入编辑模式
   - 使用键盘快捷键添加/删除节点
   - 支持节点内容的实时修改
5. 导出功能：
   - 点击"二次校验"验证格式
   - 点击"导出"生成XMind格式文件

## 🔧 开发说明

### 代码规范
- 使用 TypeScript 进行类型安全开发
- 遵循 Vue 3 Composition API 规范
- 使用 Element Plus 组件库保持 UI 一致性
- 响应式设计，支持不同屏幕尺寸
- 组件化开发，代码复用性高

### 项目特性
- **TypeScript全覆盖**: 完整的类型定义和类型检查
- **组件化架构**: 基于Vue 3的现代组件设计
- **外部网络访问**: 支持公网访问部署
- **生产就绪**: 配置完整的PM2部署方案

### Git工作流
```bash
# 功能开发
git checkout -b feature/功能名称
git add .
git commit -m "描述功能变更"
git push origin feature/功能名称

# 合并到主分支
git checkout main
git merge feature/功能名称
git push origin main
```

## 🎯 功能规划

### 近期计划
- [ ] AI接口集成（支持实际的测试用例生成）
- [ ] 更多导出格式支持
- [ ] 用户登录和权限管理
- [ ] 测试用例模板库

### 中期计划
- [ ] 测试用例执行引擎
- [ ] 报告生成和统计
- [ ] 团队协作功能
- [ ] API接口文档

### 长期规划
- [ ] 多语言支持（国际化）
- [ ] 插件系统
- [ ] 云端同步
- [ ] 移动端App

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 开启 Pull Request

### 开发环境配置
```bash
# 安装开发依赖
npm install

# 启动开发服务器
npm run dev

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [Issue](../../issues)
- 发起 [Discussion](../../discussions)
- 项目维护者联系方式

---

**注意**: 本项目为MVP版本，专注于前端功能的完整实现。后端AI接口集成将在后续版本中完成。当前版本使用模拟数据展示功能。