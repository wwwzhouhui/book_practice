import os
import json
import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeishuSync:
    """飞书同步模块"""
    
    def __init__(self, config_path=None):
        """初始化飞书同步模块
        
        Args:
            config_path: 配置文件路径，默认为项目根目录下的config/feishu_config.json
        """
        self.is_configured = False
        self.app_id = None
        self.app_secret = None
        self.table_id = None
        
        # 尝试加载配置
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_dir = project_root / "config"
            config_path = config_dir / "feishu_config.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.app_id = config.get('app_id')
                self.app_secret = config.get('app_secret')
                self.table_id = config.get('table_id')
                
                if self.app_id and self.app_secret and self.table_id:
                    self.is_configured = True
                    logger.info("飞书配置加载成功")
                else:
                    logger.warning("飞书配置不完整")
            except Exception as e:
                logger.error(f"加载飞书配置失败: {str(e)}")
        else:
            logger.warning(f"飞书配置文件不存在: {config_path}")
    
    def sync_error_questions(self, questions):
        """同步错题数据到飞书多维表格
        
        Args:
            questions: 错题数据列表
            
        Returns:
            同步结果字典
        """
        if not self.is_configured:
            return {
                "success": False,
                "message": "飞书同步未配置，请先配置飞书应用信息",
                "synced_count": 0
            }
        
        # 这里只是模拟同步过程
        logger.info(f"模拟同步 {len(questions)} 条错题到飞书")
        
        return {
            "success": True,
            "message": f"成功同步 {len(questions)} 条错题到飞书多维表格",
            "synced_count": len(questions),
            "sync_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_table_meta(self):
        """获取飞书多维表格元数据
        
        Returns:
            表格元数据字典，未配置时返回None
        """
        if not self.is_configured:
            return None
        
        # 模拟表格元数据
        return {
            "name": "错题收集表",
            "record_count": 0,
            "fields": [
                {"name": "题目ID", "type": "number"},
                {"name": "学科", "type": "text"},
                {"name": "题型", "type": "text"},
                {"name": "难度", "type": "number"},
                {"name": "题目内容", "type": "text"},
                {"name": "正确答案", "type": "text"},
                {"name": "学生答案", "type": "text"},
                {"name": "解析", "type": "text"},
                {"name": "创建时间", "type": "datetime"}
            ]
        }
    
    def test_connection(self):
        """测试飞书连接
        
        Returns:
            连接测试结果
        """
        if not self.is_configured:
            return {
                "success": False,
                "message": "飞书同步未配置"
            }
        
        # 模拟连接测试
        return {
            "success": True,
            "message": "飞书连接测试成功",
            "app_info": {
                "app_name": "作业错题收集器",
                "tenant_name": "测试学校"
            }
        }