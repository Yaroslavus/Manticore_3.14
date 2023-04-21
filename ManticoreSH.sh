#!/bin/bash
python3 manticore_main.py 1> >(tee .manticore_stdout.log ) 2> >(tee .manticore_stderr.log)