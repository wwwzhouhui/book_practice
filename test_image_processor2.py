# 测试颜色分析模块
import cv2
from modules.image_processing.color_analysis import ColorAnalyzer

def main():
    image_path = "resources/2.png"
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"无法读取图像: {image_path}")
        return
    
    analyzer = ColorAnalyzer()
    handwritten_areas = analyzer.detect_handwritten_areas(image)
    
    print(f"检测到 {len(handwritten_areas)} 个手写区域:")
    for area in handwritten_areas:
        print(f"颜色: {area['color']}, 位置: {area['bbox']}")

if __name__ == "__main__":
    main()