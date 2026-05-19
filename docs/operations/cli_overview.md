# APMultitool CLI User Guide

This guide is designed for legal technology specialists, system administrators, and developers who need to integrate APMultitool document processing pipelines into local network directories, scheduled tasks, or document management workflows.

---

## 1. Why Use the CLI?

While the desktop GUI application offers an interactive dashboard for daily document compilation, the command-line interface (CLI) is optimized for:
- **Batch Processing**: Run scheduled overnight tasks to compile and stamp massive files.
- **Workflow Integration**: Trigger operations automatically when files are saved to intake folders.
- **Scripted Operations**: Chain conversion, merging, and Bates stamping operations together inside custom PowerShell, Cmd, or Bash scripts.
- **Local Native Execution**: Perform 100% offline processing without cloud-subscription data transmission.

---

## 2. Command Structure & Options

The core command name is `apmultitool`. Global options modify outputs and verbosity, and must be declared *before* the subcommand.

### Global Modifiers:
- `--json`: Format all console outputs (successes or errors) as structured JSON on `stdout`.
- `--silent` / `-q` / `--quiet`: Suppress diagnostic progress logs on `stderr`.
- `--verbose` / `-v`: Include debug lines and full python tracebacks on failures.
- `--version`: Print program version and exit.

---

## 3. Practical Usage Examples

### Example 1: Quiet E-Mail Conversion with JSON Callback
Converts a Outlook message file, compiles attachments, and yields structured JSON metrics on completion:
```cmd
apmultitool --json --quiet email-to-pdf --input C:\Inbox\msg_003.msg --output-dir C:\Processed --output-name converted_mail.pdf
```

### Example 2: Dry-Running a Complex Document Merge
Validate input existence, check arguments, and preview sequence layouts without writing output:
```cmd
apmultitool merge --inputs file1.pdf file2.pdf file3.docx --output-dir C:\Out --output-name final.pdf --dry-run
```

### Example 3: Grayscale Bates Numbering Stamp
Applies Bates stamp `PROD-0001000` with margin Moat Collision avoidance:
```cmd
apmultitool bates --input case_record.pdf --output-dir C:\Stamped --prefix PROD --start-number 1000 --padding 7 --position "Bottom Right" --font-name Helvetica --font-size 10
```
