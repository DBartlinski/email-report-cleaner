Attribute VB_Name = "ExportMailToCsv"
' Exports the currently-selected Outlook folder's mail items to a CSV with a
' real ReceivedTime column, so scripts/process_emails.py can sort accurately.
' Setup/run steps are in the chat instructions delivered alongside this file.
Option Explicit

Sub ExportSelectedFolderToCsv()
    Dim olApp As Outlook.Application
    Dim olFolder As Outlook.MAPIFolder
    Dim olExplorer As Outlook.Explorer
    Dim olItems As Outlook.Items
    Dim olItem As Object
    Dim filePath As Variant
    Dim fileNum As Integer
    Dim line As String

    Set olApp = Application
    Set olExplorer = olApp.ActiveExplorer
    Set olFolder = olExplorer.CurrentFolder

    filePath = Application.GetSaveAsFilename("mail_export.csv", "CSV Files (*.csv), *.csv")
    If filePath = False Then Exit Sub

    fileNum = FreeFile
    Open filePath For Output As #fileNum
    Print #fileNum, "ReceivedTime,Subject,SenderName,SenderEmailAddress,ToNames,CcNames,Body"

    Set olItems = olFolder.Items
    Dim i As Long
    For i = 1 To olItems.Count
        If TypeOf olItems(i) Is Outlook.MailItem Then
            Set olItem = olItems(i)
            line = Quote(Format(olItem.ReceivedTime, "yyyy-mm-dd hh:nn:ss")) & "," & _
                   Quote(olItem.Subject) & "," & _
                   Quote(olItem.SenderName) & "," & _
                   Quote(GetSenderEmail(olItem)) & "," & _
                   Quote(olItem.To) & "," & _
                   Quote(olItem.CC) & "," & _
                   Quote(olItem.Body)
            Print #fileNum, line
        End If
    Next i

    Close #fileNum
    MsgBox "Export complete: " & filePath
End Sub

Private Function GetSenderEmail(olItem As Outlook.MailItem) As String
    On Error Resume Next
    GetSenderEmail = olItem.SenderEmailAddress
    On Error GoTo 0
End Function

' Wraps a field in double quotes and escapes embedded quotes per CSV rules.
Private Function Quote(ByVal text As String) As String
    Quote = """" & Replace(text, """", """""") & """"
End Function
