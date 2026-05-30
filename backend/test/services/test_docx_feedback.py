"""
Feedback loop for DOCX export bug.
Tests the exact code path used by the worker.
"""
import sys
import os
import tempfile
sys.path.insert(0, '.')

from services.export import ExportService
from docx import Document

def test_docx_export():
    """Test DOCX export with Chinese text."""
    
    # Sample markdown similar to what the worker generates
    test_md = """# 2024Q4市场分析报告

## 摘要

本报告聚焦2024年第四季度全球市场的尾部风险、政策突变与行业震荡。

核心发现如下：
- 第一，全球流动性转向并非"蜜月期"
- 第二，美国大选构成年内最大地缘政治黑天鹅

## 第一章 流动性转向

这是普通段落内容，用于测试正文字体。

### 1.1 子标题

更多详细内容在这里。
"""
    
    # Export to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
        output_path = f.name
    
    try:
        print(f"Exporting to: {output_path}")
        result = ExportService.export_docx(test_md, output_path)
        
        if not result:
            print("FAIL: export_docx returned None")
            return False
        
        # Open and verify
        doc = Document(output_path)
        
        print("\n=== Paragraph Analysis ===")
        all_good = True
        
        for i, p in enumerate(doc.paragraphs):
            style_name = p.style.name
            text = p.text
            
            # Check runs
            for j, r in enumerate(p.runs):
                run_text = r.text
                font_name = r.font.name
                font_size = r.font.size
                
                # Check if font is set
                if not font_name:
                    print(f"  WARN: Para {i} Run {j} [{style_name}] has no font.name")
                    all_good = False
                
                # Check if size is set
                if not font_size:
                    print(f"  WARN: Para {i} Run {j} [{style_name}] has no font.size")
                    all_good = False
                
                # Check eastAsia font
                from docx.oxml.ns import qn
                ea_font = None
                if r._element.rPr is not None:
                    rFonts = r._element.rPr.find(qn('w:rFonts'))
                    if rFonts is not None:
                        ea_font = rFonts.get(qn('w:eastAsia'))
                
                if not ea_font:
                    print(f"  WARN: Para {i} Run {j} [{style_name}] has no eastAsia font")
                    all_good = False
                
                # Print first few paragraphs
                if i < 5:
                    size_pt = round(font_size / 12700, 1) if font_size else "NONE"
                    print(f"  [{style_name:15s}] font={font_name:20s} ea={ea_font:20s} size={size_pt:>6}pt  text={run_text[:30]}")
        
        if all_good:
            print("\nPASS: All runs have font, size, and eastAsia set")
            return True
        else:
            print("\nFAIL: Some runs missing font settings")
            return False
            
    finally:
        # Cleanup
        if os.path.exists(output_path):
            os.unlink(output_path)

if __name__ == '__main__':
    success = test_docx_export()
    sys.exit(0 if success else 1)
