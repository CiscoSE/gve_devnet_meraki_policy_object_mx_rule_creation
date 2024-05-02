# Custom themes for the rich console
from rich.theme import Theme

ct = Theme(
    {
        'default': 'bright_white',
        'info': 'bright_white',
        'error': 'bold italic red',
        'debug': 'orange1',
        'warning': 'bright_yellow',
        'webhook': 'orange1',
        'env': 'aquamarine1',
        'success': 'bright_green',
        'meraki': 'bright_green',
        'webex': 'blue',
        'maverick': 'dark_orange',
    }
)
