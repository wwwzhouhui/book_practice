# 错题导出模块
本模块提供了多种格式的错题导出功能，支持PDF、CSV和Word格式，用于将错题集导出为不同格式的文件。

## 模块结构
- __init__.py : 模块初始化文件，导出必要的类供外部使用
- base_exporter.py : 导出器基类，定义了导出接口和通用方法
- pdf_exporter.py : PDF导出器，支持中文和数学公式的渲染
- csv_exporter.py : CSV导出器，支持导出题目和答案到表格文件
- word_exporter.py : Word导出器，支持格式化的题目和答案
- export_manager.py : 导出管理器，统一管理各种格式的导出
## 依赖包
要使用本模块，需要安装以下依赖包：

```bash
pip install reportlab python-docx pandas
 ```

- reportlab : 用于PDF文件生成，支持中文和数学公式
- python-docx : 用于Word文档生成
- pandas : CSV导出和数据处理
## 字体配置
### PDF导出字体配置
PDF导出器需要中文字体和数学字体支持，系统会自动尝试查找以下字体：

1. 中文字体 （按优先级）:
   
   - SimSun (宋体)
   - SimHei (黑体)
   - Microsoft YaHei (微软雅黑)
2. 数学字体 （按优先级）:
   
   - STIXTwoMath
   - Cambria Math
   - Arial Unicode MS
### 字体安装方法
1. Windows系统 ：
   
   - 系统通常已预装中文字体，位于 C:/Windows/Fonts/ 目录
   - 如果缺少字体，可下载后双击安装，或复制到 C:/Windows/Fonts/ 目录
2. 自定义字体目录 ：
   
   - 在项目根目录创建 fonts 文件夹
   - 将字体文件放入该文件夹，系统会自动查找
```plaintext
book_practice/
├── fonts/
│   ├── simhei.ttf
│   ├── simsun.ttc
│   └── STIXTwoMath-Regular.ttf
 ```

3. STIX数学字体下载 ：
   - 官方网站： https://www.stixfonts.org/
   - 下载后放入 fonts 目录或系统字体目录
## 使用方法
### 通过导出管理器使用（推荐）
导出管理器提供了统一的接口，是最简单的使用方式：

```python
from modules.export.export_manager import ExportManager
from modules.storage.database import Database

# 初始化数据库和导出管理器
db = Database()
export_mgr = ExportManager(db)

# 获取题目数据
questions = db.get_all_error_questions()

# 导出题目（不含答案）
output_path, status_message = export_mgr.export_questions(
    questions, 
    export_format="PDF",  # 可选 "PDF", "CSV", "Word"
    include_answers=False
)

# 导出题目（含答案）
output_path, status_message = export_mgr.export_questions(
    questions, 
    export_format="PDF",
    include_answers=True
)
 ```
```

### 直接使用各导出器
如果需要更精细的控制，可以直接使用各个导出器：

```python
from modules.export.pdf_exporter import PDFExporter
from modules.export.csv_exporter import CSVExporter
from modules.export.word_exporter import WordExporter

# 初始化导出器
pdf_exporter = PDFExporter()
csv_exporter = CSVExporter()
word_exporter = WordExporter()

# 导出题目
output_path = pdf_exporter.export_questions(
    questions,
    output_path=None,  # 如果为None，则使用默认路径
    include_answers=True
)
 ```
```

## 各导出器功能说明
### 1. PDF导出器 (PDFExporter)
PDF导出器使用ReportLab库生成PDF文件，支持中文和数学公式渲染。

主要功能 ：

- 自动查找并注册中文字体和数学字体
- 支持数学符号和公式的渲染
- 提供不同样式的标题、正文和答案格式
- 支持导出题目和答案（可选）
- 支持导出题目解析（当include_answers=True时）
特殊处理 ：

- 自动识别并处理数学符号
- 支持上标、下标等特殊格式
- 提供安全模式，在标准渲染失败时使用备选方案
### 2. CSV导出器 (CSVExporter)
CSV导出器生成表格格式的错题集，便于在Excel等软件中查看和编辑。

主要功能 ：

- 导出题目基本信息（ID、学科、题型、难度等）
- 支持导出题目内容
- 可选导出答案和解析
- 使用UTF-8编码，支持中文
### 3. Word导出器 (WordExporter)
Word导出器生成格式化的Word文档，支持丰富的格式和样式。

主要功能 ：

- 创建格式化的Word文档
- 支持彩色标题和分节
- 支持导出题目和答案（可选）
- 支持导出题目解析（当include_answers=True时）
依赖说明 ：

- 需要安装python-docx库
## 导出管理器 (ExportManager)
导出管理器统一管理各种格式的导出，提供简单的接口。

主要功能 ：

- 统一管理PDF、CSV、Word等多种导出格式
- 自动创建导出目录
- 生成带时间戳的文件名
- 提供统一的错误处理和状态消息
## 实际应用示例
以下是在错题查询页面中使用导出功能的示例：

```python
# 在UI页面中使用导出功能
def export_selected_questions(questions, export_format, include_answers):
    try:
        # 初始化导出管理器
        export_mgr = ExportManager(db)
        
        # 执行导出
        output_path, status_message = export_mgr.export_questions(
            questions,
            export_format=export_format,
            include_answers=include_answers
        )
        
        # 返回结果
        if output_path:
            return output_path, status_message
        else:
            return None, f"导出失败: {status_message}"
            
    except Exception as e:
        return None, f"导出过程中出错: {str(e)}"
 ```
```

## 故障排除
1. 字体问题 ：
   
   - 如果PDF中文字显示为方块，请确保系统安装了中文字体
   - 可以手动将字体文件放入项目的fonts目录
2. 数学公式渲染问题 ：
   
   - 如果数学公式显示不正确，请安装STIX字体
   - 复杂公式可能需要使用安全模式渲染
3. 依赖包安装问题 ：
   
   - Word导出需要python-docx库
   - PDF导出需要reportlab库
   - 如果导出失败，请检查相关库是否正确安装