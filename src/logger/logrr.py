"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Trevor Maco <tmaco@cisco.com>, Mark Orszycki <morszyck@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import json
import logging
import logging.handlers
import os
import pathlib
import queue
import re
from threading import Lock
from typing import ClassVar

from rich import inspect
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table

from .custom_themes import ct


def extract_readme_sections(readme_path: str = "README.md"):
    """
    Extract relevant sections from the README file.
    """
    readme_path = readme_path
    with open(readme_path, 'r') as file:
        readme_content = file.read()

    patterns = {
        'accessing_app': r'### Accessing the Application\s+(.*?)(?=###|\!\[|$)',
        'running_report': r'### Running the Webex Calling Detailed Report\s+(.*?)(?=###|\!\[|$)',
        'what_to_expect': r'#### What to Expect:\s+(.*?)(?=####|\!\[|$)',
        'please_note': r'#### Please Note:\s+(.*?)(?=####|\!\[|$)'
    }

    extracted_sections = {}
    for section, pattern in patterns.items():
        match = re.search(pattern, readme_content, re.DOTALL)
        if match:
            extracted_sections[section] = match.group(1).strip()

    if extracted_sections:
        combined_sections = '\n\n'.join(extracted_sections.values())
        additional_info_pattern = r'## Additional Info.*'
        combined_sections = re.sub(additional_info_pattern, '', combined_sections, flags=re.DOTALL).strip()
        # Remove any blank lines
        combined_sections = '\n'.join(line for line in combined_sections.split('\n') if line.strip())
        return combined_sections
    return "Relevant sections not found."


def get_config_table(config_instance):
    """
    Create a rich table format of the configuration data and return it as a renderable object.

    Args:
        config_instance: The configuration instance containing the settings.

    Returns:
        Table: A rich table object.
    """
    table = Table()
    table.add_column("Variable", justify="left", style="bright_white")
    table.add_column("Value", style="bright_white")

    for name in config_instance.model_fields.keys():
        value = getattr(config_instance, name)
        # Skip rows with empty name and value
        if name or value:
            table.add_row(name, str(value) if value not in [None, ""] else "Not Set")
    return table


def _add_rows_to_table(table, data_list, headers):
    """Helper method to add rows to a table."""
    for item in data_list:
        row = [str(item.get(header, '')) for header in headers]
        table.add_row(*row)


def flatten_json(y):
    """Recursively flatten nested dictionaries."""
    out = {}

    def flatten(x, prefix=''):
        if isinstance(x, dict):
            for key in x:
                flatten(x[key], prefix + key + '.')
        else:
            out[prefix[:-1]] = x

    flatten(y)
    return out


