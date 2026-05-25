# YMS 项目 PyCharm 配置指南

**创建日期**: 2026-03-30  
**PyCharm 版本**: 2023.1+ 推荐

---

## 📋 步骤 1: 打开项目

1. 启动 PyCharm
2. 选择 **File** → **Open** (或点击 "Open")
3. 浏览到项目目录: `/home/admin/openclaw/workspace/yms-project/`
4. 点击 **OK**

---

## 🔧 步骤 2: 配置 Python 解释器

### 2.1 创建虚拟环境

**方法 A: 使用 PyCharm 创建**

1. **File** → **Settings** (Windows: **File** → **Settings**, macOS: **PyCharm** → **Preferences**)
2. 导航到 **Project: yms-project** → **Python Interpreter**
3. 点击齿轮图标 ⚙️ → **Add...**
4. 选择 **Virtualenv Environment** → **New**
5. 配置:
   - **Location**: `$ProjectFileDir$/venv`
   - **Base interpreter**: Python 3.9+ (选择系统 Python)
   - **Inherit global site-packages**: 不勾选
   - **Make available to all projects**: 不勾选
6. 点击 **OK**

**方法 B: 使用命令行创建**

```bash
cd /home/admin/openclaw/workspace/yms-project/
python3 -m venv venv
```

然后在 PyCharm 中选择:
1. **File** → **Settings** → **Project** → **Python Interpreter**
2. 点击齿轮图标 ⚙️ → **Add...**
3. 选择 **Existing environment**
4. 浏览到: `/home/admin/openclaw/workspace/yms-project/venv/bin/python`
5. 点击 **OK**

### 2.2 安装依赖

**方法 A: 使用 PyCharm**

1. **File** → **Settings** → **Project** → **Python Interpreter**
2. 点击 **+** 按钮
3. 搜索并安装以下包:
   - numpy
   - pandas
   - scipy
   - plotly
   - matplotlib
   - seaborn
   - sqlalchemy
   - pyyaml
   - pytest (可选，用于测试)

**方法 B: 使用 requirements.txt**

1. 打开终端 (**View** → **Tool Windows** → **Terminal**)
2. 激活虚拟环境:
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📁 步骤 3: 标记目录

### 3.1 标记 Sources Root

1. 在项目视图中，右键点击 `src/` 目录
2. 选择 **Mark Directory as** → **Sources Root**
3. 目录图标会变为蓝色 📦

### 3.2 标记 Tests Root

1. 在项目视图中，右键点击 `tests/` 目录
2. 选择 **Mark Directory as** → **Tests Root**
3. 目录图标会变为绿色 🧪

### 3.3 标记其他目录

| 目录 | 标记为 |
|------|--------|
| `data/` | Resources Root |
| `docs/` | Documentation Root |
| `config/` | Resources Root |

---

## ⚙️ 步骤 4: 配置运行/调试

### 4.1 创建运行配置

1. **Run** → **Edit Configurations...**
2. 点击 **+** → **Python**
3. 配置示例:

**配置 1: Correlation Analysis Demo**
```
Name: Correlation Analysis Demo
Script path: $ProjectFileDir$/src/yms/analysis/correlation_analysis.py
Parameters: --demo
Working directory: $ProjectFileDir$
```

**配置 2: Wafer Map Demo**
```
Name: Wafer Map Demo
Script path: $ProjectFileDir$/src/yms/visualization/wafer_map_viz.py
Parameters: --demo
Working directory: $ProjectFileDir$
```

**配置 3: SPC Control Charts Demo**
```
Name: SPC Control Charts Demo
Script path: $ProjectFileDir$/src/yms/analysis/spc_control_charts.py
Parameters: --demo
Working directory: $ProjectFileDir$
```

**配置 4: Run All Tests**
```
Name: Run All Tests
Script path: $ProjectFileDir$/tests/
Working directory: $ProjectFileDir$
```

4. 点击 **Apply** → **OK**

### 4.2 运行项目

1. 在顶部工具栏选择运行配置
2. 点击绿色运行按钮 ▶️
3. 查看 **Run** 窗口输出

---

## 🧪 步骤 5: 配置测试

