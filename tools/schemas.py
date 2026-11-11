# 定义工具
TOOLS = [
    {
        "type": "function",
        "name": "read_file",
        "description": "Read the contents of a file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file"
                }
            },
            "required": ["path"],
            "additionalProperties": False
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "list_dir",
        "description": "List files and subdirectories in a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path relative to the project root. Use '.' for the root directory."
                }
            },
            "required": ["path"],
            "additionalProperties": False
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "edit_file",
        "description": (
            "Replace an exact, unique string in an existing file. "
            "Read the file before editing it."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit"
                },
                "old_string": {
                    "type": "string",
                    "description": "Exact text to replace"
                },
                "new_string": {
                    "type": "string",
                    "description": "Replacement text"
                }
            },
            "required": [
                "path",
                "old_string",
                "new_string"
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "write_file",
        "description": (
            "Create a new file and write text content to it. "
            "Do not overwrite existing files. "
            "Use edit_file to modify existing files."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the new file"
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write into new file"
                }
            },
            "required": ["path", "content"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "delete_file",
        "description": "Delete an existing file within the project directory",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to the file to delete"
                }
            },
            "required": ["path"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "search_files",
        "description": (
            "Search for keyword in project files. "
            "Return matching file paths, line numbers, and text."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword to search for in project files"
                }
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "run_tests",
        "description": (
            "Run the project's pytest test suite. "
            "Return test results and exit code."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "run_shell",
        "description": (
            "Execute a limit set of read-only commands "
            "in the project directory. "
            "Allowed commands: pwd, ls, ls -la, "
            "git status --short."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": (
                        "Command to execute, such as "
                        "'ls -la' or 'git status --short'"
                    )
                }
            },
            "required": ["command"],
            "additionalProperties": False
        },
        "strict": True 
    }
]
