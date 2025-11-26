# Change: 优化页面宽度适应

## Why
当前文档管理页面和用例设计页面的宽度限制较严格，在大屏幕设备上未能充分利用可用空间，影响用户体验和内容展示效果。

## What Changes
- 移除固定最大宽度限制，让页面更好地适应不同屏幕尺寸
- 优化文档管理页面的表格和表单布局
- 改进用例设计页面的左右分区比例
- 增强响应式设计，确保在各种窗口尺寸下都有良好体验
- 保持内容可读性和操作便利性

## Impact
- 受影响的规格: `ui-responsive-design`
- 受影响的代码:
  - `src/views/DocumentManagement.vue`
  - `src/views/TestCaseDesign.vue`
  - `src/views/Home.vue`
- 不影响后端API或数据结构