class LoggerManager:
    """
    Singleton class for managing logging and console output.
    """
    _instance = None
    _lock = Lock()

    LOG_PATH: ClassVar[str] = str(pathlib.Path(__file__).parents[1] / 'logger' / 'logs')

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LoggerManager, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        self.listener = None
        self.console = Console(theme=ct)  # Uses ThemManager Class
        self.log_queue = queue.Queue(-1)  # No limit on size
        self.queue_handler = logging.handlers.QueueHandler(self.log_queue)
        self.log_dir = self.LOG_PATH
        self.logger = self.setup()
        self.original_log_level = self.logger.level
        self.session_logs = {}  # This will store all the logs per session
        self.logger.propagate = False
        self.lock = Lock()

    def tsp(self, *args, style="default", **kwargs):
        """Thread safe print."""
        with self.lock:
            self.console.print(*args, style=style, **kwargs)

    def pp(self, *args, style="default", **kwargs):
        """ Pretty printing json with thread safe print. """
        pretty = Pretty(locals())
        self.tsp(*args, **kwargs)  # Spread the args

    def lnp(self, message, level="info"):
        """ Log n' print the message
        Log the message at the given level and print it to the console."""
        level_method = getattr(self.logger, level.lower(), self.logger.info)
        level_method(message)

    def p_panel(self, *args, **kwargs):
        """Create and print a Rich Panel in a thread-safe manner."""
        panel = Panel.fit(*args, **kwargs)
        self.tsp(panel)

    def setup(self):
        """Set up the logger with handlers for both console and file output."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        log_directory = self.log_dir
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        file_handler = logging.handlers.TimedRotatingFileHandler(f"{self.log_dir}/app.log", when="midnight", interval=1,
                                                                 backupCount=7)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format))

        console_handler = RichHandler(console=self.console)
        console_handler.setLevel(logging.DEBUG)

        self.listener = logging.handlers.QueueListener(
            self.log_queue, console_handler, file_handler, respect_handler_level=True
        )
        self.listener.start()

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.queue_handler)

        return logger

    def shutdown(self):
        """Stop the logging listener."""
        self.listener.stop()

    def print_list_as_rich_table(self, data_list: list, title: str, headers=None):
        """Display a list of dictionaries in a rich table format."""
        if not data_list or not all(isinstance(item, dict) for item in data_list):
            self.tsp("Invalid data provided for the table.")
            return

        headers = headers or data_list[0].keys()
        table = Table(title=title)
        for header in headers:
            table.add_column(header, style="bright_white")

        _add_rows_to_table(table, data_list, headers)
        self.tsp(table)

    def print_json_as_rich_table(self, json_data, title="JSON Data"):
        """
        Display JSON data in a rich table format.

        Args:
            json_data (str/dict/list): JSON data to be displayed in the table.
            title (str): Title of the table.
        """
        # Parse JSON if it's a string
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                self.tsp(f"Invalid JSON string: {e}")
                return

        # Handle case where data is already a dictionary or list
        else:
            data = json_data

        # Create a new table
        table = Table(title=title)

        # Check if the data is a list of dictionaries
        if isinstance(data, list) and all(isinstance(elem, dict) for elem in data):
            # Add headers based on the keys of the first dictionary
            headers = data[0].keys()
            for header in headers:
                table.add_column(header, style="bright_white")

            # Add rows
            for item in data:
                table.add_row(*[str(item.get(h, '')) for h in headers])

        elif isinstance(data, dict):
            # If the data is a single dictionary, display key-value pairs
            table.add_column("Key", style="bright_yellow")
            table.add_column("Value", style="bright_white")
            for key, value in data.items():
                table.add_row(str(key), json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value))

        else:
            self.tsp("Unsupported JSON format")
            return

        # Print the table
        self.tsp(table)

    def print_2_column_rich_table(self, data, title: str = "Table Name"):
        """
        Display data in a rich table format.
        """
        table = Table(title=title)
        table.add_column("Variable", justify="left", style="bright_white", width=30)
        table.add_column("Value", style="bright_white", width=60)

        for var_name, var_value in data:
            table.add_row(var_name, str(var_value) if var_value not in [None, ""] else "Not Set")
        self.tsp(table)

    def print_config_table(self, config_instance: object):
        """
        Print the configuration data in a rich table format
        """
        config_data = [(name, value) for name, value in config_instance.env_vars.items()]
        self.print_2_column_rich_table(data=config_data, title="Environment Variables")

    def print_start_panel(self, app_name: str = "App"):
        """
        Print a start panel with the app name at startup
        """
        self.p_panel(renderable=f'[bold bright_white]{app_name}[/bold bright_white]', title='Start',
                     border_style='maverick')

    def print_exit_panel(self):
        """
        Print an exit panel on shutdown
        """
        self.p_panel(renderable='Shutting down...', title='[bright_red]Exit[/bright_red]', border_style='red')

    def debug_inspect(self, obj):
        """
        Inspect an object using Rich and log the representation.
        """
        inspect(obj, console=self.console, methods=True)
        self.tsp(f"Inspected object: {type(obj).__name__}", style="debug", level="debug")


lm = LoggerManager()
