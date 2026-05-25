# YMS 系统 Linux 移植方案

**创建时间**: 2026-03-23  
**优先级**: P1 - 重要但不紧急  
**状态**: 规划阶段

---

## 📋 任务背景

将 YMS（良率管理系统）从当前环境移植到 Linux 系统，确保系统可在 Linux 服务器上稳定运行，支持生产环境部署。

---

## 🎯 移植目标

### 功能目标
- ✅ 所有 Python 脚本在 Linux 环境下正常运行
- ✅ 数据分析功能（相关性分析、SPC、Wafer Map 等）正常工作
- ✅ 数据导入/导出功能兼容
- ✅ 报告生成功能正常

### 性能目标
- ✅ 支持大规模数据处理（10W+ Wafer 数据）
- ✅ 响应时间 < 5 秒（常规查询）
- ✅ 支持多用户并发访问（如部署 Web 界面）

### 部署目标
- ✅ 支持 Ubuntu 20.04/22.04 LTS
- ✅ 支持 CentOS 7/8 或 Rocky Linux
- ✅ 提供一键部署脚本
- ✅ 提供 Docker 容器化方案（可选）

---

## 🔍 当前系统分析

### 现有组件

| 组件 | 文件 | 依赖 | Linux 兼容性 |
|------|------|------|-------------|
| 相关性分析 | `correlation_analysis.py` | pandas, numpy, scipy | ✅ 完全兼容 |
| Wafer Map 可视化 | `wafer_map_viz.py` (待实现) | matplotlib, plotly | ✅ 完全兼容 |
| SPC 控制图 | `spc_chart.py` (待实现) | pandas, matplotlib | ✅ 完全兼容 |
| 缺陷 Pareto | `defect_pareto.py` (待实现) | pandas, matplotlib | ✅ 完全兼容 |

### 潜在兼容性问题

#### 1. 文件路径问题
```python
# ❌ Windows 风格
file_path = "C:\\Users\\data\\wafers.csv"

# ✅ Linux 风格（跨平台）
import os
file_path = os.path.join("data", "wafers.csv")
# 或使用 pathlib
from pathlib import Path
file_path = Path("data") / "wafers.csv"
```

#### 2. 换行符问题
```python
# ❌ 硬编码换行符
with open(file, 'w') as f:
    f.write(data + '\r\n')  # Windows

# ✅ 使用 universal newline
with open(file, 'w', newline='') as f:
    writer = csv.writer(f)
```

#### 3. 编码问题
```python
# ✅ 始终指定编码
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()
```

#### 4. 系统命令调用
```python
# ❌ Windows 特定命令
os.system('dir')  # Windows

# ✅ 跨平台或使用 subprocess
import subprocess
subprocess.run(['ls', '-la'])  # Linux
```

---

## 📦 移植步骤

### Phase 1: 环境准备（1-2 天）

#### 1.1 选择目标 Linux 发行版
**推荐**: Ubuntu 22.04 LTS（社区支持好，文档丰富）

#### 1.2 安装 Python 环境
```bash
# 检查 Python 版本
python3 --version  # 需要 3.8+

# 安装 pip
sudo apt update
sudo apt install python3-pip python3-venv

# 创建虚拟环境
python3 -m venv yms_env
source yms_env/bin/activate
```

#### 1.3 安装依赖包
```bash
# 创建 requirements.txt
cat > requirements.txt << EOF
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.9.0
matplotlib>=3.6.0
plotly>=5.11.0
openpyxl>=3.0.0  # Excel 支持
jinja2>=3.1.0    # 报告模板
EOF

# 安装依赖
pip install -r requirements.txt
```

---

### Phase 2: 代码适配（2-3 天）

#### 2.1 路径兼容性改造
```python
# 改造所有文件路径引用
from pathlib import Path

# 定义项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# 使用 Path 对象操作
data_file = DATA_DIR / "wafers.csv"
output_file = OUTPUT_DIR / "report.html"
```

#### 2.2 配置文件适配
```ini
# config.ini 示例
[paths]
data_dir = /opt/yms/data
output_dir = /opt/yms/output
log_dir = /var/log/yms

[database]
type = sqlite
path = /opt/yms/data/yms.db
```

#### 2.3 日志系统配置
```python
import logging
from pathlib import Path

# 配置日志
log_dir = Path('/var/log/yms')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'yms.log'),
        logging.StreamHandler()
    ]
)
```

---

### Phase 3: 功能测试（2-3 天）

