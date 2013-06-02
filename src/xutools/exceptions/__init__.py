"""
copyright (c) 2013, Gabriel A. Weaver <gabriel.a.l.weaver@gmail.com>

This file is part of XUTools, Python Distribution

This code is free software:  you can redistribute
it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundations, either version
3 of the License, or (at your option) any later version.

XUTools is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.
                                                                                
You should have received a copy of the GNU General Public License               
along with this program.  If not, see http://www.gnu.org/licenses/
"""

## @package xutools.exception
# If XUTools encounters a language name that it does not recognize,
#  then it will throw this exception.
class UndefinedLanguageName(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