### 5.1 配置 pytest

1. **File** → **Settings** → **Tools** → **Python Integrated Tools**
2. **Testing**:
   - **Default test runner**: pytest
   - **Test paths**: `$ProjectFileDir$/tests`
   - **Additional options**: `-v --cov=src/yms`

### 5.2 运行测试

**方法 A: 使用 PyCharm**

1. 右键点击 `tests/` 目录
2. 选择 **Run 'pytest in tests'**
3. 查看 **Run** 窗口输出

**方法 B: 使用终端**

```bash
source venv/bin/activate
pytest tests/ -v
```

---

## 🎨 步骤 6: 代码质量工具 (可选)

### 6.1 配置 Black (代码格式化)

1. **File** → **Settings** → **Tools** → **File Watchers**
2. 点击 **+** → 选择 `<custom>`
3. 配置:
   - **Name**: Black
   - **File type**: Python
   - **Scope**: Project Files
   - **Program**: `$PyInterpreterDirectory$/black`
   - **Arguments**: `$FilePath$`
   - **Output paths to refresh**: `$FilePath$`
4. 点击 **OK**

### 6.2 配置 Flake8 (代码检查)

1. 安装 flake8:
   ```bash
   pip install flake8
   ```
2. **File** → **Settings** → **Tools** → **External Tools**
3. 点击 **+**:
   - **Name**: Flake8
   - **Program**: `$PyInterpreterDirectory$/flake8`
   - **Arguments**: `--max-line-length=100 $FilePath$`
   - **Working directory**: `$ProjectFileDir$`
4. 点击 **OK**

---

## 📊 步骤 7: 数据库配置 (可选)

### 7.1 配置 Database 工具

1. **View** → **Tool Windows** → **Database**
2. 点击 **+** → **Data Source** → **PostgreSQL**
3. 配置连接:
   - **Host**: localhost
   - **Port**: 5432
   - **Database**: yms_db
   - **User**: postgres
   - **Password**: 你的密码
4. 点击 **Test Connection** 验证
5. 点击 **OK**

### 7.2 导入 Schema

1. 右键点击数据库 → **Run SQL Script**
2. 选择 `schema/defect_module.sql`
3. 点击执行按钮 ▶️

---

## 🔍 步骤 8: 验证配置

### 8.1 运行 Hello World 测试

创建测试文件 `tests/test_hello.py`:

```python
def test_hello():
    """Hello World 测试"""
    assert True

def test_import_yms():
    """测试 YMS 包导入"""
    from yms import CorrelationAnalysis, SPCControlCharts, WaferMapViz
    assert CorrelationAnalysis is not None
    assert SPCControlCharts is not None
    assert WaferMapViz is not None
```

运行测试:
```bash
pytest tests/test_hello.py -v
```

### 8.2 运行 Demo

1. 选择 **Correlation Analysis Demo** 配置
2. 点击运行 ▶️
3. 查看输出和生成的 HTML 文件

---

## ❓ 常见问题

### Q1: 找不到 Python 解释器

**解决**:
1. **File** → **Settings** → **Project** → **Python Interpreter**
2. 点击齿轮图标 → **Add...**
3. 选择正确的 Python 版本

### Q2: 导入错误 "No module named 'yms'"

**解决**:
1. 确保 `src/` 目录已标记为 **Sources Root**
2. 检查 Python 解释器是否正确配置
3. 重启 PyCharm

### Q3: 虚拟环境问题

**解决**:
```bash
# 删除虚拟环境
rm -rf venv/

# 重新创建
python3 -m venv venv

# 重新安装依赖
source venv/bin/activate
pip install -r requirements.txt
```

### Q4: 图表不显示

**解决**:
1. 检查 plotly 是否正确安装: `pip show plotly`
2. 确保输出路径有写入权限
3. 在浏览器中打开生成的 HTML 文件

---

## 📞 获取帮助

如遇到问题:
1. 查看 PyCharm 日志 (**Help** → **Show Log in Explorer/Finder**)
2. 检查项目配置 (**File** → **Invalidate Caches / Restart**)
3. 联系项目维护者

---

**祝使用愉快！** 🎉
