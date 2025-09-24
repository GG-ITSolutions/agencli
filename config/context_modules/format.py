#!/usr/bin/env python3
"""
Format Context Module - Provides Rich formatting information for LLMs
"""

def get_formatting_guide():
    """Generate comprehensive Rich formatting guide for LLMs."""
    return """
# Rich Text Formatting Module for Terminal Output

## Colors
Use color names or hex codes:
- [red]Red text[/red]
- [blue]Blue text[/blue]
- [green]Green text[/green]
- [yellow]Yellow text[/yellow]
- [magenta]Magenta text[/magenta]
- [cyan]Cyan text[/cyan]
- [#FF0000]Custom red[/] (hex colors)

## Background Colors
- [on red]White on red[/on red]
- [on blue]White on blue[/on blue]
- [black on white]Black on white[/black on white]

## Combined Styles
- [bold red]Bold red text[/bold red]
- [italic blue on yellow]Italic blue on yellow[/italic blue on yellow]
- [bold underline green]Bold underlined green[/bold underline green]

## Lists
### Unordered Lists:
• Item 1
• Item 2
• Item 3

### Ordered Lists:
1. First item
2. Second item
3. Third item

### Checkboxes:
✓ Completed task
✗ Incomplete task
○ In progress

## Progress and Status
• 🔄 Processing...
• ✅ Completed successfully
• ❌ Error occurred
• ⚠️ Warning message
• ℹ️ Information

## Emojis and Symbols
• ✅ Success / Check
• ❌ Error / Cross
• ⚠️ Warning / Caution
• ℹ️ Information / Info
• 🔄 Loading / In progress
• 🎯 Target / Goal
• 📝 Note / Document
• 🔧 Tool / Settings
• 📊 Chart / Statistics
• 🎨 Art / Design

## Layout Tips
1. Use line breaks for better readability
2. Group related information together
3. Use consistent formatting throughout
4. Keep important information prominent
5. Use colors sparingly but effectively
6. Consider terminal width (usually 80-120 characters)

## Examples

### Success Message
✅ [green]Operation completed successfully![/green]

### Error Message
❌ [red]Error: File not found[/red]
   Please check the file path and try again.

### Command Formatting
Running command [on gray]ls -la[/on gray] in the current directory.

VERY IMPORTANT: Use Rich formatting in your responses. Do NOT use Markdown formatting.
Never use markdown symbols like **bold** or `code` or ## header2 in your responses INSTEAD USE RICH FORMATTING!
"""

if __name__ == "__main__":
    print(get_formatting_guide())
