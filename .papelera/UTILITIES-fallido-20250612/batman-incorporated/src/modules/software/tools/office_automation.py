"""
Automatización de Microsoft Office desde WSL2.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from .windows_interop import WindowsInterop


class OfficeAutomation:
    """
    Automatiza aplicaciones Microsoft Office desde WSL2
    usando COM objects a través de PowerShell.
    """
    
    def __init__(self, windows_interop: WindowsInterop):
        self.windows = windows_interop
        
    def create_excel_report(self, data: List[Dict], 
                          output_path: str,
                          sheet_name: str = "Report",
                          auto_format: bool = True) -> Dict:
        """
        Crea reporte Excel con datos.
        
        Args:
            data: Lista de diccionarios con datos
            output_path: Ruta de salida (.xlsx)
            sheet_name: Nombre de la hoja
            auto_format: Aplicar formato automático
            
        Returns:
            Dict con resultado
        """
        win_output = self.windows.wslpath(output_path)
        
        # Convertir datos a formato PowerShell
        if data:
            headers = list(data[0].keys())
        else:
            return {'success': False, 'error': 'No data provided'}
            
        script = f"""
        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $false
        $workbook = $excel.Workbooks.Add()
        $worksheet = $workbook.Worksheets.Item(1)
        $worksheet.Name = "{sheet_name}"
        
        # Headers
        """
        
        for i, header in enumerate(headers, 1):
            script += f'$worksheet.Cells.Item(1, {i}) = "{header}"\n'
            
        # Data rows
        for row_idx, row in enumerate(data, 2):
            for col_idx, header in enumerate(headers, 1):
                value = row.get(header, "")
                if isinstance(value, str):
                    script += f'$worksheet.Cells.Item({row_idx}, {col_idx}) = "{value}"\n'
                else:
                    script += f'$worksheet.Cells.Item({row_idx}, {col_idx}) = {value}\n'
                    
        if auto_format:
            script += """
        # Format headers
        $headerRange = $worksheet.Range("A1").EntireRow
        $headerRange.Font.Bold = $true
        $headerRange.Interior.ColorIndex = 15
        
        # Auto-fit columns
        $worksheet.UsedRange.EntireColumn.AutoFit()
        
        # Add borders
        $worksheet.UsedRange.Borders.LineStyle = 1
        """
        
        script += f"""
        # Save and close
        $workbook.SaveAs("{win_output}")
        $excel.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
        
        if (Test-Path "{win_output}") {{
            Write-Host "SUCCESS: Created {win_output}"
        }}
        """
        
        result = self.windows.run_powershell(script, timeout=60)
        
        if result['success'] and Path(output_path).exists():
            result['file_path'] = output_path
            
        return result
    
    def generate_word_document(self, content: Dict[str, Any],
                             output_path: str,
                             template_path: Optional[str] = None) -> Dict:
        """
        Genera documento Word.
        
        Args:
            content: Contenido del documento
            output_path: Ruta de salida (.docx)
            template_path: Plantilla opcional
            
        Returns:
            Dict con resultado
        """
        win_output = self.windows.wslpath(output_path)
        
        script = """
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        """
        
        if template_path:
            win_template = self.windows.wslpath(template_path)
            script += f'$doc = $word.Documents.Add("{win_template}")\n'
        else:
            script += '$doc = $word.Documents.Add()\n'
            
        # Agregar contenido
        if 'title' in content:
            script += f"""
        $word.Selection.Font.Size = 24
        $word.Selection.Font.Bold = $true
        $word.Selection.TypeText("{content['title']}")
        $word.Selection.TypeParagraph()
        $word.Selection.TypeParagraph()
        """
        
        if 'paragraphs' in content:
            for para in content['paragraphs']:
                script += f"""
        $word.Selection.Font.Size = 11
        $word.Selection.Font.Bold = $false
        $word.Selection.TypeText("{para}")
        $word.Selection.TypeParagraph()
        """
        
        script += f"""
        # Save and close
        $doc.SaveAs("{win_output}")
        $word.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
        
        Write-Host "SUCCESS: Created {win_output}"
        """
        
        return self.windows.run_powershell(script, timeout=60)
    
    def create_powerpoint_presentation(self, slides: List[Dict],
                                     output_path: str,
                                     template: str = "blank") -> Dict:
        """
        Crea presentación PowerPoint.
        
        Args:
            slides: Lista de slides con título y contenido
            output_path: Ruta de salida (.pptx)
            template: Plantilla a usar
            
        Returns:
            Dict con resultado
        """
        win_output = self.windows.wslpath(output_path)
        
        script = """
        $ppt = New-Object -ComObject PowerPoint.Application
        $presentation = $ppt.Presentations.Add()
        """
        
        for i, slide in enumerate(slides):
            script += f"""
        # Slide {i+1}
        $slide = $presentation.Slides.Add({i+1}, 2)  # ppLayoutText
        $slide.Shapes[1].TextFrame.TextRange.Text = "{slide.get('title', f'Slide {i+1}')}"
        $slide.Shapes[2].TextFrame.TextRange.Text = "{slide.get('content', '')}"
        """
        
        script += f"""
        # Save and close
        $presentation.SaveAs("{win_output}")
        $ppt.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
        
        Write-Host "SUCCESS: Created {win_output}"
        """
        
        return self.windows.run_powershell(script, timeout=60)
    
    def send_outlook_email(self, to: str,
                         subject: str,
                         body: str,
                         attachments: List[str] = None,
                         cc: Optional[str] = None) -> Dict:
        """
        Envía email usando Outlook.
        
        Args:
            to: Destinatario(s)
            subject: Asunto
            body: Cuerpo del mensaje
            attachments: Lista de archivos adjuntos
            cc: CC opcional
            
        Returns:
            Dict con resultado
        """
        script = f"""
        $outlook = New-Object -ComObject Outlook.Application
        $mail = $outlook.CreateItem(0)
        
        $mail.To = "{to}"
        $mail.Subject = "{subject}"
        $mail.Body = "{body}"
        """
        
        if cc:
            script += f'$mail.CC = "{cc}"\n'
            
        if attachments:
            for attachment in attachments:
                win_path = self.windows.wslpath(attachment)
                script += f'$mail.Attachments.Add("{win_path}")\n'
                
        script += """
        $mail.Send()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
        
        Write-Host "SUCCESS: Email sent"
        """
        
        return self.windows.run_powershell(script)