#### 3.1 单元测试
```python
# tests/test_correlation.py
import unittest
from pathlib import Path

class TestCorrelationAnalysis(unittest.TestCase):
    def test_pearson_correlation(self):
        # 测试数据
        test_data = Path(__file__).parent / "test_data.csv"
        # 执行分析
        # 验证结果
        pass
```

#### 3.2 集成测试
```bash
# 测试完整流程
python3 scripts/correlation_analysis.py \
  --input data/sample.csv \
  --output output/test_report.html
```

#### 3.3 性能测试
```bash
# 大数据集测试
time python3 scripts/correlation_analysis.py \
  --input data/large_dataset.csv \
  --output output/perf_test.html
```

---

### Phase 4: 部署脚本（1-2 天）

#### 4.1 创建安装脚本
```bash
#!/bin/bash
# install.sh - YMS 系统安装脚本

set -e

echo "=== YMS 系统安装 ==="

# 1. 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误：需要 Python 3.8+"
    exit 1
fi

# 2. 创建目录结构
sudo mkdir -p /opt/yms/{data,output,logs,scripts}
sudo chown -R $USER:$USER /opt/yms

# 3. 创建虚拟环境
python3 -m venv /opt/yms/venv
source /opt/yms/venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
echo "export YMS_HOME=/opt/yms" >> ~/.bashrc
echo "export PATH=\$PATH:/opt/yms/venv/bin" >> ~/.bashrc

echo "=== 安装完成 ==="
echo "请运行：source ~/.bashrc"
```

#### 4.2 创建系统服务（systemd）
```ini
# /etc/systemd/system/yms.service
[Unit]
Description=YMS Backend Service
After=network.target

[Service]
Type=simple
User=yms
WorkingDirectory=/opt/yms
ExecStart=/opt/yms/venv/bin/python3 -m flask run --host=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4.3 Docker 部署方案（可选）
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV YMS_HOME=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口（如有 Web 界面）
EXPOSE 5000

# 启动命令
CMD ["python3", "scripts/main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  yms:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - YMS_ENV=production
```

---

### Phase 5: 文档与培训（1 天）

#### 5.1 编写用户文档
- 安装指南
- 使用手册
- 故障排查指南

#### 5.2 编写运维文档
- 日常维护清单
- 备份恢复流程
- 监控告警配置

---

## ⚠️ 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 依赖包兼容性问题 | 中 | 低 | 提前在 Linux 环境测试所有依赖 |
| 性能下降 | 中 | 低 | 进行性能基准测试 |
| 数据迁移丢失 | 高 | 低 | 完整备份 + 验证校验和 |
| 权限配置错误 | 中 | 中 | 使用最小权限原则，详细测试 |

---

## 📊 验收标准

### 功能验收
- [ ] 所有脚本在 Linux 环境下正常运行
- [ ] 输出结果与原始环境一致
- [ ] 无路径/编码/换行符相关问题

### 性能验收
- [ ] 处理 10K Wafer 数据 < 10 秒
- [ ] 处理 100K Wafer 数据 < 2 分钟
- [ ] 内存占用 < 2GB

### 部署验收
- [ ] 一键安装脚本成功执行
- [ ] systemd 服务正常启动/停止
- [ ] Docker 容器可正常部署（如采用）

---

## 📅 时间估算

| 阶段 | 工作内容 | 预计时间 |
|------|----------|----------|
| Phase 1 | 环境准备 | 1-2 天 |
| Phase 2 | 代码适配 | 2-3 天 |
| Phase 3 | 功能测试 | 2-3 天 |
| Phase 4 | 部署脚本 | 1-2 天 |
| Phase 5 | 文档编写 | 1 天 |
| **总计** | | **7-11 天** |

---

## 🎯 下一步行动

### 立即行动（本周）
1. [ ] 准备 Linux 测试环境（虚拟机或云服务器）
2. [ ] 安装 Python 和基础依赖
3. [ ] 测试现有脚本的兼容性

### 短期计划（2 周内）
1. [ ] 完成代码适配改造
2. [ ] 编写安装脚本
3. [ ] 完成功能测试

### 长期计划（1 个月内）
1. [ ] 完成 Docker 容器化
2. [ ] 编写完整文档
3. [ ] 生产环境部署

---

## 📚 参考资料

- [Python 跨平台最佳实践](https://docs.python.org/3/library/os.html#os.path)
- [Ubuntu Python 开发指南](https://ubuntu.com/server/docs/service-python)
- [Docker Python 应用部署](https://docs.docker.com/language/python/)
- [systemd 服务配置](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**创建者**: lamber  
**最后更新**: 2026-03-23 13:30  
**状态**: 规划完成，等待执行
