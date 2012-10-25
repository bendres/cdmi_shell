cdmi_shell
==========

This utility provides a *nix like shell interface for CDMI.

Requirements:
=============
python >= 2.6
urllib3
requests >= 0.13.3

Configuration:
==============
Default behavoir is to load ~/.cdmirc if it exists. See cdmirc.example for
the proper syntax. If a config file is not supplied then you will be prompted
for URL, username and password. Run 'python cdmi_shell.py -h' for syntax.

Known Issues:
=============
1. ls does not support dot notation
2. ENTER by itself recalls the last command and executes it
3. cd will exit when using "cd .." within cdmi_domain_summaries

