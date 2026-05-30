# Frontend

AI 报告系统前端，基于 React 19 + Vite + TypeScript 构建。

## 技术栈

- **React 19** —— UI 框架
- **Vite** —— 构建工具
- **TypeScript** —— 类型安全
- **Tailwind CSS** —— 样式
- **Zustand** —— 状态管理
- **TanStack Query** —— 服务端状态管理
- **React Router v7** —— 路由
- **ReactFlow** —— 流程图可视化
- **Recharts** —— 图表

## 目录说明

```
frontend/src/
├── app/              # 页面路由组件
│   ├── dashboard/
│   ├── reports/
│   ├── admin/
│   └── ...
├── components/       # 可复用组件
│   ├── layout/       # 布局（Sidebar、TopNav、AppShell）
│   ├── report/       # 报告相关（AgentChat、ReportPreview）
│   └── ui/           # 基础 UI（Button、Card、Input）
├── stores/           # Zustand 状态存储
├── api/              # API 请求封装
├── types/            # TypeScript 类型定义
├── hooks/            # 自定义 Hooks
└── lib/              # 工具函数
```

## 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
```

## 配置说明

- `vite.config.ts` —— Vite 配置（路径别名 `@/` 指向 `src/`）
- `tailwind.config.js` —— Tailwind CSS 主题配置
- `postcss.config.cjs` —— PostCSS 配置
- `tsconfig.json` —— TypeScript 严格模式开启
