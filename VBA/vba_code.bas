Sub DeleteBCColumnsInRows()
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long

    ' Aktif çalisma sayfasini seç
    Set ws = ThisWorkbook.Sheets("cleaned_u-free_v1,columns") ' "Sheet1" yerine kendi sayfanizin adini yazin

    ' Son satirin bulunmasi
    lastRow = ws.Cells(ws.Rows.Count, "J").End(xlUp).Row

    ' J sütununda deger olan her satiri kontrol et
    For i = 1 To lastRow
        ' Eger J sütununda bir deger varsa
        If ws.Cells(i, "J").Value <> "" Then
            ' B ve C sütunlarindaki degerleri sil
            ws.Cells(i, "B").Resize(1, 2).Delete Shift:=xlToLeft
        End If
    Next i
End Sub

