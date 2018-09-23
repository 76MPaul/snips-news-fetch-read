# Copyright (C) <2018>  <MAGNIER Paul>

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import sys

from os import mkdir, path
from os.path import join
from sys import platform as _platform


#####################
#    DIRECTORIES    #
#####################
CLIENT_DIR =    path.dirname(path.abspath(__file__))
BASE_DIR =      path.dirname(CLIENT_DIR)
DATA_DIR =      path.join(CLIENT_DIR, 'data')
LOGS_DIR =      path.join(DATA_DIR,   'logs')
GOOGLE_CREDENTIAL_DIR =      path.join(CLIENT_DIR, 'Google credentials')

DIRS = [DATA_DIR, LOGS_DIR] #, DATABASE_DIR, VOICE_DIR

for d in DIRS:
    if not path.exists(d):
        mkdir(d)
  
#####################
#        NEWS       #
#####################
  
NEWS = ['getNews',]

NEWS_API = ''
